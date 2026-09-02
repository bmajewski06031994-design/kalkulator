import streamlit as st
import pandas as pd
import numpy as np
import math

# Set Page Config
st.set_page_config(
    page_title="Engineering Toolbox v6.0",
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
</style>
""", unsafe_allow_html=True)

# --- REFERENCE DATABASES ---

# 1. Materials Density Database
MATERIALS_DB = {
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
    "PTFE (Teflon)": {"group": "Tworzywa sztuczne", "density_g": 2.20, "density_kg": 2200, "price_kg": 45.00, "young_gpa": 0.5, "desc": "Uszczelnienia chemiczne, ślizgi niskotarciowe"}
}

# 2. Fasteners Nuts (DIN 934) and Washers (DIN 125) Database
FASTENERS_DB = {
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

# 3. Bolt Weights (DIN 933 Approximations in kg/1000pcs)
BOLT_WEIGHTS_DB = {
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

# 4. Bolt Pricing (DIN 933 Approximations in PLN/1000pcs)
BOLT_PRICES_DB = {k: round(v * 12.5, 2) for k, v in BOLT_WEIGHTS_DB.items()}

# 5. Thread Parameters Database (M3 to M48)
THREAD_PARAMS_DB = {
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

# 6. Steel Strength & Properties Database
STEEL_PROPERTIES_DB = {
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

# 7. Labor Roles Rates
LABOR_RATES = {
    "Projektowanie CAD / Inżynieria": 150,
    "Programowanie i Obróbka CNC": 180,
    "Spawanie i Ślusarstwo": 120,
    "Montaż i Pasowanie": 100,
    "Kontrola Jakości i Metrologia": 110,
    "Nadzór Inżynieryjny": 160,
    "Prace Pomocnicze / Przygotowanie": 70
}

# --- NAVIGATION SIDEBAR ---
st.sidebar.markdown("<h2 style='text-align: center; color: #1F497D;'>MENU NAWIGACJI</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "Wybierz moduł:",
    [
        "📊 Pulpit Główny",
        "⚖️ 1. Kalkulator Masy & Surowca",
        "🔩 2. Elementy Złączne & Costing",
        "🔧 3. Parametry Montażowe",
        "🪚 4. Kalkulator Cięcia i Strat",
        "🔬 5. Właściwości i Klasy Stali",
        "⏱️ 6. Kalkulator Czasu Pracy"
    ]
)

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; font-size: 0.8rem; color: #777;'>ENGINEERING TOOLBOX v6.0<br>SaaS Pro Premium Bundle<br>© 2026 Wszelkie prawa zastrzeżone</div>", unsafe_allow_html=True)


# --- PAGES IMPLEMENTATION ---

# PAGE 0: PULPIT GŁÓWNY
if menu == "📊 Pulpit Główny":
    st.markdown("<div class='main-header'>ENGINEERING TOOLBOX v6.0</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zintegrowany Portal Techniczno-Kosztorysowy w czasie rzeczywistym</div>", unsafe_allow_html=True)
    
    st.markdown("""
    Witaj w nowej, zoptymalizowanej wersji **Engineering Toolbox v6.0**! Jest to nowoczesna aplikacja webowa (SaaS) oparta na silniku Streamlit, 
    która w 100% odzwierciedla dane normatywne i zaawansowane formuły matematyczne zawarte w wersji arkuszowej (Excel v10).
    
    **Najnowsza odsłona v6.0 wprowadza:**
    *   **🪚 Nowy Kalkulator Cięcia i Strat (Scrap Estimator):** Pozwala na precyzyjne wyliczenie zapotrzebowania na sztangi profili (np. 6 m) oraz masę i koszt powstających odpadów (remnants i rzazu tarczy).
    *   **🔬 Nową Kartę Właściwości i Klas Stali:** Interaktywną ściągawkę z twardością (HV, HB, Rockwell) oraz dopuszczalnym składem chemicznym i mechanicznym łączników ze stali węglowej i nierdzewnej (A2/A4).
    *   **🔩 Rozszerzoną Bazę Elementów Złącznych:** Pełne wsparcie dla wyceny ciężkich łączników konstrukcyjnych **aż do rozmiaru M48**!
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h4>🎨 LEGENDA OZNACZEŃ KOLORYSTYCZNYCH</h4>"
                    "<ul>"
                    "<li><b>Elementy kontrolne i suwaki:</b> Służą do wprowadzania danych geometrycznych i wyboru opcji.</li>"
                    "<li><b>Zielone bloki informacji:</b> Reprezentują automatyczne wyniki obliczeń oraz statusy bezpieczeństwa.</li>"
                    "<li><b>Panele alertów:</b> Sygnalizują potencjalne błędy bądź błędy parametrów wejściowych.</li>"
                    "</ul></div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='card'><h4>📈 KORZYŚCI DLA TWÓJ BIZNES PASYWNY</h4>"
                    "<ul>"
                    "<li><b>Wersja mobilna:</b> Klienci mogą korzystać z narzędzia na smartfonie bezpośrednio na warsztacie.</li>"
                    "<li><b>Automatyzacja wycen:</b> Umożliwia błyskawiczne przygotowanie ofert kosztorysowych dla klientów końcowych.</li>"
                    "<li><b>Baza bez makr:</b> Pełna niezależność i bezproblemowe działanie na dowolnej przeglądarce.</li>"
                    "</ul></div>", unsafe_allow_html=True)

