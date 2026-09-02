import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math

# Set Page Config
st.set_page_config(
    page_title="Engineering Toolbox v12.2 PRO",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1F497D;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        font-style: italic;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #F8F9FA;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #2F5496;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2F5496;
    }
    .metric-cost {
        font-size: 2.2rem;
        font-weight: bold;
        color: #27AE60;
    }
    .metric-waste {
        font-size: 1.8rem;
        font-weight: bold;
        color: #C0392B;
    }
</style>
""", unsafe_allow_html=True)

# --- REFERENCE DATABASES (CACHED) ---

@st.cache_data
def get_materials_db():
    return {
        "Stal węglowa (Mild Steel)": {"group": "Metale (Żelazne)", "density_g": 7.85, "density_kg": 7850, "price_kg": 6.50, "young_gpa": 210, "desc": "Stal konstrukcyjna, śruby, rury, profile"},
        "Stal nierdzewna 304": {"group": "Metale (Żelazne)", "density_g": 7.93, "density_kg": 7930, "price_kg": 18.50, "young_gpa": 193, "desc": "Odporna na korozję, przemysł spożywczy"},
        "Stal nierdzewna 316": {"group": "Metale (Żelazne)", "density_g": 8.00, "density_kg": 8000, "price_kg": 24.00, "young_gpa": 200, "desc": "Środowisko morskie, odporność chemiczna"},
        "Żeliwo szare (Grey Iron)": {"group": "Metale (Żelazne)", "density_g": 7.15, "density_kg": 7150, "price_kg": 8.00, "young_gpa": 110, "desc": "Korpusy maszyn, tarcze hamulcowe"},
        "Żeliwo sferoidalne (Ductile)": {"group": "Metale (Żelazne)", "density_g": 6.92, "density_kg": 6920, "price_kg": 9.50, "young_gpa": 170, "desc": "Elementy maszyn o wysokiej wytrzymałości"},
        "Stal narzędziowa (Tool Steel)": {"group": "Metale (Żelazne)", "density_g": 7.81, "density_kg": 7810, "price_kg": 15.00, "young_gpa": 210, "desc": "Narzędzia skrawające, formy, matryce"},
        "Aluminium 6061-T6": {"group": "Metale (Nieżelazne)", "density_g": 2.70, "density_kg": 2700, "price_kg": 16.00, "young_gpa": 70, "desc": "Konstrukcje lekkie, lotnictwo, jachty"},
        "Aluminium 7075-T6": {"group": "Metale (Nieżelazne)", "density_g": 2.81, "density_kg": 2810, "price_kg": 22.00, "young_gpa": 72, "desc": "Elementy o bardzo wysokiej wytrzymałości"},
        "Miedź czysta (Copper/ETP)": {"group": "Metale (Nieżelazne)", "density_g": 8.96, "density_kg": 8960, "price_kg": 38.00, "young_gpa": 110, "desc": "Elektrotechnika, przewody, wymienniki ciepła"},
        "Mosiądz (Brass C360)": {"group": "Metale (Nieżelazne)", "density_g": 8.50, "density_kg": 8500, "price_kg": 28.00, "young_gpa": 100, "desc": "Tuleje, złączki, elementy toczone"},
        "Brąz fosforowy (Bronze)": {"group": "Metale (Nieżelazne)", "density_g": 8.80, "density_kg": 8800, "price_kg": 32.00, "young_gpa": 115, "desc": "Łożyska ślizgowe, sprężyny, przekładnie"},
        "Tytan Grade 5 (Ti6Al4V)": {"group": "Metale (Nieżelazne)", "density_g": 4.43, "density_kg": 4430, "price_kg": 140.00, "young_gpa": 114, "desc": "Zastosowania medyczne, kosmonautyka, motorsport"},
        "POM-C (Delrin/Acetal)": {"group": "Tworzywa sztuczne", "density_g": 1.41, "density_kg": 1410, "price_kg": 19.00, "young_gpa": 3, "desc": "Koła zębate, ślizgi, precyzyjne detale"},
        "PA6 (Nylon 6)": {"group": "Tworzywa sztuczne", "density_g": 1.14, "density_kg": 1140, "price_kg": 14.50, "young_gpa": 2.5, "desc": "Tuleje ślizgowe, rolki, uszczelnienia"},
        "PTFE (Teflon)": {"group": "Tworzywa sztuczne", "density_g": 2.20, "density_kg": 2200, "price_kg": 45.00, "young_gpa": 0.5, "desc": "Uszczelnienia chemiczne, ślizgi niskotarciowe"},
        "Polycarbonate (PC)": {"group": "Tworzywa sztuczne", "density_g": 1.20, "density_kg": 1200, "price_kg": 25.00, "young_gpa": 2.4, "desc": "Osłony przezroczyste, bezpieczne szyby"},
        "Polyethylene (HDPE)": {"group": "Tworzywa sztuczne", "density_g": 0.96, "density_kg": 960, "price_kg": 12.00, "young_gpa": 0.8, "desc": "Rurociągi, zbiorniki chemiczne, płyty ślizgowe"},
        "Polypropylene (PP)": {"group": "Tworzywa sztuczne", "density_g": 0.90, "density_kg": 900, "price_kg": 10.50, "young_gpa": 1.3, "desc": "Niska masa, wysoka odporność chemiczna"}
    }

@st.cache_data
def get_fasteners_db():
    return {
        "M3": {"nut_s": 5.5, "nut_m": 2.4, "nut_weight": 0.384, "nut_price": 19.61, "washer_d1": 3.2, "washer_d2": 7.0, "washer_h": 0.5, "washer_weight": 0.119, "washer_price": 9.79},
        "M4": {"nut_s": 7.0, "nut_m": 3.2, "nut_weight": 0.810, "nut_price": 24.72, "washer_d1": 4.3, "washer_d2": 9.0, "washer_h": 0.8, "washer_weight": 0.308, "washer_price": 12.62},
        "M5": {"nut_s": 8.0, "nut_m": 4.0, "nut_weight": 1.230, "nut_price": 29.76, "washer_d1": 5.3, "washer_d2": 10.0, "washer_h": 1.0, "washer_weight": 0.443, "washer_price": 14.64},
        "M6": {"nut_s": 10.0, "nut_m": 5.0, "nut_weight": 2.500, "nut_price": 45.00, "washer_d1": 6.4, "washer_d2": 12.5, "washer_h": 1.6, "washer_weight": 1.020, "washer_price": 23.30},
        "M8": {"nut_s": 13.0, "nut_m": 6.5, "nut_weight": 5.200, "nut_price": 77.40, "washer_d1": 8.4, "washer_d2": 16.0, "washer_h": 1.6, "washer_weight": 1.830, "washer_price": 35.45},
        "M10": {"nut_s": 17.0, "nut_m": 8.0, "nut_weight": 11.60, "nut_price": 154.20, "washer_d1": 10.5, "washer_d2": 20.0, "washer_h": 2.0, "washer_weight": 3.570, "washer_price": 61.55},
        "M12": {"nut_s": 19.0, "nut_m": 10.0, "nut_weight": 17.30, "nut_price": 222.60, "washer_d1": 13.0, "washer_d2": 24.0, "washer_h": 2.5, "washer_weight": 6.270, "washer_price": 102.05},
        "M14": {"nut_s": 22.0, "nut_m": 11.0, "nut_weight": 25.00, "nut_price": 315.00, "washer_d1": 15.0, "washer_d2": 28.0, "washer_h": 2.5, "washer_weight": 8.620, "washer_price": 137.30},
        "M16": {"nut_s": 24.0, "nut_m": 13.0, "nut_weight": 33.30, "nut_price": 414.60, "washer_d1": 17.0, "washer_d2": 30.0, "washer_h": 3.0, "washer_weight": 11.30, "washer_price": 177.50},
        "M18": {"nut_s": 27.0, "nut_m": 15.0, "nut_weight": 49.40, "nut_price": 607.80, "washer_d1": 19.0, "washer_d2": 34.0, "washer_h": 3.0, "washer_weight": 14.70, "washer_price": 228.50},
        "M20": {"nut_s": 30.0, "nut_m": 16.0, "nut_weight": 64.40, "nut_price": 787.80, "washer_d1": 21.0, "washer_d2": 37.0, "washer_h": 3.0, "washer_weight": 17.20, "washer_price": 266.00},
        "M24": {"nut_s": 36.0, "nut_m": 19.0, "nut_weight": 110.0, "nut_price": 1335.00, "washer_d1": 25.0, "washer_d2": 44.0, "washer_h": 4.0, "washer_weight": 32.30, "washer_price": 492.50},
        "M30": {"nut_s": 46.0, "nut_m": 24.0, "nut_weight": 223.0, "nut_price": 2680.00, "washer_d1": 31.0, "washer_d2": 56.0, "washer_h": 4.0, "washer_weight": 53.60, "washer_price": 780.00},
        "M36": {"nut_s": 55.0, "nut_m": 29.0, "nut_weight": 393.0, "nut_price": 4720.00, "washer_d1": 37.0, "washer_d2": 66.0, "washer_h": 5.0, "washer_weight": 92.00, "washer_price": 1350.00},
        "M48": {"nut_s": 75.0, "nut_m": 38.0, "nut_weight": 977.0, "nut_price": 11700.00, "washer_d1": 50.0, "washer_d2": 92.0, "washer_h": 8.0, "washer_weight": 220.0, "washer_price": 3200.00}
    }

@st.cache_data
def get_bolt_weights_db():
    return {
        "M3-8": 0.66, "M3-10": 0.75, "M3-12": 0.84, "M3-16": 1.00, "M3-20": 1.18, "M3-25": 1.40, "M3-30": 1.61,
        "M4-8": 1.49, "M4-10": 1.64, "M4-12": 1.80, "M4-16": 2.10, "M4-20": 2.41, "M4-25": 2.80, "M4-30": 3.19, "M4-40": 3.96,
        "M5-8": 2.38, "M5-10": 2.63, "M5-12": 2.87, "M5-16": 3.37, "M5-20": 3.87, "M5-25": 4.49, "M5-30": 5.11, "M5-40": 6.35, "M5-50": 7.59,
        "M6-8": 3.74, "M6-10": 4.08, "M6-12": 4.42, "M6-16": 5.11, "M6-20": 5.80, "M6-25": 6.65, "M6-30": 7.51, "M6-40": 9.23, "M6-50": 11.00, "M6-60": 12.70,
        "M8-8": 5.85, "M8-10": 9.10, "M8-12": 9.80, "M8-16": 11.10, "M8-20": 12.30, "M8-25": 13.90, "M8-30": 15.50, "M8-40": 18.70, "M8-50": 21.80, "M8-60": 25.00,
        "M10-10": 16.20, "M10-12": 17.20, "M10-16": 19.20, "M10-20": 21.20, "M10-25": 23.70, "M10-30": 26.20, "M10-40": 31.20, "M10-50": 36.20, "M10-60": 41.30,
        "M12-10": 23.30, "M12-12": 25.00, "M12-16": 27.70, "M12-20": 31.00, "M12-25": 34.10, "M12-30": 37.70, "M12-40": 44.90, "M12-50": 52.00, "M12-60": 58.20,
        "M16-16": 58.30, "M16-20": 63.50, "M16-25": 70.20, "M16-30": 76.90, "M16-40": 90.20, "M16-50": 103.00, "M16-60": 117.00,
        "M20-16": 105.00, "M20-20": 114.00, "M20-25": 124.00, "M20-30": 134.00, "M20-40": 155.00, "M20-50": 176.00, "M20-60": 196.00,
        "M24-20": 184.00, "M24-25": 199.00, "M24-30": 214.00, "M24-40": 244.00, "M24-50": 274.00, "M24-60": 304.00,
        "M30-35": 424.00, "M30-40": 448.00, "M30-50": 496.00, "M30-60": 543.00, "M30-80": 637.00, "M30-100": 732.00, "M30-150": 969.00, "M30-200": 1210.00,
        "M36-35": 670.00, "M36-40": 714.00, "M36-50": 783.00, "M36-60": 851.00, "M36-80": 990.00, "M36-100": 1140.00, "M36-150": 1470.00, "M36-200": 1810.00,
        "M48-40": 1590.00, "M48-50": 1710.00, "M48-60": 1830.00, "M48-80": 2080.00, "M48-100": 2320.00, "M48-150": 2940.00, "M48-200": 3560.00
    }

@st.cache_data
def get_thread_params_db():
    return {
        "M3": {"pitch": 0.50, "drill": 2.5, "fine_hole": 3.2, "medium_hole": 3.4, "t_8_8": 1.28, "t_10_9": 1.80, "t_12_9": 2.16, "p_8_8": 2.1, "p_10_9": 3.0},
        "M4": {"pitch": 0.70, "drill": 3.3, "fine_hole": 4.3, "medium_hole": 4.5, "t_8_8": 2.97, "t_10_9": 4.18, "t_12_9": 5.02, "p_8_8": 3.7, "p_10_9": 5.3},
        "M5": {"pitch": 0.80, "drill": 4.2, "fine_hole": 5.3, "medium_hole": 5.5, "t_8_8": 6.03, "t_10_9": 8.48, "t_12_9": 10.18, "p_8_8": 6.0, "p_10_9": 8.6},
        "M6": {"pitch": 1.00, "drill": 5.0, "fine_hole": 6.4, "medium_hole": 6.6, "t_8_8": 10.25, "t_10_9": 14.41, "t_12_9": 17.29, "p_8_8": 8.5, "p_10_9": 12.2},
        "M8": {"pitch": 1.25, "drill": 6.8, "fine_hole": 8.4, "medium_hole": 9.0, "t_8_8": 24.93, "t_10_9": 35.06, "t_12_9": 42.07, "p_8_8": 15.5, "p_10_9": 22.3},
        "M10": {"pitch": 1.50, "drill": 8.5, "fine_hole": 10.5, "medium_hole": 11.0, "t_8_8": 49.00, "t_10_9": 70.00, "t_12_9": 83.00, "p_8_8": 24.7, "p_10_9": 35.5},
        "M12": {"pitch": 1.75, "drill": 10.2, "fine_hole": 13.0, "medium_hole": 14.0, "t_8_8": 86.00, "t_10_9": 121.0, "t_12_9": 146.0, "p_8_8": 36.1, "p_10_9": 51.9},
        "M14": {"pitch": 2.00, "drill": 12.0, "fine_hole": 15.0, "medium_hole": 16.0, "t_8_8": 138.0, "t_10_9": 194.0, "t_12_9": 233.0, "p_8_8": 49.5, "p_10_9": 71.1},
        "M16": {"pitch": 2.00, "drill": 14.0, "fine_hole": 17.0, "medium_hole": 18.0, "t_8_8": 215.0, "t_10_9": 302.0, "t_12_9": 363.0, "p_8_8": 68.1, "p_10_9": 97.9},
        "M18": {"pitch": 2.50, "drill": 15.5, "fine_hole": 19.0, "medium_hole": 20.0, "t_8_8": 340.0, "t_10_9": 485.0, "t_12_9": 567.0, "p_8_8": 93.0, "p_10_9": 131.0},
        "M20": {"pitch": 2.50, "drill": 17.5, "fine_hole": 21.0, "medium_hole": 22.0, "t_8_8": 420.0, "t_10_9": 590.0, "t_12_9": 709.0, "p_8_8": 107.0, "p_10_9": 154.0},
        "M24": {"pitch": 3.00, "drill": 21.0, "fine_hole": 25.0, "medium_hole": 26.0, "t_8_8": 725.0, "t_10_9": 1020.0, "t_12_9": 1220.0, "p_8_8": 154.0, "p_10_9": 221.0},
        "M30": {"pitch": 3.50, "drill": 26.5, "fine_hole": 31.0, "medium_hole": 33.0, "t_8_8": 1450.00, "t_10_9": 2040.00, "t_12_9": 2450.00, "p_8_8": 243.0, "p_10_9": 348.0},
        "M36": {"pitch": 4.00, "drill": 32.0, "fine_hole": 37.0, "medium_hole": 39.0, "t_8_8": 2540.00, "t_10_9": 3570.00, "t_12_9": 4280.00, "p_8_8": 356.0, "p_10_9": 510.0},
        "M48": {"pitch": 5.00, "drill": 43.0, "fine_hole": 50.0, "medium_hole": 52.0, "t_8_8": 6220.00, "t_10_9": 8740.00, "t_12_9": 10500.00, "p_8_8": 641.0, "p_10_9": 918.0}
    }

@st.cache_data
def get_steel_properties_db():
    return {
        '4.8': {"rm_min": 420, "rel_min": 340, "vickers": "130 - 250", "brinell": "124 - 238", "rockwell": "71 - 99 HRB", "c_max": 0.55, "p_max": 0.05, "s_max": 0.06},
        '5.6': {"rm_min": 500, "rel_min": 300, "vickers": "155 - 250", "brinell": "147 - 238", "rockwell": "79 - 99 HRB", "c_max": 0.55, "p_max": 0.05, "s_max": 0.06},
        '5.8': {"rm_min": 520, "rel_min": 420, "vickers": "160 - 250", "brinell": "152 - 238", "rockwell": "82 - 99 HRB", "c_max": 0.55, "p_max": 0.05, "s_max": 0.06},
        '6.8': {"rm_min": 600, "rel_min": 480, "vickers": "190 - 250", "brinell": "181 - 238", "rockwell": "89 - 99 HRB", "c_max": 0.55, "p_max": 0.05, "s_max": 0.06},
        '8.8': {"rm_min": 800, "rel_min": 640, "vickers": "250 - 320", "brinell": "238 - 304", "rockwell": "20 - 32 HRC", "c_max": 0.55, "p_max": 0.04, "s_max": 0.05},
        '9.8': {"rm_min": 900, "rel_min": 720, "vickers": "290 - 360", "brinell": "276 - 342", "rockwell": "28 - 37 HRC", "c_max": 0.55, "p_max": 0.04, "s_max": 0.05},
        '10.9': {"rm_min": 1040, "rel_min": 900, "vickers": "320 - 380", "brinell": "304 - 361", "rockwell": "32 - 39 HRC", "c_max": 0.55, "p_max": 0.04, "s_max": 0.05},
        '12.9': {"rm_min": 1220, "rel_min": 1080, "vickers": "385 - 435", "brinell": "366 - 412", "rockwell": "39 - 44 HRC", "c_max": 0.50, "p_max": 0.035, "s_max": 0.035},
        'A2-50': {"rm_min": 500, "rel_min": 210, "vickers": "~150", "brinell": "~140", "rockwell": "~80 HRB", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03},
        'A2-70': {"rm_min": 700, "rel_min": 450, "vickers": "~200", "brinell": "~190", "rockwell": "~90 HRB", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03},
        'A2-80': {"rm_min": 800, "rel_min": 600, "vickers": "~250", "brinell": "~240", "rockwell": "~24 HRC", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03},
        'A4-50': {"rm_min": 500, "rel_min": 210, "vickers": "~150", "brinell": "~140", "rockwell": "~80 HRB", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03},
        'A4-70': {"rm_min": 700, "rel_min": 450, "vickers": "~200", "brinell": "~190", "rockwell": "~90 HRB", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03},
        'A4-80': {"rm_min": 800, "rel_min": 600, "vickers": "~250", "brinell": "~240", "rockwell": "~24 HRC", "c_max": 0.07, "p_max": 0.045, "s_max": 0.03}
    }

@st.cache_data
def get_iso_tolerances_db():
    return {
        (0, 3): {
            "H7": (10, 0), "H8": (14, 0), "G7": (12, 2),
            "h6": (0, -6), "g6": (-2, -8), "f7": (-6, -16), "js6": (3.0, -3.0)
        },
        (3, 6): {
            "H7": (12, 0), "H8": (18, 0), "G7": (16, 4),
            "h6": (0, -8), "g6": (-4, -12), "f7": (-10, -22), "js6": (4.0, -4.0)
        },
        (6, 10): {
            "H7": (15, 0), "H8": (22, 0), "G7": (20, 5),
            "h6": (0, -9), "g6": (-5, -14), "f7": (-13, -28), "js6": (4.5, -4.5)
        },
        (10, 18): {
            "H7": (18, 0), "H8": (27, 0), "G7": (24, 6),
            "h6": (0, -11), "g6": (-6, -17), "f7": (-16, -34), "js6": (5.5, -5.5)
        },
        (18, 30): {
            "H7": (21, 0), "H8": (33, 0), "G7": (28, 7),
            "h6": (0, -13), "g6": (-7, -20), "f7": (-20, -41), "js6": (6.5, -6.5)
        },
        (30, 50): {
            "H7": (25, 0), "H8": (39, 0), "G7": (34, 9),
            "h6": (0, -16), "g6": (-9, -25), "f7": (-25, -50), "js6": (8.0, -8.0)
        },
        (50, 80): {
            "H7": (30, 0), "H8": (46, 0), "G7": (40, 10),
            "h6": (0, -19), "g6": (-10, -29), "f7": (-30, -60), "js6": (9.5, -9.5)
        },
        (80, 120): {
            "H7": (35, 0), "H8": (54, 0), "G7": (47, 12),
            "h6": (0, -22), "g6": (-12, -34), "f7": (-36, -71), "js6": (11.0, -11.0)
        }
    }

@st.cache_data
def get_awg_table():
    return [
        {"AWG": "4/0", "diameter": 11.684, "cross_section": 107.20, "resistance": 0.172},
        {"AWG": "3/0", "diameter": 10.404, "cross_section": 85.01, "resistance": 0.217},
        {"AWG": "2/0", "diameter": 9.260, "cross_section": 67.43, "resistance": 0.273},
        {"AWG": "0", "diameter": 8.250, "cross_section": 53.49, "resistance": 0.345},
        {"AWG": "1", "diameter": 7.350, "cross_section": 42.41, "resistance": 0.431},
        {"AWG": "2", "diameter": 6.540, "cross_section": 33.62, "resistance": 0.544},
        {"AWG": "3", "diameter": 5.820, "cross_section": 26.67, "resistance": 0.686},
        {"AWG": "4", "diameter": 5.190, "cross_section": 21.15, "resistance": 0.865},
        {"AWG": "5", "diameter": 4.620, "cross_section": 16.77, "resistance": 1.090},
        {"AWG": "6", "diameter": 4.110, "cross_section": 13.30, "resistance": 1.380},
        {"AWG": "7", "diameter": 3.670, "cross_section": 10.55, "resistance": 1.700},
        {"AWG": "8", "diameter": 3.260, "cross_section": 8.367, "resistance": 2.140},
        {"AWG": "9", "diameter": 2.910, "cross_section": 6.631, "resistance": 2.700},
        {"AWG": "10", "diameter": 2.590, "cross_section": 5.261, "resistance": 3.410},
        {"AWG": "11", "diameter": 2.300, "cross_section": 4.170, "resistance": 4.300},
        {"AWG": "12", "diameter": 2.050, "cross_section": 3.310, "resistance": 5.420},
        {"AWG": "13", "diameter": 1.830, "cross_section": 2.630, "resistance": 6.820},
        {"AWG": "14", "diameter": 1.630, "cross_section": 2.080, "resistance": 8.600},
        {"AWG": "15", "diameter": 1.450, "cross_section": 1.650, "resistance": 10.900},
        {"AWG": "16", "diameter": 1.290, "cross_section": 1.310, "resistance": 13.700},
        {"AWG": "17", "diameter": 1.150, "cross_section": 1.040, "resistance": 17.300},
        {"AWG": "18", "diameter": 1.020, "cross_section": 0.823, "resistance": 21.900},
        {"AWG": "19", "diameter": 0.904, "cross_section": 0.653, "resistance": 27.400},
        {"AWG": "20", "diameter": 0.813, "cross_section": 0.519, "resistance": 34.800},
        {"AWG": "21", "diameter": 0.724, "cross_section": 0.412, "resistance": 43.600},
        {"AWG": "22", "diameter": 0.643, "cross_section": 0.324, "resistance": 55.200},
        {"AWG": "24", "diameter": 0.511, "cross_section": 0.205, "resistance": 87.700},
        {"AWG": "26", "diameter": 0.404, "cross_section": 0.128, "resistance": 140.000},
        {"AWG": "28", "diameter": 0.320, "cross_section": 0.080, "resistance": 222.000},
        {"AWG": "30", "diameter": 0.254, "cross_section": 0.051, "resistance": 361.000}
    ]

@st.cache_data
def get_metric_cables_db():
    return [
        {"area": 0.50, "diameter": 0.80, "cu_res": 34.50, "al_res": 53.00, "amp_1p": 0.0, "amp_3p": 0.0},
        {"area": 0.75, "diameter": 0.98, "cu_res": 23.00, "al_res": 35.30, "amp_1p": 0.0, "amp_3p": 0.0},
        {"area": 1.00, "diameter": 1.13, "cu_res": 17.20, "al_res": 26.50, "amp_1p": 0.0, "amp_3p": 0.0},
        {"area": 1.50, "diameter": 1.38, "cu_res": 11.50, "al_res": 17.70, "amp_1p": 17.5, "amp_3p": 15.5},
        {"area": 2.50, "diameter": 1.78, "cu_res": 6.90, "al_res": 10.60, "amp_1p": 24.0, "amp_3p": 21.0},
        {"area": 4.00, "diameter": 2.26, "cu_res": 4.30, "al_res": 6.60, "amp_1p": 32.0, "amp_3p": 28.0},
        {"area": 6.00, "diameter": 2.76, "cu_res": 2.90, "al_res": 4.40, "amp_1p": 41.0, "amp_3p": 36.0},
        {"area": 10.0, "diameter": 3.57, "cu_res": 1.70, "al_res": 2.70, "amp_1p": 57.0, "amp_3p": 50.0},
        {"area": 16.0, "diameter": 4.50, "cu_res": 1.10, "al_res": 1.70, "amp_1p": 76.0, "amp_3p": 68.0},
        {"area": 25.0, "diameter": 5.60, "cu_res": 0.69, "al_res": 1.10, "amp_1p": 101.0, "amp_3p": 89.0},
        {"area": 35.0, "diameter": 6.70, "cu_res": 0.49, "al_res": 0.76, "amp_1p": 125.0, "amp_3p": 110.0},
        {"area": 50.0, "diameter": 8.00, "cu_res": 0.34, "al_res": 0.53, "amp_1p": 151.0, "amp_3p": 134.0}
    ]

# --- NAVIGATION SIDEBAR ---
st.sidebar.markdown("<h2 style='text-align: center; color: #1F497D;'>⚙️ TOOLBOX v12.1</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "Wybierz moduł obliczeniowy:",
    [
        "📊 Pulpit Główny",
        "⚖️ 1. Kalkulator Masy & Surowca",
        "🔩 2. Elementy Złączne & Costing",
        "🔧 3. Parametry Montażowe",
        "🪚 4. Kalkulator Cięcia i Strat",
        "📐 5. Pasowania i Tolerancje ISO",
        "🔬 6. Właściwości i Klasy Stali",
        "🔌 7. Przewody & AWG",
        "⏱️ 8. Kalkulator Czasu Pracy"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #777;'>ENGINEERING TOOLBOX v12.2 PRO<br>Streamlit SaaS Web Suite<br>Działa 100% Offline</div>", unsafe_allow_html=True)

# Datasets Init
MATERIALS_DB = get_materials_db()
FASTENERS_DB = get_fasteners_db()
BOLT_WEIGHTS_DB = get_bolt_weights_db()
BOLT_PRICES_DB = {k: round(v * 12.5, 2) for k, v in BOLT_WEIGHTS_DB.items()}
THREAD_PARAMS_DB = get_thread_params_db()
STEEL_PROPERTIES_DB = get_steel_properties_db()
ISO_TOLERANCES_DB = get_iso_tolerances_db()
AWG_TABLE = get_awg_table()
METRIC_CABLES_DB = get_metric_cables_db()

# --- PAGES ---

# 0. PULPIT GŁÓWNY
if menu == "📊 Pulpit Główny":
    st.markdown("<div class='main-header'>ENGINEERING TOOLBOX v12.2 PRO</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zintegrowany Portal Techniczno-Kosztorysowy w czasie rzeczywistym</div>", unsafe_allow_html=True)
    
    st.markdown("""
    Witaj w profesjonalnej aplikacji **Engineering Toolbox v12.2 PRO** przeniesionej na silnik **Streamlit**! 
    Narzędzie to łączy zaawansowane bazy danych normatywnych z interaktywnymi kalkulatorami, umożliwiając 
    błyskawiczne wykonywanie obliczeń fizycznych, montażowych, pasowań oraz precyzyjne kosztorysowanie.
    
    ### 🚀 Funkcjonalności i zalety systemu Streamlit:
    1. **Błyskawiczne przeliczanie:** Wszystkie parametry są aktualizowane w czasie rzeczywistym przy każdej zmianie suwaka lub pola wejściowego.
    2. **Wizualna czystość:** Przejrzyste tabele składowe oraz pełna responsywność ułatwiają pracę na każdym urządzeniu (komputer, tablet, telefon).
    3. **Integracja baz danych:** Kompletne ugruntowanie w Twoich źródłach technicznych: od mas łączników po dokładne tolerancje mikrometryczne i rezystancję przewodów miedzianych.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h4>🎨 OZNACZENIA KOLORYSTYCZNE INTERFEJSU</h4>"
                    "<ul>"
                    "<li><b>Niebieskie pola wprowadzania:</b> Twoje suwaki i formularze do konfiguracji wymiarów.</li>"
                    "<li><b>Zielone bloki wyników:</b> Natychmiastowe podsumowania fizyczne oraz finansowe.</li>"
                    "<li><b>Alerty pomarańczowe i czerwone:</b> Sygnalizatory przekroczenia bezpiecznych wartości (np. wcisku lub wymiarów nominalnych).</li>"
                    "</ul></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h4>📋 DOSTĘPNE MODUŁY</h4>"
                    "<ul>"
                    "<li><b>Kalkulator masy:</b> Obsługuje 6 rodzajów profili hutniczych (w tym pręty sześciokątne).</li>"
                    "<li><b>Elementy złączne:</b> Costing i ciężary śrub, nakrętek i podkładek do rozmiaru M48.</li>"
                    "<li><b>Pasowania ISO:</b> Dobiera odchyłki mikrometryczne dla otworów i wałków (zakres 1-120mm).</li>"
                    "<li><b>Przewody i AWG:</b> Pełna baza rezystancji i ampacytów kabli miedzianych i aluminiowych.</li>"
                    "</ul></div>", unsafe_allow_html=True)