# PAGE 1: KALKULATOR MASY & SUROWCA
elif menu == "⚖️ 1. Kalkulator Masy & Surowca":
    st.markdown("<div class='main-header'>⚖️ 1. KALKULATOR MASY I KOSZTÓW MATERIAŁU</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Obliczanie parametrów fizycznych oraz kosztorys surowcowy profili hutniczych</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wprowadź dane")
        profile = st.selectbox("Rodzaj profilu:", ["Blacha/Płaskownik", "Pręt okrągły", "Rura okrągła", "Profil kwadratowy", "Profil prostokątny", "Pręt sześciokątny"])
        material = st.selectbox("Gatunek materiału:", list(MATERIALS_DB.keys()))
        
        # Geometry fields based on profile selection
        dim1, dim2, wall, length = 0.0, 0.0, 0.0, 0.0
        
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
            dim1 = st.number_input("Rozmiar pod klucz s (mm):", min_value=0.1, value=19.0, step=1.0)
            
        length = st.number_input("Długość L (mm):", min_value=1.0, value=1000.0, step=100.0)
        qty = st.number_input("Ilość sztuk:", min_value=1, value=10, step=1)
        
        # Price adjustments
        mat_data = MATERIALS_DB[material]
        sug_price = mat_data["price_kg"]
        custom_price = st.number_input("Własna cena (PLN/kg) - pozostaw 0 aby użyć ceny sugerowanej:", min_value=0.0, value=0.0, step=0.5)
        eff_price = custom_price if custom_price > 0 else sug_price

    with col_out:
        st.subheader("Wyniki obliczeń")
        
        # Volume Calculation (cm3)
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
            vol = (0.866 * (dim1**2) * length) / 1000.0
            
        density_g = mat_data["density_g"]
        single_mass = (vol * density_g) / 1000.0 # kg
        total_mass = single_mass * qty
        total_cost = total_mass * eff_price
        
        st.info(f"**Gatunek materiału:** {material} ({mat_data['group']})  \n"
                f"**Gęstość:** {mat_data['density_kg']} kg/m³  \n"
                f"**Zastosowanie:** {mat_data['desc']}")
        
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 0.9rem; color: #555;'>Masa pojedynczego elementu</div>
            <div class='metric-value'>{single_mass:.3f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Masa całkowita partii ({qty} szt.)</div>
            <div class='metric-value'>{total_mass:.2f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Efektywna cena surowca</div>
            <div class='metric-value'>{eff_price:.2f} PLN/kg</div>
            <br>
            <div style='font-size: 1rem; font-weight: bold; color: #1F497D;'>KOSZT CAŁKOWITY MATERIAŁU</div>
            <div style='font-size: 2.2rem; font-weight: bold; color: #2F5496;'>{total_cost:.2f} PLN</div>
        </div>
        """, unsafe_allow_html=True)

# PAGE 2: ELEMENTY ZŁĄCZNE & COSTING
elif menu == "🔩 2. Elementy Złączne & Costing":
    st.markdown("<div class='main-header'>🔩 2. KALKULATOR ELEMENTÓW ZŁĄCZNYCH I WYCENA</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Costing, ciężar i konfiguracja zestawów śrubowych DIN 933 / 934 / 125</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Konfiguracja zestawu")
        size = st.selectbox("Rozmiar nominalny gwintu:", list(FASTENERS_DB.keys()), index=4) # Default M8
        
        # Filter available lengths for selected size
        avail_lengths = [int(k.split("-")[1]) for k in BOLT_WEIGHTS_DB.keys() if k.split("-")[0] == size]
        length = st.selectbox("Długość śruby L (mm) wg DIN 933:", sorted(avail_lengths), index=2 if len(avail_lengths)>2 else 0)
        
        material_class = st.selectbox("Klasa / Materiał elementu:", [
            "Klasa 8.8 (Stal węg. ocynk) [Mnożnik: 1.0x]",
            "Klasa 10.9 (Stal węg. ocynk) [Mnożnik: 1.3x]",
            "Klasa 12.9 (Czarna / Socket) [Mnożnik: 1.6x]",
            "Stal nierdzewna A2 (304) [Mnożnik: 2.5x]",
            "Stal kwasoodporna A4 (316) [Mnożnik: 3.8x]"
        ])
        
        qty = st.number_input("Ilość kompletnych zestawów (szt.):", min_value=1, value=1000, step=100)
        add_nut = st.selectbox("Dodaj nakrętkę DIN 934?", ["Tak", "Nie"], index=0)
        num_washers = st.selectbox("Ilość podkładek DIN 125:", [0, 1, 2], index=2)

    with col_out:
        st.subheader("Wyniki obliczeń kosztów i masy")
        
        # Multipliers mapping
        multiplier = 1.0
        if "10.9" in material_class: multiplier = 1.3
        elif "12.9" in material_class: multiplier = 1.6
        elif "A2" in material_class: multiplier = 2.5
        elif "A4" in material_class: multiplier = 3.8
        
        # Get base weights (kg / 1000 pcs)
        bolt_key = f"{size}-{length}"
        bolt_weight = BOLT_WEIGHTS_DB.get(bolt_key, 0.0)
        bolt_price = BOLT_PRICES_DB.get(bolt_key, 0.0)
        
        fdata = FASTENERS_DB[size]
        nut_weight = fdata["nut_weight"] if add_nut == "Tak" else 0.0
        nut_price = fdata["nut_price"] if add_nut == "Tak" else 0.0
        
        washer_weight = fdata["washer_weight"] * num_washers
        washer_price = fdata["washer_price"] * num_washers
        
        # Totals for single set
        single_set_weight_g = bolt_weight + nut_weight + washer_weight # grams
        total_party_mass_kg = (single_set_weight_g * qty) / 1000.0
        
        # Cost calculations
        cost_bolt_1000 = bolt_price * multiplier
        cost_nut_1000 = nut_price * multiplier
        cost_washer_1000 = washer_price * multiplier
        
        total_set_cost_1000 = cost_bolt_1000 + cost_nut_1000 + cost_washer_1000
        total_cost_pln = (total_set_cost_1000 * qty) / 1000.0
        
        st.markdown(f"""
        <div class='card'>
            <div style='font-size: 0.9rem; color: #555;'>Masa jednego kompletnego zestawu</div>
            <div class='metric-value'>{single_set_weight_g:.2f} g</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Łączna waga całej partii ({qty} szt.)</div>
            <div class='metric-value'>{total_party_mass_kg:.2f} kg</div>
            <br>
            <div style='font-size: 0.9rem; color: #555;'>Mnożnik materiałowy ceny</div>
            <div class='metric-value'>{multiplier:.1f}x</div>
            <br>
            <div style='font-size: 1rem; font-weight: bold; color: #1F497D;'>ŁĄCZNY KOSZT ELEMENTÓW ZŁĄCZNYCH</div>
            <div style='font-size: 2.2rem; font-weight: bold; color: #2F5496;'>{total_cost_pln:.2f} PLN</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Details breakdown
        with st.expander("Zobacz zestawienie składowe i rozbicie wagowo-cenowe"):
            df_breakdown = pd.DataFrame({
                "Element": ["Śruba DIN 933", "Nakrętka DIN 934", "Podkładki DIN 125"],
                "Masa 1 szt. (g)": [bolt_weight, fdata["nut_weight"], fdata["washer_weight"]],
                "Masa w zest. (g)": [bolt_weight, nut_weight, washer_weight],
                "Masa partii (kg)": [
                    round((bolt_weight * qty) / 1000.0, 3),
                    round((nut_weight * qty) / 1000.0, 3),
                    round((washer_weight * qty) / 1000.0, 3)
                ],
                "Cena baz./1000szt": [bolt_price, nut_price, washer_price],
                "Cena ef./1000szt": [cost_bolt_1000, cost_nut_1000, cost_washer_1000]
            })
            st.dataframe(df_breakdown, hide_index=True)

# PAGE 3: PARAMETRY MONTAŻOWE
elif menu == "🔧 3. Parametry Montażowe":
    st.markdown("<div class='main-header'>🔧 3. PARAMETRY MONTAŻOWE GWINTÓW</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Dobór wierteł pod gwinty, otwory przejściowe oraz momenty dokręcania śrub</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Parametry gwintu")
        size = st.selectbox("Rozmiar śruby / gwintu:", list(THREAD_PARAMS_DB.keys()), index=4) # Default M8
        class_bolt = st.selectbox("Klasa wytrzymałości śruby:", ["8.8", "10.9", "12.9"])
        
    with col_out:
        st.subheader("Zalecenia techniczne")
        tdata = THREAD_PARAMS_DB[size]
        
        # Determine torques & preloads
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
            preload = tdata["p_10_9"] * 1.2
            
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
                    <td style='font-weight: bold;'>Otwór przejściowy dokładny:</td>
                    <td style='text-align: right;'>Ø {tdata['fine_hole']:.1f} mm</td>
                </tr>
                <tr>
                    <td style='font-weight: bold;'>Otwór przejściowy średni:</td>
                    <td style='text-align: right;'>Ø {tdata['medium_hole']:.1f} mm</td>
                </tr>
                <tr style='background-color: #DCE6F1;'>
                    <td style='font-weight: bold; color: #1F497D;'>Zalecany moment dokręcania (klasa {class_bolt}):</td>
                    <td style='text-align: right; font-size: 1.4rem; font-weight: bold; color: #1F497D;'>{torque:.2f} Nm</td>
                </tr>
                <tr>
                    <td style='font-weight: bold;'>Zalecana siła napięcia wstępnego Fm:</td>
                    <td style='text-align: right;'>{preload:.1f} kN</td>
                </tr>
            </table>
            <div style='font-size: 0.8rem; color: #777; margin-top: 1rem; font-style: italic;'>
                * Wskazówka: Obliczenia momentu dokręcania i napięcia wstępnego oszacowano dla współczynnika tarcia łba i gwintu μ=0.14 (stal węglowa czarna, nieoliwiona).
            </div>
        </div>
        """, unsafe_allow_html=True)

# PAGE 4: KALKULATOR CIĘCIA I STRAT (NEW)
elif menu == "🪚 4. Kalkulator Cięcia i Strat":
    st.markdown("<div class='main-header'>🪚 4. KALKULATOR CIĘCIA I STRAT MATERIAŁOWYCH</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Zoptymalizowane cięcie profili hutniczych, zapotrzebowanie na sztangi i koszt odpadów</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wprowadź dane cięcia")
        stock_len = st.number_input("Długość profilu handlowego (mm) (np. sztanga 6m):", min_value=100.0, value=6000.0, step=500.0)
        cut_len = st.number_input("Długość uciętego elementu (mm):", min_value=1.0, value=450.0, step=10.0)
        qty_req = st.number_input("Wymagana ilość sztuk (szt.):", min_value=1, value=50, step=5)
        kerf = st.number_input("Szerokość rzazu piły (grubość tarczy tnącej) (mm):", min_value=0.0, value=3.0, step=0.5)
        weight_per_m = st.number_input("Masa 1 metra profilu (kg/m):", min_value=0.01, value=4.5, step=0.5)
        price_per_kg = st.number_input("Cena profilu za kg (PLN/kg):", min_value=0.1, value=6.50, step=0.5)

    with col_out:
        st.subheader("Wyniki optymalizacji rozkroju")
        
        # Calculate pieces per bar
        if cut_len <= 0 or stock_len < cut_len:
            pcs_per_bar = 0
            bars_req = 0
            remnant_single = stock_len
            total_waste_mm = 0
            yield_pct = 0.0
        else:
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
                    <td style='font-weight: bold; color: #27AE60;'>Sztuk z jednej sztangi:</td>
                    <td style='text-align: right; font-weight: bold; color: #27AE60;'>{pcs_per_bar} szt.</td>
                </tr>
                <tr style='font-size: 1.1rem; background-color: #DCE6F1;'>
                    <td style='font-weight: bold; color: #1F497D;'>Wymagana ilość sztang (szt.):</td>
                    <td style='text-align: right; font-weight: bold; color: #1F497D;'>{bars_req} szt. (łącznie {(bars_req*stock_len/1000.0):.1f} mb)</td>
                </tr>
                <tr>
                    <td>Użyteczny odpad (końcówka) z 1 sztangi:</td>
                    <td style='text-align: right;'>{remnant_single:.1f} mm</td>
                </tr>
                <tr>
                    <td>Łączna długość strat (odpad + rzaz):</td>
                    <td style='text-align: right;'>{total_waste_mm:.0f} mm</td>
                </tr>
                <tr style='font-weight: bold;'>
                    <td>Współczynnik wykorzystania materiału:</td>
                    <td style='text-align: right; color: #27AE60;'>{yield_pct:.2f}%</td>
                </tr>
                <tr style='border-top: 1px solid #ccc;'>
                    <td>Masa zakupionego materiału:</td>
                    <td style='text-align: right;'>{total_bought_mass:.2f} kg</td>
                </tr>
                <td>Masa gotowych wyrobów:</td>
                <td style='text-align: right;'>{total_useful_mass:.2f} kg</td>
                </tr>
                <tr>
                    <td>Masa całkowita strat:</td>
                    <td style='text-align: right; color: #C0392B;'>{total_waste_mass:.2f} kg</td>
                </tr>
                <tr style='border-top: 2px solid #2F5496; font-size: 1.2rem; font-weight: bold; color: #1F497D;'>
                    <td>KOSZT ZAKUPU SUROWCA:</td>
                    <td style='text-align: right; font-size: 1.5rem;'>{total_bought_cost:.2f} PLN</td>
                </tr>
                <tr style='font-size: 1.1rem; font-weight: bold; color: #C0392B;'>
                    <td>KOSZT STRAT MATERIAŁOWYCH:</td>
                    <td style='text-align: right;'>{total_waste_cost:.2f} PLN</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# PAGE 5: WŁAŚCIWOŚCI I KLASY STALI (NEW)
elif menu == "🔬 5. Właściwości i Klasy Stali":
    st.markdown("<div class='main-header'>🔬 5. WŁAŚCIWOŚCI I KLASY WYTRZYMAŁOŚCI STALI</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Właściwości mechaniczne, twardość oraz graniczne składy chemiczne stali i łączników</div>", unsafe_allow_html=True)
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Wybór gatunku lub klasy")
        steel_grade = st.selectbox("Klasa śruby lub gatunek stali:", list(STEEL_PROPERTIES_DB.keys()), index=4) # Default 8.8
        
    with col_out:
        st.subheader("Parametry mechaniczne i chemiczne")
        sdata = STEEL_PROPERTIES_DB[steel_grade]
        
        is_stainless = "A2" in steel_grade or "A4" in steel_grade
        steel_type = "Austenityczna Stal Nierdzewna" if is_stainless else "Stal Węglowa / Stopowa do ulepszania cieplnego"
        
        st.info(f"**Typ materiału:** {steel_type}  \n"
                f"Zgodność z normami: **DIN EN ISO 3506** (stale nierdzewne) lub **DIN EN ISO 898** (stale węglowe).")
        
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
                    <td>Twardość Vickersa (min - max):</td>
                    <td style='text-align: right;'>{sdata['vickers']} HV</td>
                </tr>
                <tr>
                    <td>Twardość Brinella (min - max):</td>
                    <td style='text-align: right;'>{sdata['brinell']} HB</td>
                </tr>
                <tr>
                    <td>Twardość Rockwella (min - max):</td>
                    <td style='text-align: right;'>{sdata['rockwell']}</td>
                </tr>
                <tr style='border-top: 1px solid #ccc; font-weight: bold;'>
                    <td colspan='2' style='padding-top: 0.5rem; color: #555;'>Graniczny skład chemiczny (limity %):</td>
                </tr>
                <tr>
                    <td>Zawartość Węgla C (max %):</td>
                    <td style='text-align: right;'>{sdata['c_max']:.3f}%</td>
                </tr>
                <tr>
                    <td>Zawartość Fosforu P (max %):</td>
                    <td style='text-align: right;'>{sdata['p_max']}%</td>
                </tr>
                <tr>
                    <td>Zawartość Siarki S (max %):</td>
                    <td style='text-align: right;'>{sdata['s_max']}%</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

# PAGE 6: WYCENA CZASU PRACY
elif menu == "⏱️ 6. Kalkulator Czasu Pracy":
    st.markdown("<div class='main-header'>⏱️ 6. KALKULATOR CZASU PRACY & ROBOCIZNY</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Dynamiczne wycenianie procesów technologicznych i kosztów pracy ludzkiej</div>", unsafe_allow_html=True)
    
    # We use st.session_state to store custom operations dynamically
    if "operations" not in st.session_state:
        st.session_state["operations"] = [
            {"step": "Projektowanie konstrukcji", "role": "Projektowanie CAD / Inżynieria", "hours": 4.0},
            {"step": "Obróbka CNC korpusu", "role": "Programowanie i Obróbka CNC", "hours": 6.0},
            {"step": "Spawanie ramy", "role": "Spawanie i Ślusarstwo", "hours": 3.0},
            {"step": "Montaż końcowy", "role": "Montaż i Pasowanie", "hours": 5.0},
            {"step": "Kontrola metrologiczna", "role": "Kontrola Jakości i Metrologia", "hours": 2.0}
        ]
        
    col_dict, col_calc = st.columns([1, 2])
    
    with col_dict:
        st.subheader("1. Stawki godzinowe stanowisk")
        st.info("Poniższe komórki reprezentują stawki w PLN/h – możesz je edytować, by zaktualizować cały kalkulator!")
        rates = {}
        for role, default_rate in LABOR_RATES.items():
            rates[role] = st.number_input(f"{role} (PLN/h):", min_value=1.0, value=float(default_rate), step=5.0)
            
    with col_calc:
        st.subheader("2. Harmonogram operacji technologicznych")
        
        # Add new operation inputs
        with st.expander("➕ Dodaj nową operację / krok"):
            new_step = st.text_input("Nazwa kroku / operacji:", placeholder="np. Malowanie proszkowe")
            new_role = st.selectbox("Przypisana rola/stanowisko:", list(LABOR_RATES.keys()))
            new_hours = st.number_input("Czas trwania (h):", min_value=0.1, value=1.0, step=0.5)
            
            if st.button("Dodaj krok do listy"):
                if new_step:
                    st.session_state["operations"].append({"step": new_step, "role": new_role, "hours": new_hours})
                    st.toast("Pomyślnie dodano operację!", icon="✅")
                else:
                    st.error("Wpisz nazwę operacji przed dodaniem!")
                    
        # List of current operations
        st.write("---")
        st.write("**Lista operacji w projekcie:**")
        
        total_hours = 0.0
        total_labor_cost = 0.0
        
        display_list = []
        for i, op in enumerate(st.session_state["operations"]):
            rate = rates[op["role"]]
            cost = op["hours"] * rate
            total_hours += op["hours"]
            total_labor_cost += cost
            display_list.append({
                "Nr": i + 1,
                "Nazwa operacji": op["step"],
                "Stanowisko": op["role"],
                "Czas (h)": op["hours"],
                "Stawka (PLN/h)": rate,
                "Koszt (PLN)": cost
            })
            
        st.dataframe(pd.DataFrame(display_list), hide_index=True, use_container_width=True)
        
        if st.button("🗑️ Resetuj listę do przykładowych kroków"):
            st.session_state["operations"] = [
                {"step": "Projektowanie konstrukcji", "role": "Projektowanie CAD / Inżynieria", "hours": 4.0},
                {"step": "Obróbka CNC korpusu", "role": "Programowanie i Obróbka CNC", "hours": 6.0},
                {"step": "Spawanie ramy", "role": "Spawanie i Ślusarstwo", "hours": 3.0},
                {"step": "Montaż końcowy", "role": "Montaż i Pasowanie", "hours": 5.0},
                {"step": "Kontrola metrologiczna", "role": "Kontrola Jakości i Metrologia", "hours": 2.0}
            ]
            st.rerun()
            
        # Markup & Summary
        st.write("---")
        markup_pct = st.number_input("Dodatkowa marża / narzut zysku (%):", min_value=0.0, value=15.0, step=1.0)
        markup_val = total_labor_cost * (markup_pct / 100.0)
        final_labor_cost = total_labor_cost + markup_val
        
        st.markdown(f"""
        <div class='card'>
            <table style='width:100%; border: none;'>
                <tr style='font-size: 1.1rem;'>
                    <td>Suma roboczogodzin (h):</td>
                    <td style='text-align: right; font-weight: bold;'>{total_hours:.1f} h</td>
                </tr>
                <tr style='font-size: 1.1rem;'>
                    <td>Koszt robocizny netto:</td>
                    <td style='text-align: right; font-weight: bold;'>{total_labor_cost:.2f} PLN</td>
                </tr>
                <tr>
                    <td>Wartość narzutu ({markup_pct}%):</td>
                    <td style='text-align: right;'>{markup_val:.2f} PLN</td>
                </tr>
                <tr style='background-color: #DCE6F1; border-top: 2px solid #1F497D; font-weight: bold;'>
                    <td style='font-size: 1.3rem; color: #1F497D;'>ŁĄCZNY KOSZT ROBOCIZNY:</td>
                    <td style='text-align: right; font-size: 1.8rem; color: #1F497D;'>{final_labor_cost:.2f} PLN</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