# 1. KALKULATOR MASY & SUROWCA
elif menu == "⚖️ 1. Kalkulator Masy & Surowca":
    st.markdown("<div class='main-header'>⚖️ 1. KALKULATOR MASY I KOSZTÓW MATERIAŁU</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Obliczanie parametrów fizycznych oraz kosztorys surowcowy profili hutniczych</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wprowadź dane geometryczne")
        profile = st.selectbox("Rodzaj profilu hutniczego:", ["Blacha/Płaskownik", "Pręt okrągły", "Rura okrągła", "Profil kwadratowy", "Profil prostokątny", "Pręt sześciokątny"])
        material = st.selectbox("Gatunek materiału:", list(MATERIALS_DB.keys()))
        
        dim1, dim2, wall = 0.0, 0.0, 0.0
        
        if profile == "Blacha/Płaskownik":
            dim1 = st.number_input("Grubość t (mm):", min_value=0.1, value=10.0, step=1.0)
            dim2 = st.number_input("Szerokość b (mm):", min_value=1.0, value=100.0, step=10.0)
        elif profile == "Pręt okrągły":
            dim1 = st.number_input("Średnica d (mm):", min_value=0.1, value=50.0, step=5.0)
        elif profile == "Rura okrągła":
            dim1 = st.number_input("Średnica zewnętrzna D (mm):", min_value=0.1, value=60.0, step=5.0)
            wall = st.number_input("Grubość ścianki g (mm):", min_value=0.1, value=3.0, step=0.5)
        elif profile == "Profil kwadratowy":
            dim1 = st.number_input("Bok A (mm):", min_value=0.1, value=40.0, step=5.0)
            wall = st.number_input("Grubość ścianki g (mm) (wpisz 0 dla pręta pełnego):", min_value=0.0, value=2.0, step=0.5)
        elif profile == "Profil prostokątny":
            dim1 = st.number_input("Bok A (mm):", min_value=0.1, value=60.0, step=5.0)
            dim2 = st.number_input("Bok B (mm):", min_value=0.1, value=40.0, step=5.0)
            wall = st.number_input("Grubość ścianki g (mm) (wpisz 0 dla pręta pełnego):", min_value=0.0, value=2.0, step=0.5)
        elif profile == "Pręt sześciokątny":
            dim1 = st.number_input("Rozmiar s pod klucz (mm):", min_value=0.1, value=19.0, step=1.0)
            
        length = st.number_input("Długość całkowita L (mm):", min_value=1.0, value=1000.0, step=100.0)
        qty = st.number_input("Ilość sztuk w partii:", min_value=1, value=10, step=1)
        
        mat_data = MATERIALS_DB[material]
        sug_price = mat_data["price_kg"]
        custom_price = st.number_input("Własna cena surowca (PLN/kg) [Zostaw 0 dla ceny sugerowanej]:", min_value=0.0, value=0.0, step=0.5)
        eff_price = custom_price if custom_price > 0 else sug_price

    with col_out:
        st.subheader("Wyniki kalkulacji fizycznych i kosztowych")
        
        # Volume Calculation (cm3) based on formulas [32]
        vol = 0.0
        if profile == "Blacha/Płaskownik":
            vol = (dim1 * dim2 * length) / 1000.0
        elif profile == "Pręt okrągły":
            vol = (math.pi * (dim1**2) / 4.0 * length) / 1000.0
        elif profile == "Rura okrągła":
            vol = (math.pi * (dim1**2 - (dim1 - 2.0*wall)**2) / 4.0 * length) / 1000.0
        elif profile == "Profil kwadratowy":
            if wall > 0:
                vol = (dim1**2 - (dim1 - 2.0*wall)**2) * length / 1000.0
            else:
                vol = (dim1**2) * length / 1000.0
        elif profile == "Profil prostokątny":
            if wall > 0:
                vol = (dim1*dim2 - (dim1 - 2.0*wall)*(dim2 - 2.0*wall)) * length / 1000.0
            else:
                vol = (dim1*dim2) * length / 1000.0
        elif profile == "Pręt sześciokątny":
            # Formula: 0.866 * s^2 * L [32]
            vol = (0.866 * (dim1**2) * length) / 1000.0
            
        density_g = mat_data["density_g"]
        single_mass = (vol * density_g) / 1000.0 # kg
        total_mass = single_mass * qty
        total_cost = total_mass * eff_price
        
        st.info(f"**Wybrany materiał:** {material}  \n"
                f"**Gęstość konstrukcyjna:** {mat_data['density_kg']} kg/m³  \n"
                f"**Zastosowanie standardowe:** {mat_data['desc']}")
        
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 0.9rem; color: #555;'>Masa jednostkowa elementu:</div>
            <div class='metric-value'>{single_mass:.3f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Masa całkowita partii ({qty} szt.):</div>
            <div class='metric-value'>{total_mass:.2f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Efektywna stawka za kilogram:</div>
            <div class='metric-value'>{eff_price:.2f} PLN/kg</div>
            <br>
            <div style='font-size: 1rem; font-weight: bold; color: #1F497D;'>ŁĄCZNY KOSZT MATERIAŁU:</div>
            <div class='metric-cost'>{total_cost:.2f} PLN</div>
        </div>
        """, unsafe_allow_html=True)

# 2. ELEMENTY ZŁĄCZNE & COSTING
elif menu == "🔩 2. Elementy Złączne & Costing":
    st.markdown("<div class='main-header'>🔩 2. KALKULATOR ELEMENTÓW ZŁĄCZNYCH I COSTING</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zestawienia masowe i wycena zestawów śrubowych wg DIN 933 / 934 / 125</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Konfigurator Zestawu")
        size = st.selectbox("Nominalna średnica gwintu:", list(FASTENERS_DB.keys()), index=4) # Default M8
        
        # Available lengths filtering
        avail_lengths = [int(k.split("-")[1]) for k in BOLT_WEIGHTS_DB.keys() if k.split("-")[0] == size]
        length = st.selectbox("Długość śruby L (mm) [DIN 933 / Pełny gwint]:", sorted(avail_lengths), index=2 if len(avail_lengths)>2 else 0)
        
        material_class = st.selectbox("Klasa wytrzymałości / Materiał:", [
            "Klasa 8.8 (Stal węg. ocynk) [Mnożnik: 1.0x]",
            "Klasa 10.9 (Stal węg. ocynk) [Mnożnik: 1.3x]",
            "Klasa 12.9 (Stal węg. czarna) [Mnożnik: 1.6x]",
            "Stal nierdzewna A2 (304) [Mnożnik: 2.5x]",
            "Stal kwasoodporna A4 (316) [Mnożnik: 3.8x]"
        ])
        
        qty = st.number_input("Ilość kompletnych zestawów (szt.):", min_value=1, value=1000, step=100)
        add_nut = st.selectbox("Dodaj nakrętkę sześciokątną DIN 934?", ["Tak", "Nie"], index=0)
        num_washers = st.selectbox("Ilość podkładek płaskich DIN 125:", [0, 1, 2], index=2)

    with col_out:
        st.subheader("Kalkulacja kosztów i masy zestawu")
        
        # Multipliers
        multiplier = 1.0
        if "10.9" in material_class: multiplier = 1.3
        elif "12.9" in material_class: multiplier = 1.6
        elif "A2" in material_class: multiplier = 2.5
        elif "A4" in material_class: multiplier = 3.8
        
        bolt_key = f"{size}-{length}"
        bolt_weight = BOLT_WEIGHTS_DB.get(bolt_key, 0.0) # kg per 1000 pcs (equal to grams per single piece) [26]
        bolt_price = BOLT_PRICES_DB.get(bolt_key, 0.0)
        
        fdata = FASTENERS_DB[size]
        nut_weight = fdata["nut_weight"] if add_nut == "Tak" else 0.0
        nut_price = fdata["nut_price"] if add_nut == "Tak" else 0.0
        
        washer_weight = fdata["washer_weight"] * num_washers
        washer_price = fdata["washer_price"] * num_washers
        
        # Single set totals in grams
        single_set_weight_g = bolt_weight + nut_weight + washer_weight
        total_party_mass_kg = (single_set_weight_g * qty) / 1000.0
        
        # Pricing
        eff_bolt_price = bolt_price * multiplier
        eff_nut_price = nut_price * multiplier
        eff_washer_price = washer_price * multiplier
        
        total_set_cost_1k = eff_bolt_price + eff_nut_price + eff_washer_price
        total_cost_pln = (total_set_cost_1k * qty) / 1000.0
        
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 0.9rem; color: #555;'>Masa jednego kompletnego zestawu śrubowego:</div>
            <div class='metric-value'>{single_set_weight_g:.2f} g</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Łączna masa całej partii ({qty} szt.):</div>
            <div class='metric-value'>{total_party_mass_kg:.2f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Mnożnik materiałowy (klasa/stal):</div>
            <div class='metric-value'>{multiplier:.1f}x</div>
            <br>
            <div style='font-size: 1rem; font-weight: bold; color: #1F497D;'>ŁĄCZNY KOSZT ZESTAWÓW:</div>
            <div class='metric-cost'>{total_cost_pln:.2f} PLN</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Zobacz szczegółowe zestawienie wagowe i wycenę bazy"):
            df_breakdown = pd.DataFrame({
                "Składnik": ["Śruba DIN 933", "Nakrętka DIN 934", "Podkładki DIN 125"],
                "Masa 1 szt. (g)": [bolt_weight, fdata["nut_weight"], fdata["washer_weight"]],
                "Ciężar w zest. (g)": [bolt_weight, nut_weight, washer_weight],
                "Masa partii (kg)": [
                    round((bolt_weight * qty) / 1000.0, 3),
                    round((nut_weight * qty) / 1000.0, 3),
                    round((washer_weight * qty) / 1000.0, 3)
                ],
                "Cena bazowa / 1k (PLN)": [bolt_price, nut_price, washer_price],
                "Cena efektywna / 1k (PLN)": [eff_bolt_price, eff_nut_price, eff_washer_price]
            })
            st.dataframe(df_breakdown, hide_index=True)

# 3. PARAMETRY MONTAŻOWE
elif menu == "🔧 3. Parametry Montażowe":
    st.markdown("<div class='main-header'>🔧 3. PARAMETRY MONTAŻOWE GWINTÓW</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zalecane średnice wierteł, otwory przejściowe i momenty dokręcania śrub</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wybór parametrów śruby")
        size = st.selectbox("Rozmiar śruby / gwintu:", list(THREAD_PARAMS_DB.keys()), index=4) # Default M8
        class_bolt = st.selectbox("Klasa wytrzymałości śruby (własności mechaniczne):", ["8.8", "10.9", "12.9"])
        
    with col_out:
        st.subheader("Rekomendowane wytyczne i momenty")
        tdata = THREAD_PARAMS_DB[size]
        
        # Calculate torques & preloads
        torque = 0.0
        preload = 0.0
        if class_bolt == "8.8":
            torque = tdata["t_8_8"]
            preload = tdata["p_8_8"]
        elif class_bolt == "10.9":
            torque = tdata["t_10_9"]
            preload = tdata["p_10_9"]
        elif class_bolt == "12.9":
            torque = tdata["t_12_9"]
            preload = tdata["p_10_9"] * 1.2 # Extrapolated
            
        st.markdown(f"""
        <div class='card'>
            <table style='width:100%; border: none;'>
                <tr>
                    <td style='font-weight: bold;'>Skok gwintu metrycznego zwykłego:</td>
                    <td style='text-align: right; font-size: 1.1rem; color: #1F497D;'>{tdata['pitch']:.2f} mm</td>
                </tr>
                <tr style='background-color: #E2EFDA;'>
                    <td style='font-weight: bold; color: #2F5496;'>Zalecane wiertło pod gwint:</td>
                    <td style='text-align: right; font-size: 1.4rem; font-weight: bold; color: #2F5496;'>Ø {tdata['drill']:.1f} mm</td>
                </tr>
                <tr>
                    <td>Otwór przejściowy dokładny (Fine):</td>
                    <td style='text-align: right;'>Ø {tdata['fine_hole']:.1f} mm</td>
                </tr>
                <tr>
                    <td>Otwór przejściowy średni (Medium):</td>
                    <td style='text-align: right;'>Ø {tdata['medium_hole']:.1f} mm</td>
                </tr>
                <tr style='background-color: #DCE6F1;'>
                    <td style='font-weight: bold; color: #1F497D;'>Maksymalny moment dokręcania Ma (klasa {class_bolt}):</td>
                    <td style='text-align: right; font-size: 1.4rem; font-weight: bold; color: #1F497D;'>{torque:.2f} Nm</td>
                </tr>
                <tr>
                    <td>Zalecana siła napięcia wstępnego Fm:</td>
                    <td style='text-align: right; font-weight: bold;'>{preload:.1f} kN</td>
                </tr>
            </table>
            <div style='font-size: 0.8rem; color: #777; margin-top: 1.2rem; font-style: italic;'>
                * Współczynnik tarcia łba i gwintu μ = 0.14 ( plain carbon steel, czarna sucha, nieoliwiona ). Obliczenia wg DIN EN ISO 898 [29].
            </div>
        </div>
        """, unsafe_allow_html=True)

# 4. KALKULATOR CIĘCIA I STRAT
elif menu == "🪚 4. Kalkulator Cięcia i Strat":
    st.markdown("<div class='main-header'>🪚 4. KALKULATOR CIĘCIA I STRAT MATERIAŁOWYCH</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zoptymalizowane cięcie profili hutniczych z uwzględnieniem rzazu tarczy tnącej</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wprowadź dane technologiczne rozkroju")
        stock_len = st.number_input("Długość profilu handlowego (sztanga) (mm):", min_value=100.0, value=6000.0, step=500.0)
        cut_len = st.number_input("Długość gotowego uciętego elementu (mm):", min_value=1.0, value=450.0, step=10.0)
        qty_req = st.number_input("Wymagana ilość sztuk gotowych (szt.):", min_value=1, value=50, step=5)
        kerf = st.number_input("Grubość rzazu piły (grubość tarczy tnącej) (mm):", min_value=0.0, value=3.0, step=0.5)
        weight_per_m = st.number_input("Masa 1 metra bieżącego profilu (kg/m):", min_value=0.01, value=4.5, step=0.5)
        price_per_kg = st.number_input("Cena profilu za kg (PLN/kg):", min_value=0.1, value=6.50, step=0.5)

    with col_out:
        st.subheader("Wyniki optymalizacji i koszt strat")
        
        if cut_len <= 0 or stock_len < cut_len:
            pcs_per_bar = 0
            bars_req = 0
            remnant_single = stock_len
            total_waste_mm = 0
            yield_pct = 0.0
        else:
            # Formula for pieces per bar considering kerf
            pcs_per_bar = int((stock_len + kerf) / (cut_len + kerf))
            if pcs_per_bar <= 0:
                bars_req = 0
                remnant_single = stock_len
                total_waste_mm = 0
                yield_pct = 0.0
            else:
                bars_req = math.ceil(qty_req / pcs_per_bar)
                remnant_single = stock_len - (pcs_per_bar * cut_len) - ((pcs_per_bar - 1) * kerf)
                total_waste_mm = (bars_req * stock_len) - (qty_req * cut_len)
                yield_pct = (qty_req * cut_len) / (bars_req * stock_len) * 100.0
                
        total_bought_mass = (bars_req * stock_len / 1000.0) * weight_per_m
        total_useful_mass = (qty_req * cut_len / 1000.0) * weight_per_m
        total_waste_mass = max(0.0, total_bought_mass - total_useful_mass)
        
        total_bought_cost = total_bought_mass * price_per_kg
        total_waste_cost = total_waste_mass * price_per_kg
        
        st.markdown(f"""
        <div class='card'>
            <table style='width:100%; border: none;'>
                <tr style='font-size: 1.1rem; background-color: #E2EFDA;'>
                    <td style='font-weight: bold; color: #27AE60;'>Liczba elementów z 1 sztangi:</td>
                    <td style='text-align: right; font-weight: bold; color: #27AE60;'>{pcs_per_bar} szt.</td>
                </tr>
                <tr style='font-size: 1.1rem; background-color: #DCE6F1;'>
                    <td style='font-weight: bold; color: #1F497D;'>Wymagana ilość sztang zakupowych:</td>
                    <td style='text-align: right; font-weight: bold; color: #1F497D;'>{bars_req} szt. (łącznie {(bars_req*stock_len/1000.0):.1f} mb)</td>
                </tr>
                <tr>
                    <td>Użyteczny odpad (końcówka) z 1 sztangi:</td>
                    <td style='text-align: right;'>{remnant_single:.1f} mm</td>
                </tr>
                <tr>
                    <td>Łączna długość strat (odpady + rzazy piły):</td>
                    <td style='text-align: right;'>{total_waste_mm:.0f} mm</td>
                </tr>
                <tr style='font-weight: bold;'>
                    <td>Współczynnik wykorzystania surowca:</td>
                    <td style='text-align: right; color: #27AE60;'>{yield_pct:.2f}%</td>
                </tr>
                <tr style='border-top: 1px solid #ccc;'>
                    <td>Masa zakupionego materiału:</td>
                    <td style='text-align: right;'>{total_bought_mass:.2f} kg</td>
                </tr>
                <tr>
                    <td>Masa gotowych wyrobów (netto):</td>
                    <td style='text-align: right;'>{total_useful_mass:.2f} kg</td>
                </tr>
                <tr>
                    <td>Masa całkowita strat:</td>
                    <td style='text-align: right; color: #C0392B;'>{total_waste_mass:.2f} kg</td>
                </tr>
                <tr style='border-top: 2px solid #2F5496; font-size: 1.2rem; font-weight: bold; color: #1F497D;'>
                    <td>ŁĄCZNY KOSZT SUROWCA (ZAKUP):</td>
                    <td style='text-align: right; font-size: 1.5rem; color: #2F5496;'>{total_bought_cost:.2f} PLN</td>
                </tr>
                <tr style='font-size: 1.1rem; font-weight: bold; color: #C0392B;'>
                    <td>KOSZT STRAT ODPADOWYCH:</td>
                    <td style='text-align: right; font-size: 1.3rem;' class='metric-waste'>{total_waste_cost:.2f} PLN</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# 5. PASOWANIA I TOLERANCJE ISO
elif menu == "📐 5. Pasowania i Tolerancje ISO":
    st.markdown("<div class='main-header'>📐 5. PASOWANIA I TOLERANCJE ISO 286-2</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Dobór odchyłek wymiarowych oraz wyznaczanie luzu lub wcisku dla wałków i otworów</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Konfigurator Pasowania")
        nominal = st.number_input("Wymiar nominalny elementu d (mm) [Zakres: 1 do 120 mm]:", min_value=1.0, max_value=120.0, value=20.0, step=1.0)
        hole_class = st.selectbox("Tolerancja otworu (Hole):", ["H7", "H8", "G7", "Brak"], index=0)
        shaft_class = st.selectbox("Tolerancja wałka (Shaft):", ["h6", "g6", "f7", "js6", "Brak"], index=0)

    with col_out:
        st.subheader("Charakterystyka skojarzenia")
        
        # Range lookup logic [30]
        matched_range = None
        matched_data = None
        for (low, high), data in ISO_TOLERANCES_DB.items():
            if low < nominal <= high:
                matched_range = (low, high)
                matched_data = data
                break
                
        if matched_range:
            st.info(f"**Przedział wymiarowy ISO:** over {matched_range[0]} to {matched_range[1]} mm")
            
            # Hole ES/EI
            es_hole_um, ei_hole_um = 0, 0
            hole_defined = hole_class != "Brak"
            if hole_defined:
                es_hole_um, ei_hole_um = matched_data.get(hole_class, (0, 0))
            
            # Shaft es/ei
            es_shaft_um, ei_shaft_um = 0, 0
            shaft_defined = shaft_class != "Brak"
            if shaft_defined:
                es_shaft_um, ei_shaft_um = matched_data.get(shaft_class, (0, 0))
                
            hole_max = nominal + es_hole_um / 1000.0
            hole_min = nominal + ei_hole_um / 1000.0
            shaft_max = nominal + es_shaft_um / 1000.0
            shaft_min = nominal + ei_shaft_um / 1000.0
            
            tol_hole = es_hole_um - ei_hole_um
            tol_shaft = es_shaft_um - ei_shaft_um
            
            fit_type = "Brak pasowania (Skonfiguruj wałek i otwór)"
            fit_color = "#333333"
            
            if hole_defined and shaft_defined:
                if hole_min >= shaft_max:
                    luz_min = (hole_min - shaft_max) * 1000.0
                    luz_max = (hole_max - shaft_min) * 1000.0
                    fit_type = "PASOWANIE LUZOWE (Clearance Fit)"
                    fit_desc = f"Zawsze występuje luz montażowy.  \n**Luz minimalny:** {luz_min:.1f} µm  \n**Luz maksymalny:** {luz_max:.1f} µm"
                    fit_color = "#27AE60"
                elif shaft_min >= hole_max:
                    wcisk_min = (shaft_min - hole_max) * 1000.0
                    wcisk_max = (shaft_max - hole_min) * 1000.0
                    fit_type = "PASOWANIE CIASNE (Interference Fit)"
                    fit_desc = f"Wymagane połączenie wciskowe.  \n**Wcisk minimalny:** {wcisk_min:.1f} µm  \n**Wcisk maksymalny:** {wcisk_max:.1f} µm"
                    fit_color = "#C0392B"
                else:
                    luz_gora = (hole_max - shaft_min) * 1000.0
                    wcisk_gora = (shaft_max - hole_min) * 1000.0
                    fit_type = "PASOWANIE MIESZANE (Transition Fit)"
                    fit_desc = f"Zależnie od dokładności wykonania powstanie luz lub wcisk.  \n**Maksymalny luz:** {luz_gora:.1f} µm  \n**Maksymalny wcisk:** {wcisk_gora:.1f} µm"
                    fit_color = "#F39C12"
                    
            st.markdown(f"""
            <div class='card'>
                <table style='width:100%; border: none;'>
                    <tr>
                        <td colspan='2' style='font-weight: bold; background-color: #ECEFF1; font-size: 1.1rem; color: #1F497D; padding: 5px;'>OTWÓR (Hole: {hole_class})</td>
                    </tr>
                    <tr>
                        <td>Odchyłki ES / EI:</td>
                        <td style='text-align: right; font-weight: bold;'>+{es_hole_um} / +{ei_hole_um} µm</td>
                    </tr>
                    <tr>
                        <td>Wymiary graniczne D_max / D_min:</td>
                        <td style='text-align: right; font-weight: bold; color: #2F5496;'>{hole_max:.4f} / {hole_min:.4f} mm</td>
                    </tr>
                    <tr>
                        <td>Pole tolerancji TD:</td>
                        <td style='text-align: right;'>{tol_hole} µm</td>
                    </tr>
                    <tr style='border-top: 1px solid #ccc;'>
                        <td colspan='2' style='font-weight: bold; background-color: #ECEFF1; font-size: 1.1rem; color: #1F497D; padding: 5px;'>WAŁEK (Shaft: {shaft_class})</td>
                    </tr>
                    <tr>
                        <td>Odchyłki es / ei:</td>
                        <td style='text-align: right; font-weight: bold;'>{es_shaft_um:+} / {ei_shaft_um:+} µm</td>
                    </tr>
                    <tr>
                        <td>Wymiary graniczne d_max / d_min:</td>
                        <td style='text-align: right; font-weight: bold; color: #2F5496;'>{shaft_max:.4f} / {shaft_min:.4f} mm</td>
                    </tr>
                    <tr>
                        <td>Pole tolerancji Td:</td>
                        <td style='text-align: right;'>{tol_shaft} µm</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            if hole_defined and shaft_defined:
                st.markdown(f"""
                <div class='card' style='border-left-color: {fit_color};'>
                    <div style='font-weight: bold; font-size: 1.1rem; color: {fit_color};'>{fit_type}</div>
                    <div style='margin-top: 5px; font-size: 1rem;'>{fit_desc}</div>
                </div>
                """, unsafe_allow_html=True)

            # Dodatkowy wykres stref tolerancji za pomocą Plotly
            st.markdown("### 📊 Wykres Stref Tolerancji")
            fig = go.Figure()
            
            # Linia zerowa (linia nominalna)
            fig.add_shape(
                type="line",
                x0=-0.6, y0=0, x1=1.6, y1=0,
                line=dict(color="#777777", width=2, dash="dash")
            )
            
            # Słupki tolerancji
            if hole_defined:
                fig.add_trace(go.Bar(
                    x=["Otwór (Hole)"],
                    y=[es_hole_um - ei_hole_um],
                    base=ei_hole_um,
                    name=f"Otwór {hole_class}",
                    marker_color="#2F5496",
                    text=[f"+{es_hole_um} µm" if es_hole_um >= 0 else f"{es_hole_um} µm"],
                    textposition="inside" if (es_hole_um - ei_hole_um) > 8 else "outside",
                    hovertemplate=f"Otwór {hole_class}<br>ES: {es_hole_um:+} µm<br>EI: {ei_hole_um:+} µm<br>TD: {tol_hole} µm<extra></extra>"
                ))
                
            if shaft_defined:
                fig.add_trace(go.Bar(
                    x=["Wałek (Shaft)"],
                    y=[es_shaft_um - ei_shaft_um],
                    base=ei_shaft_um,
                    name=f"Wałek {shaft_class}",
                    marker_color="#D35400",
                    text=[f"{es_shaft_um:+} µm" if es_shaft_um != 0 else "0 µm"],
                    textposition="inside" if (es_shaft_um - ei_shaft_um) > 8 else "outside",
                    hovertemplate=f"Wałek {shaft_class}<br>es: {es_shaft_um:+} µm<br>ei: {ei_shaft_um:+} µm<br>Td: {tol_shaft} µm<extra></extra>"
                ))
                
            # Wyznaczenie zakresu osi Y dla czytelności
            y_vals = []
            if hole_defined:
                y_vals.extend([ei_hole_um, es_hole_um])
            if shaft_defined:
                y_vals.extend([ei_shaft_um, es_shaft_um])
            if not y_vals:
                y_vals = [0]
            y_min = min(y_vals)
            y_max = max(y_vals)
            padding = max(15.0, (y_max - y_min) * 0.3)
            
            fig.update_layout(
                yaxis_title="Odchyłka [µm]",
                xaxis=dict(range=[-0.5, 1.5]),
                showlegend=True,
                height=350,
                margin=dict(l=50, r=40, t=20, b=20),
                yaxis=dict(range=[y_min - padding, y_max + padding])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Wymiar nominalny musi mieścić się w przedziale (1, 120] mm.")

# 6. WŁAŚCIWOŚCI I KLASY STALI
elif menu == "🔬 6. Właściwości i Klasy Stali":
    st.markdown("<div class='main-header'>🔬 6. WŁAŚCIWOŚCI I KLASY WYTRZYMAŁOŚCI STALI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Karta twardości, wytrzymałości mechanicznej oraz granicznych składów chemicznych</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wybór klasy śruby lub gatunku")
        steel_grade = st.selectbox("Wybierz klasę śruby lub gatunek stali:", list(STEEL_PROPERTIES_DB.keys()), index=4) # Default 8.8
        
    with col_out:
        st.subheader("Karta Właściwości Materiałowych")
        sdata = STEEL_PROPERTIES_DB[steel_grade]
        
        is_stainless = "A2" in steel_grade or "A4" in steel_grade
        steel_type = "Austenityczna Stal Nierdzewna" if is_stainless else "Stal Węglowa / Stopowa do ulepszania cieplnego"
        norm_text = "DIN EN ISO 3506" if is_stainless else "DIN EN ISO 898"
        
        st.info(f"**Typ materiału:** {steel_type}  \n"
                f"**Zgodność z normami:** {norm_text}")
        
        st.markdown(f"""
        <div class='card'>
            <table style='width:100%; border: none;'>
                <tr style='font-weight: bold; background-color: #E2EFDA;'>
                    <td style='color: #2F5496;'>Wytrzymałość na rozciąganie Rm (min):</td>
                    <td style='text-align: right; font-size: 1.2rem; color: #2F5496;'>{sdata['rm_min']} MPa</td>
                </tr>
                <tr style='font-weight: bold; background-color: #DCE6F1;'>
                    <td style='color: #1F497D;'>Granica plastyczności ReL (min):</td>
                    <td style='text-align: right; font-size: 1.2rem; color: #1F497D;'>{sdata['rel_min']} MPa</td>
                </tr>
                <tr>
                    <td>Twardość Vickersa (HV):</td>
                    <td style='text-align: right; font-weight: bold;'>{sdata['vickers']} HV</td>
                </tr>
                <tr>
                    <td>Twardość Brinella (HB):</td>
                    <td style='text-align: right; font-weight: bold;'>{sdata['brinell']} HB</td>
                </tr>
                <tr>
                    <td>Twardość Rockwella (HRB/HRC):</td>
                    <td style='text-align: right; font-weight: bold;'>{sdata['rockwell']}</td>
                </tr>
                <tr style='border-top: 1px solid #ccc; font-weight: bold; color: #555;'>
                    <td colspan='2' style='padding-top: 10px;'>Skład chemiczny (limity % max):</td>
                </tr>
                <tr>
                    <td>Zawartość Węgla C (% max):</td>
                    <td style='text-align: right;'>{sdata['c_max']:.3f}%</td>
                </tr>
                <tr>
                    <td>Zawartość Fosforu P (% max):</td>
                    <td style='text-align: right;'>{sdata['p_max']}%</td>
                </tr>
                <tr>
                    <td>Zawartość Siarki S (% max):</td>
                    <td style='text-align: right;'>{sdata['s_max']}%</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# 7. PRZEWODY & AWG
elif menu == "🔌 7. Przewody & AWG":
    st.markdown("<div class='main-header'>🔌 7. PRZEWODY ELEKTRYCZNE & TABELA AWG</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Konwersja amerykańskich rozmiarów AWG oraz obciążalność kabli metrycznych</div>", unsafe_allow_html=True)
    
    tab_awg, tab_metric = st.tabs(["🇺🇸 Konwerter AWG (KBE)", "🇪🇺 Kable Metryczne & Rezystancje"])
    
    with tab_awg:
        st.subheader("Tabela amerykańskich rozmiarów AWG (American Wire Gauge)")
        df_awg = pd.DataFrame(AWG_TABLE)
        df_awg.columns = ["Numer AWG", "Średnica zewnętrzna Ø (mm)", "Przekrój geometryczny (mm²)", "Rezystancja przewodnika (Ohm/km)"]
        
        # Interactive selector for conversion
        selected_awg = st.selectbox("Szybki podgląd parametrów AWG:", [row["AWG"] for row in AWG_TABLE])
        awg_matched = next(item for item in AWG_TABLE if item["AWG"] == selected_awg)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Średnica zewnętrzna Ø", f"{awg_matched['diameter']:.3f} mm")
        with col2:
            st.metric("Przekrój poprzeczny", f"{awg_matched['cross_section']:.3f} mm²")
        with col3:
            st.metric("Rezystancja miedzi przy 20°C", f"{awg_matched['resistance']:.4f} Ω/km")
            
        st.dataframe(df_awg, use_container_width=True, hide_index=True)
        
    with tab_metric:
        st.subheader("Miedziane i Aluminiowe Kable Metryczne")
        df_metric = pd.DataFrame(METRIC_CABLES_DB)
        df_metric.columns = ["Przekrój (mm²)", "Przybliżona Średnica (mm)", "Rezystancja Cu przy 20°C (Ω/km)", "Rezystancja Al przy 20°C (Ω/km)", "Obciążalność 1-faza w powietrzu (A)", "Obciążalność 3-fazy w powietrzu (A)"]
        st.dataframe(df_metric, use_container_width=True, hide_index=True)

# 8. KALKULATOR CZASU PRACY
elif menu == "⏱️ 8. Kalkulator Czasu Pracy":
    st.markdown("<div class='main-header'>⏱️ 8. KALKULATOR CZASU PRACY & ROBOCIZNY</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Dynamiczne wycenianie procesów technologicznych i kosztów pracy ludzkiej</div>", unsafe_allow_html=True)
    
    # Session state for operations list
    if "operations" not in st.session_state:
        st.session_state["operations"] = [
            {"step": "Projektowanie konstrukcji CAD", "role": "Projektowanie CAD / Inżynieria", "hours": 4.0},
            {"step": "Generowanie ścieżek CAM & obróbka CNC", "role": "Programowanie i Obróbka CNC", "hours": 6.0},
            {"step": "Spawanie ramy nośnej", "role": "Spawanie i Ślusarstwo", "hours": 3.0},
            {"step": "Montaż mechaniczny podzespołów", "role": "Montaż i Pasowanie", "hours": 5.0},
            {"step": "Kontrola metrologiczna i odbiór jakości", "role": "Kontrola Jakości i Metrologia", "hours": 2.0}
        ]
        
    col_dict, col_calc = st.columns([1, 2])
    
    with col_dict:
        st.subheader("1. Konfiguracja stawek godzinowych")
        st.info("Pola są edytowalne. Możesz dostosować stawki roboczogodziny (PLN/h) dla każdego stanowiska:")
        rates = {}
        for role, default_rate in LABOR_RATES.items():
            rates[role] = st.number_input(f"{role} (PLN/h):", min_value=1.0, value=float(default_rate), step=5.0)
            
    with col_calc:
        st.subheader("2. Harmonogram operacji technologicznych")
        
        # Form to add operation
        with st.expander("➕ Dodaj nową operację / krok technologiczny"):
            new_step = st.text_input("Opis operacji / Krok:", placeholder="np. Piaskowanie konstrukcji ramy")
            new_role = st.selectbox("Przypisane stanowisko:", list(LABOR_RATES.keys()))
            new_hours = st.number_input("Czas trwania operacji (h):", min_value=0.1, value=1.0, step=0.5)
            
            if st.button("Dodaj krok do budżetu"):
                if new_step:
                    st.session_state["operations"].append({"step": new_step, "role": new_role, "hours": new_hours})
                    st.toast("Pomyślnie dodano operację!", icon="✅")
                else:
                    st.error("Opis operacji nie może być pusty!")
                    
        st.write("---")
        st.write("**Lista operacji technologicznych w projekcie:**")
        
        total_hours = 0.0
        total_labor_cost = 0.0
        
        display_list = []
        for i, op in enumerate(st.session_state["operations"]):
            rate = rates[op["role"]]
            cost = op["hours"] * rate
            total_hours += op["hours"]
            total_labor_cost += cost
            display_list.append({
                "Lp.": i + 1,
                "Opis kroku technologicznego": op["step"],
                "Stanowisko": op["role"],
                "Czas (h)": op["hours"],
                "Stawka (PLN/h)": rate,
                "Koszt kroku (PLN)": cost
            })
            
        st.dataframe(pd.DataFrame(display_list), hide_index=True, use_container_width=True)
        
        # Reset button
        if st.button("🗑️ Resetuj listę operacji do domyślnych"):
            st.session_state["operations"] = [
                {"step": "Projektowanie konstrukcji CAD", "role": "Projektowanie CAD / Inżynieria", "hours": 4.0},
                {"step": "Generowanie ścieżek CAM & obróbka CNC", "role": "Programowanie i Obróbka CNC", "hours": 6.0},
                {"step": "Spawanie ramy nośnej", "role": "Spawanie i Ślusarstwo", "hours": 3.0},
                {"step": "Montaż mechaniczny podzespołów", "role": "Montaż i Pasowanie", "hours": 5.0},
                {"step": "Kontrola metrologiczna i odbiór jakości", "role": "Kontrola Jakości i Metrologia", "hours": 2.0}
            ]
            st.rerun()
            
        st.write("---")
        markup_pct = st.number_input("Narzut / Marża zysku na robociznę (%):", min_value=0.0, value=15.0, step=1.0)
        markup_val = total_labor_cost * (markup_pct / 100.0)
        final_labor_cost = total_labor_cost + markup_val
        
        st.markdown(f"""
        <div class='card'>
            <table style='width:100%; border: none;'>
                <tr style='font-size: 1.1rem;'>
                    <td>Łączna suma roboczogodzin (h):</td>
                    <td style='text-align: right; font-weight: bold;'>{total_hours:.1f} h</td>
                </tr>
                <tr style='font-size: 1.1rem;'>
                    <td>Koszt robocizny netto (koszt własny):</td>
                    <td style='text-align: right; font-weight: bold;'>{total_labor_cost:.2f} PLN</td>
                </tr>
                <tr>
                    <td>Narzut marży ({markup_pct}%):</td>
                    <td style='text-align: right;'>{markup_val:.2f} PLN</td>
                </tr>
                <tr style='background-color: #DCE6F1; border-top: 2px solid #1F497D; font-weight: bold;'>
                    <td style='font-size: 1.3rem; color: #1F497D;'>ŁĄCZNY KOSZT ROBOCIZNY:</td>
                    <td style='text-align: right; font-size: 1.8rem; color: #1F497D;'>{final_labor_cost:.2f} PLN</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
