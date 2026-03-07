"""
pipeline.py — UBA Methodological Convention 4.0 (December 2025)
Handbook on Environmental Value Factors

Hard-coded value factor data from all tables in the handbook.
Public API: run_table(key)  →  loads data  →  saves CSV

All monetary values are in EUR_2025 (price level of 2025, inflation taken
into account up to end of 2024, per Destatis 2025).
"""

import logging
import csv
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

import config

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Table 1 — GHG value factors  (Chapter 2, p. 11)
# Unit: EUR_2025 / t GHG
# Source: adapted GIVE model (Anthoff 2025), equity-weighted
# ──────────────────────────────────────────────────────────────────────────────
_GHG_DATA = [
    # (year, co2_0pct, co2_1pct, ch4_0pct, ch4_1pct, n2o_0pct, n2o_1pct)
    (2020,    935,    310,   7_770,  4_580,  260_900, 105_700),
    (2025,    990,    345,   9_220,  5_800,  282_300, 118_700),
    (2026,  1_000,    350,   9_510,  6_040,  286_600, 121_300),
    (2027,  1_010,    355,   9_790,  6_290,  290_900, 123_900),
    (2028,  1_020,    365,  10_080,  6_530,  295_200, 126_500),
    (2029,  1_040,    370,  10_370,  6_780,  299_500, 129_100),
    (2030,  1_050,    375,  10_660,  7_020,  303_800, 131_700),
    (2040,  1_150,    440,  14_200,  9_950,  339_900, 154_500),
    (2050,  1_240,    485,  16_580, 12_100,  355_400, 167_800),
]


def _build_ghg_rows() -> list[dict]:
    rows = []
    for rec in _GHG_DATA:
        year, co2_0, co2_1, ch4_0, ch4_1, n2o_0, n2o_1 = rec
        base = {"emission_year": year, "source_table": "Table 1",
                "unit": "EUR_2025/t", "chapter": 2}
        rows.append({**base, "substance": "CO2_CO2eq", "prtp_pct": 0, "value_factor": co2_0})
        rows.append({**base, "substance": "CO2_CO2eq", "prtp_pct": 1, "value_factor": co2_1})
        rows.append({**base, "substance": "CH4",       "prtp_pct": 0, "value_factor": ch4_0})
        rows.append({**base, "substance": "CH4",       "prtp_pct": 1, "value_factor": ch4_1})
        rows.append({**base, "substance": "N2O",       "prtp_pct": 0, "value_factor": n2o_0})
        rows.append({**base, "substance": "N2O",       "prtp_pct": 1, "value_factor": n2o_1})
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 2–4 — Air pollutant value factors  (Chapter 3, pp. 18–20)
# Unit: EUR_2025 / t emission
# Source: van der Kamp et al. (2024), EcoSenseWeb v1.3, HRAPIE / Chen & Hoek (2020)
# ──────────────────────────────────────────────────────────────────────────────
# Table 2: Average VF for unknown sources
# Columns: health, crop, material_building, total
_AIR_TABLE2 = {
    # substance: (health, crop, material_building, total)
    "PM2.5":   (128_200,    0,    0, 128_200),
    "PMcoarse": (  1_690,   0,    0,   1_690),
    "PM10":    ( 90_200,    0,    0,  90_200),
    "NOx":     ( 36_000, 1_530,  210,  37_740),
    "SO2":     ( 34_500,  -140,  965,  35_325),
    "NMVOC":   (    525, 1_450,    0,   1_975),
    "NH3":     ( 30_400,  -125,    0,  30_275),
}

# Table 3: Differentiated VF — health impacts only, by source type
# Key: (sector, surroundings, emission_height_m)
# sector: "power_station" | "industry" | "small_scale"
# surroundings: "unspecified" | "unknown" | "city" | "town"
# emission_height: ">100" | "0-100" | "0-20" | "20-100"
_AIR_TABLE3 = {
    # (sector,          surroundings,  height):  {substance: value}
    ("power_station",  "unspecified",  ">100"):  {
        "PM2.5": 66_900, "PMcoarse": 745, "PM10": 47_000,
        "NOx": 28_800, "SO2": 31_800, "NMVOC": 530, "NH3": 33_300},
    ("industry",       "unknown",     "0-100"):  {
        "PM2.5": 137_400, "PMcoarse": 1_870, "PM10": 96_700,
        "NOx": 38_100, "SO2": 35_600, "NMVOC": 535, "NH3": 33_200},
    ("industry",       "city",        "0-20"):   {
        "PM2.5": 245_900, "PMcoarse": 3_350, "PM10": 173_100,
        "NOx": 38_100, "SO2": 35_600, "NMVOC": 535, "NH3": 33_200},
    ("industry",       "city",        "20-100"): {
        "PM2.5": 138_700, "PMcoarse": 1_890, "PM10": 97_700,
        "NOx": 38_100, "SO2": 35_600, "NMVOC": 535, "NH3": 33_200},
    ("industry",       "town",        "0-20"):   {
        "PM2.5": 170_300, "PMcoarse": 2_320, "PM10": 119_900,
        "NOx": 38_100, "SO2": 35_600, "NMVOC": 535, "NH3": 33_200},
    ("industry",       "town",        "20-100"): {
        "PM2.5": 138_700, "PMcoarse": 1_890, "PM10": 97_700,
        "NOx": 38_100, "SO2": 35_600, "NMVOC": 535, "NH3": 33_200},
    ("small_scale",    "unknown",     "0-100"):  {
        "PM2.5": 130_300, "PMcoarse": 1_690, "PM10": 91_700,
        "NOx": 39_400, "SO2": 35_900, "NMVOC": 530, "NH3": 33_100},
    ("small_scale",    "city",        "0-20"):   {
        "PM2.5": 233_200, "PMcoarse": 3_030, "PM10": 164_100,
        "NOx": 39_400, "SO2": 35_900, "NMVOC": 530, "NH3": 33_100},
    ("small_scale",    "city",        "20-100"): {
        "PM2.5": 131_600, "PMcoarse": 1_710, "PM10": 92_600,
        "NOx": 39_400, "SO2": 35_900, "NMVOC": 530, "NH3": 33_100},
    ("small_scale",    "town",        "0-20"):   {
        "PM2.5": 161_500, "PMcoarse": 2_100, "PM10": 113_700,
        "NOx": 39_400, "SO2": 35_900, "NMVOC": 530, "NH3": 33_100},
    ("small_scale",    "town",        "20-100"): {
        "PM2.5": 131_600, "PMcoarse": 1_710, "PM10": 92_600,
        "NOx": 39_400, "SO2": 35_900, "NMVOC": 530, "NH3": 33_100},
}

# Table 4: VF from road traffic by surroundings — health impacts only
# PM10_abrasion: tires/brakes/roads (50% PM2.5 + 50% PMcoarse assumption)
_AIR_TABLE4 = {
    # surroundings: {substance: value}
    "unknown":  {"PM2.5": 125_900, "PMcoarse": 1_600, "PM10_abrasion": 63_800,
                 "NOx": 37_100, "SO2": 34_600, "NMVOC": 525, "NH3": 32_100},
    "urban":    {"PM2.5": 511_600, "PMcoarse": 7_800, "PM10_abrasion": 259_700,
                 "NOx": 37_100, "SO2": 34_600, "NMVOC": 525, "NH3": 32_100},
    "suburban": {"PM2.5": 147_500, "PMcoarse": 1_940, "PM10_abrasion": 74_700,
                 "NOx": 37_100, "SO2": 34_600, "NMVOC": 525, "NH3": 32_100},
    "rural":    {"PM2.5":  86_600, "PMcoarse":   960, "PM10_abrasion": 43_780,
                 "NOx": 37_100, "SO2": 34_600, "NMVOC": 525, "NH3": 32_100},
}


def _build_air_rows() -> list[dict]:
    rows = []
    # Table 2
    for substance, (health, crop, matbuild, total) in _AIR_TABLE2.items():
        rows.append({
            "source_table": "Table 2", "chapter": 3,
            "context": "unknown_source", "sector": "", "surroundings": "",
            "emission_height_m": "", "substance": substance,
            "impact_component": "health",    "value_factor": health, "unit": "EUR_2025/t",
        })
        rows.append({
            "source_table": "Table 2", "chapter": 3,
            "context": "unknown_source", "sector": "", "surroundings": "",
            "emission_height_m": "", "substance": substance,
            "impact_component": "crop",      "value_factor": crop,   "unit": "EUR_2025/t",
        })
        rows.append({
            "source_table": "Table 2", "chapter": 3,
            "context": "unknown_source", "sector": "", "surroundings": "",
            "emission_height_m": "", "substance": substance,
            "impact_component": "material_building", "value_factor": matbuild, "unit": "EUR_2025/t",
        })
        rows.append({
            "source_table": "Table 2", "chapter": 3,
            "context": "unknown_source", "sector": "", "surroundings": "",
            "emission_height_m": "", "substance": substance,
            "impact_component": "total",     "value_factor": total,  "unit": "EUR_2025/t",
        })
    # Table 3
    for (sector, surroundings, height), vals in _AIR_TABLE3.items():
        for substance, vf in vals.items():
            rows.append({
                "source_table": "Table 3", "chapter": 3,
                "context": "stationary_combustion",
                "sector": sector, "surroundings": surroundings,
                "emission_height_m": height, "substance": substance,
                "impact_component": "health", "value_factor": vf, "unit": "EUR_2025/t",
            })
    # Table 4
    for surroundings, vals in _AIR_TABLE4.items():
        for substance, vf in vals.items():
            rows.append({
                "source_table": "Table 4", "chapter": 3,
                "context": "road_traffic",
                "sector": "transport", "surroundings": surroundings,
                "emission_height_m": "0-3", "substance": substance,
                "impact_component": "health", "value_factor": vf, "unit": "EUR_2025/t",
            })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Table 5 — Electricity generation value factors  (Chapter 4, p. 24)
# Unit: EUR-cent_2025 / kWh_el  (incl. upstream supply chains)
# Source: Walther et al. (2024b), van der Kamp et al. (2024), Anthoff (2025)
# ──────────────────────────────────────────────────────────────────────────────
_ELECTRICITY_DATA = [
    # (source, air_pollutants, ghg_1pct, ghg_0pct, total_1pct, total_0pct)
    ("German_electricity_mix_2024",  2.23, 11.56, 32.53, 13.79, 34.76),
    ("Lignite",                      3.93, 35.89,103.34, 39.82,107.27),
    ("Hard_coal",                    4.82, 29.08, 82.26, 33.90, 87.09),
    ("Natural_gas",                  1.18, 14.72, 41.23, 15.90, 42.41),
    ("Oil",                          8.94, 28.91, 83.06, 37.85, 92.00),
    ("Biomass",                      8.08,  7.45, 16.48, 15.54, 24.56),
    ("Photovoltaics",                0.82,  1.90,  5.36,  2.72,  6.18),
    ("Hydropower",                   0.08,  0.13,  0.36,  0.21,  0.43),
    ("Wind_energy",                  0.37,  0.56,  1.58,  0.93,  1.95),
]


def _build_electricity_rows() -> list[dict]:
    rows = []
    for rec in _ELECTRICITY_DATA:
        src, ap, ghg1, ghg0, tot1, tot0 = rec
        base = {"source_table": "Table 5", "chapter": 4,
                "energy_source": src, "unit": "EUR-cent_2025/kWh_el"}
        rows.append({**base, "component": "air_pollutants", "prtp_pct": "",  "value_factor": ap})
        rows.append({**base, "component": "greenhouse_gases","prtp_pct": 1,  "value_factor": ghg1})
        rows.append({**base, "component": "greenhouse_gases","prtp_pct": 0,  "value_factor": ghg0})
        rows.append({**base, "component": "total_env_impacts","prtp_pct": 1, "value_factor": tot1})
        rows.append({**base, "component": "total_env_impacts","prtp_pct": 0, "value_factor": tot0})
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Table 6 — Heat generation value factors  (Chapter 4, p. 25)
# Unit: EUR-cent_2025 / kWh_final_energy
# ──────────────────────────────────────────────────────────────────────────────
_HEAT_DATA = [
    # (source, air_pollutants, ghg_1pct, ghg_0pct, total_1pct, total_0pct)
    ("Heating_oil",                           1.51, 10.73, 30.88, 12.24, 32.39),
    ("Natural_gas",                           0.65,  8.07, 22.69,  8.72, 23.34),
    ("Lignite_briquette",                    12.17, 15.04, 42.55, 27.21, 54.72),
    ("District_heating_with_grid_losses",     1.78,  9.82, 27.62, 11.60, 29.40),
    ("Electricity_heating_with_grid_losses",  2.85, 16.42, 46.60, 19.26, 49.45),
    ("Solar_thermal",                         0.45,  0.75,  2.12,  1.20,  2.57),
    ("Surface_geothermal_and_ambient_heat",   1.31,  5.50, 15.60,  6.81, 16.91),
    ("Deep_geothermal",                       0.28,  1.18,  3.36,  1.47,  3.64),
    ("Biomass",                               4.01,  1.20,  2.83,  5.22,  6.85),
]


def _build_heat_rows() -> list[dict]:
    rows = []
    for rec in _HEAT_DATA:
        src, ap, ghg1, ghg0, tot1, tot0 = rec
        base = {"source_table": "Table 6", "chapter": 4,
                "energy_source": src, "unit": "EUR-cent_2025/kWh_final_energy"}
        rows.append({**base, "component": "air_pollutants",  "prtp_pct": "",  "value_factor": ap})
        rows.append({**base, "component": "greenhouse_gases", "prtp_pct": 1,  "value_factor": ghg1})
        rows.append({**base, "component": "greenhouse_gases", "prtp_pct": 0,  "value_factor": ghg0})
        rows.append({**base, "component": "total_env_impacts","prtp_pct": 1,  "value_factor": tot1})
        rows.append({**base, "component": "total_env_impacts","prtp_pct": 0,  "value_factor": tot0})
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Table 7 — Refrigerant value factors  (Chapter 4, p. 27)
# Unit: EUR_2025 / kg refrigerant
# All refrigerants have zero ozone depletion potential
# ──────────────────────────────────────────────────────────────────────────────
_REFRIGERANT_DATA = [
    # (classification, category, refrigerant, gwp100, vf_1pct, vf_0pct)
    ("stable_in_air",    "Hydrofluorocarbons", "R-32",   675,  230,  670),
    ("stable_in_air",    "Hydrofluorocarbons", "R-134a",1430,  490, 1415),
    ("stable_in_air",    "Hydrofluorocarbons", "R-410A",2088,  720, 2070),
    ("non_stable_in_air","Propane",            "R-290",     3,    1,    3),
    ("non_stable_in_air","NH3",                "R-717",     0,    0,    0),
    ("non_stable_in_air","CO2",                "R-744",     1,  0.3,    1),
    ("non_stable_in_air","Isobutane",          "R-600a",    3,    1,    3),
    ("non_stable_in_air","Propane",            "R-1270",    2,  0.7,    2),
]


def _build_refrigerant_rows() -> list[dict]:
    rows = []
    for rec in _REFRIGERANT_DATA:
        cls, cat, ref, gwp, vf1, vf0 = rec
        base = {"source_table": "Table 7", "chapter": 4,
                "classification": cls, "category": cat, "refrigerant": ref,
                "gwp100": gwp, "unit": "EUR_2025/kg_refrigerant"}
        rows.append({**base, "prtp_pct": 1, "value_factor": vf1})
        rows.append({**base, "prtp_pct": 0, "value_factor": vf0})
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 9–16 — Transport value factors per vehicle km  (Chapter 5, pp. 31–40)
# Unit: EUR-cent_2025 / vehicle km
# Note: Noise marked *** = not included numerically; air long-haul has no abrasion
# ──────────────────────────────────────────────────────────────────────────────
# Each row: (route, prtp, vehicle_category, specification,
#            ghg, ap_exhaust, ap_abrasion, infra_vehicles, energy, total)
_TRANSPORT_VEHKM = [
    # ── Table 9a: all routes, 0% PRTP ──────────────────────────────────────
    ("all_routes", 0, "Car",                  "Petrol",          16.09, 0.46, 0.20,   8.00,  6.15,   30.91),
    ("all_routes", 0, "Car",                  "Diesel",          17.48, 2.40, 0.20,   8.20,  4.90,   33.18),
    ("all_routes", 0, "Car",                  "Electric",         0.00, 0.00, 0.20,  12.35,  9.24,   21.79),
    ("all_routes", 0, "Small_motorcycle",     "Diesel",           6.21, 3.16, 0.07,   3.49,  2.44,   15.38),
    ("all_routes", 0, "Motorcycle",           "Petrol",          12.38, 0.71, 0.07,   5.31,  4.36,   22.83),
    ("all_routes", 0, "LCV",                  "Diesel",          24.40, 3.39, 0.20,   9.16,  7.44,   44.59),
    ("all_routes", 0, "LCV",                  "Petrol",          18.46, 0.77, 0.20,   9.16,  7.06,   35.65),
    ("all_routes", 0, "LCV",                  "Electric",         0.00, 0.00, 0.20,  14.15, 12.05,   26.40),
    ("all_routes", 0, "HGV_<7.5t",            "Diesel",          37.07, 5.69, 1.08,   9.16,  7.44,   60.43),
    ("all_routes", 0, "HGV_7.5-14t",          "Diesel",          41.90, 5.52, 1.08,  12.37,  9.96,   70.83),
    ("all_routes", 0, "HGV_14-28t",           "Diesel",          62.87, 6.81, 1.08,  32.49, 22.37,  125.61),
    ("all_routes", 0, "HGV_28-40t",           "Diesel",          82.83, 4.78, 1.08,  54.50, 24.90,  168.09),
    ("all_routes", 0, "Public_bus",           "Diesel",          97.65,14.57, 2.05,  26.22, 33.25,  173.74),
    ("all_routes", 0, "Coach",                "Diesel",          68.82, 9.39, 1.24,  26.01, 22.39,  127.84),
    ("all_routes", 0, "Passenger_train_LD",   "Electric",         0.00, 0.00, 6.24, 175.32,827.05, 1008.60),
    ("all_routes", 0, "Passenger_train_LT",   "Weighted_av.",    52.69,20.71, 3.15,  48.36,338.80,  463.72),
    ("all_routes", 0, "Freight_train",        "Weighted_av.",   110.16,50.77, 7.38, 329.67,849.85, 1347.83),
    ("all_routes", 0, "Passenger_air_SM",     "Short_medium_haul",1844.76,223.29,"",31.32,271.64, 2371.02),
    ("all_routes", 0, "Passenger_air_LH",     "Long_haul",      3753.59,357.33,"",  30.23,405.43, 4546.58),
    ("all_routes", 0, "Freight_air",          "Weighted_av.",   4942.15,531.21,"",  48.49,555.03, 6076.89),
    ("all_routes", 0, "Inland_dry_cargo_vessel","National",     1981.45,1223.09,"", 766.18,567.59, 4538.32),
    ("all_routes", 0, "Inland_tank_vessel",   "National",       2892.37,1772.09,"", 795.86,828.53, 6288.85),
    ("all_routes", 0, "Inland_pushed_convoy", "National",       4416.48,2715.51,"", 766.18,706.14, 8604.31),
    # ── Table 10b: all routes, 1% PRTP ─────────────────────────────────────
    ("all_routes", 1, "Car",                  "Petrol",           5.58, 0.46, 0.20,   3.55,  2.71,   12.50),
    ("all_routes", 1, "Car",                  "Diesel",           6.08, 2.40, 0.20,   3.64,  2.10,   14.43),
    ("all_routes", 1, "Car",                  "Electric",         0.00, 0.00, 0.20,   6.34,  3.85,   10.39),
    ("all_routes", 1, "Small_motorcycle",     "Diesel",           2.27, 3.16, 0.07,   1.59,  1.05,    8.15),
    ("all_routes", 1, "Motorcycle",           "Petrol",           4.31, 0.71, 0.07,   2.48,  1.87,    9.44),
    ("all_routes", 1, "LCV",                  "Diesel",           8.48, 3.39, 0.20,   4.16,  3.19,   19.42),
    ("all_routes", 1, "LCV",                  "Petrol",           6.40, 0.77, 0.20,   4.16,  3.10,   14.64),
    ("all_routes", 1, "LCV",                  "Electric",         0.00, 0.00, 0.20,   7.61,  5.02,   12.84),
    ("all_routes", 1, "HGV_<7.5t",            "Diesel",          12.88, 5.69, 1.08,   4.16,  3.19,   27.00),
    ("all_routes", 1, "HGV_7.5-14t",          "Diesel",          14.56, 5.52, 1.08,   5.64,  4.27,   31.07),
    ("all_routes", 1, "HGV_14-28t",           "Diesel",          21.86, 6.81, 1.08,  14.93,  9.60,   54.27),
    ("all_routes", 1, "HGV_28-40t",           "Diesel",          28.82, 4.78, 1.08,  24.80, 10.69,   70.17),
    ("all_routes", 1, "Public_bus",           "Diesel",          33.92,14.57, 2.05,  11.25, 14.09,   75.88),
    ("all_routes", 1, "Coach",                "Diesel",          23.92, 9.39, 1.24,  11.61,  9.61,   55.77),
    ("all_routes", 1, "Passenger_train_LD",   "Electric",         0.00, 0.00, 6.24,  79.01,322.46,  407.72),
    ("all_routes", 1, "Passenger_train_LT",   "Weighted_av.",    18.28,20.71, 3.15,  21.80,133.89,  197.83),
    ("all_routes", 1, "Freight_train",        "Weighted_av.",    38.22,50.77, 7.38, 148.26,334.87,  579.50),
    ("all_routes", 1, "Passenger_air_SM",     "Short_medium_haul",640.11,223.29,"", 12.06,122.56,  998.02),
    ("all_routes", 1, "Passenger_air_LH",     "Long_haul",      1302.00,357.33,"",  11.64,182.93, 1853.90),
    ("all_routes", 1, "Freight_air",          "Weighted_av.",   1714.33,531.21,"",  18.67,250.56, 2514.77),
    ("all_routes", 1, "Inland_dry_cargo_vessel","National",      687.37,1223.09,"", 331.61,273.58, 2515.65),
    ("all_routes", 1, "Inland_tank_vessel",   "National",       1003.37,1772.09,"", 355.50,399.35, 3530.30),
    ("all_routes", 1, "Inland_pushed_convoy", "National",       1532.09,2715.51,"", 331.61,335.27, 4914.49),
    # ── Table 11a: motorway, 0% PRTP ───────────────────────────────────────
    ("motorway", 0, "Car",            "Petrol",    17.00, 0.55, 0.14,  8.00, 6.15,  31.84),
    ("motorway", 0, "Car",            "Diesel",    18.42, 3.06, 0.14,  8.20, 4.90,  34.71),
    ("motorway", 0, "Car",            "Electric",   0.00, 0.00, 0.14, 12.35, 9.24,  21.72),
    ("motorway", 0, "Small_motorcycle","Diesel",    6.17, 2.31, 0.03,  3.49, 2.44,  14.44),
    ("motorway", 0, "Motorcycle",     "Petrol",    12.87, 0.87, 0.03,  5.31, 4.36,  23.43),
    ("motorway", 0, "LCV",            "Diesel",    29.27, 4.81, 0.14,  9.16, 7.44,  50.81),
    ("motorway", 0, "LCV",            "Petrol",    21.88, 0.83, 0.14,  9.16, 7.06,  39.06),
    ("motorway", 0, "LCV",            "Electric",   0.00, 0.00, 0.14, 14.15,12.05,  26.34),
    ("motorway", 0, "HGV_<7.5t",      "Diesel",    37.91, 5.31, 0.60,  9.16, 7.44,  60.41),
    ("motorway", 0, "HGV_7.5-14t",    "Diesel",    41.61, 5.06, 0.60, 12.37, 9.96,  69.60),
    ("motorway", 0, "HGV_14-28t",     "Diesel",    59.45, 5.93, 0.60, 32.49,22.37, 120.84),
    ("motorway", 0, "HGV_28-40t",     "Diesel",    76.68, 4.05, 0.60, 54.50,24.90, 160.73),
    ("motorway", 0, "Public_bus",     "Diesel",    71.98,11.92, 0.60, 26.22,33.25, 143.96),
    ("motorway", 0, "Coach",          "Diesel",    62.25, 7.08, 0.60, 26.01,22.39, 118.33),
    # ── Table 12b: motorway, 1% PRTP ───────────────────────────────────────
    ("motorway", 1, "Car",            "Petrol",     5.90, 0.55, 0.14,  3.55, 2.71,  12.83),
    ("motorway", 1, "Car",            "Diesel",     6.40, 3.06, 0.14,  3.64, 2.10,  15.34),
    ("motorway", 1, "Car",            "Electric",   0.00, 0.00, 0.14,  6.34, 3.85,  10.32),
    ("motorway", 1, "Small_motorcycle","Diesel",    2.24, 2.31, 0.03,  1.59, 1.05,   7.23),
    ("motorway", 1, "Motorcycle",     "Petrol",     4.47, 0.87, 0.03,  2.48, 1.87,   9.73),
    ("motorway", 1, "LCV",            "Diesel",    10.16, 4.81, 0.14,  4.16, 3.19,  22.46),
    ("motorway", 1, "LCV",            "Petrol",     7.59, 0.83, 0.14,  4.16, 3.10,  15.82),
    ("motorway", 1, "LCV",            "Electric",   0.00, 0.00, 0.14,  7.61, 5.02,  12.77),
    ("motorway", 1, "HGV_<7.5t",      "Diesel",    13.17, 5.31, 0.60,  4.16, 3.19,  26.42),
    ("motorway", 1, "HGV_7.5-14t",    "Diesel",    14.46, 5.06, 0.60,  5.64, 4.27,  30.03),
    ("motorway", 1, "HGV_14-28t",     "Diesel",    20.67, 5.93, 0.60, 14.93, 9.60,  51.73),
    ("motorway", 1, "HGV_28-40t",     "Diesel",    26.68, 4.05, 0.60, 24.80,10.69,  66.82),
    ("motorway", 1, "Public_bus",     "Diesel",    25.02,11.92, 0.60, 11.25,14.09,  62.87),
    ("motorway", 1, "Coach",          "Diesel",    21.64, 7.08, 0.60, 11.61, 9.61,  50.54),
    # ── Table 13a: rural, 0% PRTP ──────────────────────────────────────────
    ("rural", 0, "Car",              "Petrol",    14.47, 0.40, 0.14,  8.00, 6.15,  29.17),
    ("rural", 0, "Car",              "Diesel",    16.18, 2.05, 0.14,  8.20, 4.90,  31.47),
    ("rural", 0, "Car",              "Electric",   0.00, 0.00, 0.14, 12.35, 9.24,  21.72),
    ("rural", 0, "Small_motorcycle", "Diesel",     6.21, 2.38, 0.04,  3.49, 2.44,  14.56),
    ("rural", 0, "Motorcycle",       "Petrol",    11.32, 0.71, 0.04,  5.31, 4.36,  21.74),
    ("rural", 0, "LCV",              "Diesel",    22.58, 3.01, 0.14,  9.16, 7.44,  42.32),
    ("rural", 0, "LCV",              "Petrol",    16.90, 0.70, 0.14,  9.16, 7.06,  33.95),
    ("rural", 0, "LCV",              "Electric",   0.00, 0.00, 0.14, 14.15,12.05,  26.34),
    ("rural", 0, "HGV_<7.5t",        "Diesel",    36.70, 5.50, 0.77,  9.16, 7.44,  59.56),
    ("rural", 0, "HGV_7.5-14t",      "Diesel",    42.81, 5.37, 0.77, 12.37, 9.96,  71.27),
    ("rural", 0, "HGV_14-28t",       "Diesel",    66.57, 6.72, 0.77, 32.49,22.37, 128.91),
    ("rural", 0, "HGV_28-40t",       "Diesel",    89.62, 4.82, 0.77, 54.50,24.90, 174.61),
    ("rural", 0, "Public_bus",       "Diesel",    95.41,12.83, 1.01, 26.22,33.25, 168.72),
    ("rural", 0, "Coach",            "Diesel",    71.18, 8.97, 0.87, 26.01,22.39, 129.42),
    ("rural", 0, "Passenger_train_LD","Electric",   0.00, 0.00, 6.24,175.32,827.05,1008.60),
    ("rural", 0, "Passenger_train_LT","Weighted_av.",52.69,20.41,3.15,48.36,338.80, 463.43),
    ("rural", 0, "Freight_train",    "Weighted_av.",110.16,49.80,7.38,329.67,849.85,1346.87),
    # ── Table 14b: rural, 1% PRTP ──────────────────────────────────────────
    ("rural", 1, "Car",              "Petrol",     5.02, 0.40, 0.14,  3.55, 2.71,  11.81),
    ("rural", 1, "Car",              "Diesel",     5.63, 2.05, 0.14,  3.64, 2.10,  13.56),
    ("rural", 1, "Car",              "Electric",   0.00, 0.00, 0.14,  6.34, 3.85,  10.32),
    ("rural", 1, "Small_motorcycle", "Diesel",     2.27, 2.38, 0.04,  1.59, 1.05,   7.33),
    ("rural", 1, "Motorcycle",       "Petrol",     3.94, 0.71, 0.04,  2.48, 1.87,   9.04),
    ("rural", 1, "LCV",              "Diesel",     7.85, 3.01, 0.14,  4.16, 3.19,  18.35),
    ("rural", 1, "LCV",              "Petrol",     5.86, 0.70, 0.14,  4.16, 3.10,  13.96),
    ("rural", 1, "LCV",              "Electric",   0.00, 0.00, 0.14,  7.61, 5.02,  12.77),
    ("rural", 1, "HGV_<7.5t",        "Diesel",    12.75, 5.50, 0.77,  4.16, 3.19,  26.37),
    ("rural", 1, "HGV_7.5-14t",      "Diesel",    14.87, 5.37, 0.77,  5.64, 4.27,  30.92),
    ("rural", 1, "HGV_14-28t",       "Diesel",    23.14, 6.72, 0.77, 14.93, 9.60,  55.16),
    ("rural", 1, "HGV_28-40t",       "Diesel",    31.18, 4.82, 0.77, 24.80,10.69,  72.25),
    ("rural", 1, "Public_bus",       "Diesel",    33.15,12.83, 1.01, 11.25,14.09,  72.33),
    ("rural", 1, "Coach",            "Diesel",    24.74, 8.97, 0.87, 11.61, 9.61,  55.80),
    ("rural", 1, "Passenger_train_LD","Electric",  0.00, 0.00, 6.24, 79.01,322.46, 407.72),
    ("rural", 1, "Passenger_train_LT","Weighted_av.",18.28,20.41,3.15,21.80,133.89, 197.53),
    ("rural", 1, "Freight_train",    "Weighted_av.",38.22,49.80,7.38,148.26,334.87, 578.53),
    # ── Table 15a: urban, 0% PRTP ──────────────────────────────────────────
    ("urban", 0, "Car",              "Petrol",    16.90, 0.47, 0.85,  8.00, 6.15,  32.38),
    ("urban", 0, "Car",              "Diesel",    17.98, 2.26, 0.85,  8.20, 4.90,  34.19),
    ("urban", 0, "Car",              "Electric",   0.00, 0.00, 0.85, 12.35, 9.24,  22.44),
    ("urban", 0, "Small_motorcycle", "Diesel",     6.21,10.88, 0.33,  3.49, 2.44,  23.35),
    ("urban", 0, "Motorcycle",       "Petrol",    12.90, 1.15, 0.33,  5.31, 4.36,  24.05),
    ("urban", 0, "LCV",              "Diesel",    22.31, 3.02, 0.85,  9.16, 7.44,  42.78),
    ("urban", 0, "LCV",              "Petrol",    17.20, 0.81, 0.85,  9.16, 7.06,  35.08),
    ("urban", 0, "LCV",              "Electric",   0.00, 0.00, 0.85, 14.15,12.05,  27.05),
    ("urban", 0, "HGV_<7.5t",        "Diesel",    33.73, 8.14, 7.86,  9.16, 7.44,  66.32),
    ("urban", 0, "HGV_7.5-14t",      "Diesel",    40.50, 7.79, 7.86, 12.37, 9.96,  78.47),
    ("urban", 0, "HGV_14-28t",       "Diesel",    68.28,10.62, 7.86, 32.49,22.37, 141.61),
    ("urban", 0, "HGV_28-40t",       "Diesel",    92.80, 8.03, 7.86, 54.50,24.90, 188.10),
    ("urban", 0, "Public_bus",       "Diesel",   104.28,17.16,11.10, 26.22,33.25, 192.01),
    ("urban", 0, "Coach",            "Diesel",    76.81,14.34, 8.22, 26.01,22.39, 147.76),
    ("urban", 0, "Passenger_train_LD","Electric",   0.00, 0.00, 6.24,175.32,827.05,1008.60),
    ("urban", 0, "Passenger_train_LT","Weighted_av.",52.69,23.58,3.15,48.36,338.80, 466.59),
    ("urban", 0, "Freight_train",    "Weighted_av.",110.16,60.21,7.38,329.67,849.85,1357.28),
    # ── Table 16b: urban, 1% PRTP ──────────────────────────────────────────
    ("urban", 1, "Car",              "Petrol",     5.86, 0.47, 0.85,  3.55, 2.71,  13.44),
    ("urban", 1, "Car",              "Diesel",     6.26, 2.26, 0.85,  3.64, 2.10,  15.11),
    ("urban", 1, "Car",              "Electric",   0.00, 0.00, 0.85,  6.34, 3.85,  11.04),
    ("urban", 1, "Small_motorcycle", "Diesel",     2.27,10.88, 0.33,  1.59, 1.05,  16.12),
    ("urban", 1, "Motorcycle",       "Petrol",     4.49, 1.15, 0.33,  2.48, 1.87,  10.32),
    ("urban", 1, "LCV",              "Diesel",     7.76, 3.02, 0.85,  4.16, 3.19,  18.98),
    ("urban", 1, "LCV",              "Petrol",     5.97, 0.81, 0.85,  4.16, 3.10,  14.89),
    ("urban", 1, "LCV",              "Electric",   0.00, 0.00, 0.85,  7.61, 5.02,  13.49),
    ("urban", 1, "HGV_<7.5t",        "Diesel",    11.73, 8.14, 7.86,  4.16, 3.19,  35.07),
    ("urban", 1, "HGV_7.5-14t",      "Diesel",    14.08, 7.79, 7.86,  5.64, 4.27,  39.63),
    ("urban", 1, "HGV_14-28t",       "Diesel",    23.74,10.62, 7.86, 14.93, 9.60,  66.74),
    ("urban", 1, "HGV_28-40t",       "Diesel",    32.29, 8.03, 7.86, 24.80,10.69,  83.67),
    ("urban", 1, "Public_bus",       "Diesel",    36.22,17.16,11.10, 11.25,14.09,  89.82),
    ("urban", 1, "Coach",            "Diesel",    26.70,14.34, 8.22, 11.61, 9.61,  70.47),
    ("urban", 1, "Passenger_train_LD","Electric",   0.00, 0.00, 6.24, 79.01,322.46, 407.72),
    ("urban", 1, "Passenger_train_LT","Weighted_av.",18.28,23.58,3.15,21.80,133.89, 200.70),
    ("urban", 1, "Freight_train",    "Weighted_av.",38.22,60.21,7.38,148.26,334.87, 588.94),
]


def _build_transport_vehkm_rows() -> list[dict]:
    rows = []
    table_map = {("all_routes",0):"Table 9",  ("all_routes",1):"Table 10",
                 ("motorway",  0):"Table 11", ("motorway",  1):"Table 12",
                 ("rural",     0):"Table 13", ("rural",     1):"Table 14",
                 ("urban",     0):"Table 15", ("urban",     1):"Table 16"}
    for rec in _TRANSPORT_VEHKM:
        route, prtp, vehicle, spec, ghg, ap_ex, ap_ab, infra, energy, total = rec
        rows.append({
            "source_table":        table_map.get((route, prtp), ""),
            "chapter":             5,
            "route_type":          route,
            "prtp_pct":            prtp,
            "vehicle_category":    vehicle,
            "specification":       spec,
            "ghg":                 ghg,
            "air_pollutants_exhaust":  ap_ex,
            "air_pollutants_abrasion": ap_ab,
            "infra_and_vehicles":  infra,
            "energy_supply":       energy,
            "total":               total,
            "noise_included":      "no",
            "unit":                "EUR-cent_2025/vehicle_km",
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 17–18 — Occupation rates and per-Pkm/tkm factors  (Chapter 5, pp. 41–42)
# ──────────────────────────────────────────────────────────────────────────────
_OCCUPATION_DATA = [
    # (vehicle, passengers_per_vehicle, tonnes_per_vehicle)
    ("Car",                                   1.40, ""),
    ("Small_motorcycle",                      1.00, ""),
    ("Motorcycle",                            1.40, ""),
    ("Public_bus",                           12.90, ""),
    ("Coach",                                24.90, ""),
    ("Passenger_train_LD",                  261.00, ""),
    ("Passenger_train_LT",                   72.00, ""),
    ("Passenger_air_SM",                    124.00, ""),
    ("Passenger_air_LH",                    199.00, ""),
    ("LCV",                                    "",  0.40),
    ("HGV_<7.5t",                              "",  0.92),
    ("HGV_7.4-14t",                            "",  1.59),
    ("HGV_14-28t",                             "",  3.39),
    ("HGV_28-40t_trailer",                     "", 10.03),
    ("Freight_train",                          "", 560.00),
    ("Freight_air",                            "",  52.82),
    ("Inland_waterways_motor_vessel",          "", 938.00),
    ("Inland_waterways_water_craft_assembly",  "",1902.00),
]

_PKTKM_DATA = [
    # (vehicle, specification, unit, total_1pct, total_0pct)
    ("Car",                  "Petrol",          "EUR-cent_2025/Pkm",  8.93, 22.09),
    ("Car",                  "Diesel",          "EUR-cent_2025/Pkm", 10.31, 23.72),
    ("Car",                  "Electric",        "EUR-cent_2025/Pkm",  7.43, 15.57),
    ("Small_motorcycle",     "Diesel",          "EUR-cent_2025/Pkm",  8.57, 16.19),
    ("Motorcycle",           "Petrol",          "EUR-cent_2025/Pkm",  6.74, 16.30),
    ("Public_bus",           "Diesel",          "EUR-cent_2025/Pkm",  5.88, 13.47),
    ("Coach",                "Diesel",          "EUR-cent_2025/Pkm",  4.32,  9.91),
    ("Passenger_train_LD",   "Electric",        "EUR-cent_2025/Pkm",  1.56,  3.86),
    ("Passenger_train_LT",   "Weighted_av.",    "EUR-cent_2025/Pkm",  2.75,  6.44),
    ("Passenger_air_SM",     "Short_medium_haul","EUR-cent_2025/Pkm", 7.81, 18.55),
    ("Passenger_air_LH",     "Long_haul",       "EUR-cent_2025/Pkm",  9.04, 22.16),
    ("HGV_<7.5t",            "Diesel",          "EUR-cent_2025/tkm", 29.32, 65.62),
    ("HGV_7.5-14t",          "Diesel",          "EUR-cent_2025/tkm", 19.59, 44.66),
    ("HGV_14-28t",           "Diesel",          "EUR-cent_2025/tkm", 15.99, 37.01),
    ("HGV_28-40t",           "Diesel",          "EUR-cent_2025/tkm",  7.00, 16.76),
    ("Freight_train",        "Weighted_av.",    "EUR-cent_2025/tkm",  1.03,  2.41),
    ("Freight_air",          "Weighted_av.",    "EUR-cent_2025/tkm", 52.32,127.04),
    ("Inland_dry_cargo_vessel","National",      "EUR-cent_2025/tkm",  2.68,  4.84),
    ("Inland_tank_vessel",   "National",        "EUR-cent_2025/tkm",  3.76,  6.71),
    ("Inland_pushed_convoy", "National",        "EUR-cent_2025/tkm",  2.58,  4.52),
]


def _build_transport_pkm_rows() -> list[dict]:
    rows = []
    for rec in _OCCUPATION_DATA:
        v, pax, tonnes = rec
        rows.append({
            "source_table": "Table 17", "chapter": 5,
            "vehicle_category": v,
            "passengers_per_vehicle": pax,
            "tonnes_per_vehicle": tonnes,
        })
    for rec in _PKTKM_DATA:
        v, spec, unit, tot1, tot0 = rec
        rows.append({
            "source_table": "Table 18", "chapter": 5,
            "vehicle_category": v, "specification": spec, "unit": unit,
            "total_env_impacts_1pct_prtp": tot1,
            "total_env_impacts_0pct_prtp": tot0,
            "noise_included": "no",
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 19–20 — Noise value factors  (Chapter 5, pp. 43–45)
# Unit: EUR_2025 / person / year
# Source: Bieler and Sutter (2022)
# ──────────────────────────────────────────────────────────────────────────────
_NOISE_ANNOYANCE = [
    # (dba_class, road_total, rail_total, air_total)  — Table 19
    ("45-49", 118,    66.45, 187),
    ("50-54", 138,   123,    315),
    ("55-59", 183,   200,    447),
    ("60-64", 253,   299,    585),
    ("65-69", 348,   418,    728),
    ("70-74", 469,   558,    877),
    (">=75",  615,   720,  1_031),
]

# Table 20: cognitive impairment in children only (most practical for value factor use)
_NOISE_COGNITIVE_CHILDREN = [
    # (dba_class, road_total, rail_total, air_total)
    ("45-49",  "",      "",       ""),
    ("50-54",  2.14,   2.14,    2.14),
    ("55-59", 13.55,  13.55,   13.55),
    ("60-64", 34.08,  34.08,   34.08),
    ("65-69", 54.61,  54.61,   54.61),
    ("70-74", 75.14,  75.14,   75.14),
    (">=75",  95.67,  95.67,   95.67),
]


def _build_noise_rows() -> list[dict]:
    rows = []
    for dba, road, rail, air in _NOISE_ANNOYANCE:
        for mode, val in [("road", road), ("rail", rail), ("air", air)]:
            rows.append({
                "source_table": "Table 19", "chapter": 5,
                "impact_type": "annoyance_excl_sleep_disturbance",
                "dba_class_LDEN": dba, "transport_mode": mode,
                "value_factor": val, "unit": "EUR_2025/person/year",
            })
    for dba, road, rail, air in _NOISE_COGNITIVE_CHILDREN:
        for mode, val in [("road", road), ("rail", rail), ("air", air)]:
            rows.append({
                "source_table": "Table 20", "chapter": 5,
                "impact_type": "cognitive_impairment_children",
                "dba_class_LDEN": dba, "transport_mode": mode,
                "value_factor": val, "unit": "EUR_2025/person/year",
            })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 22–24 — Nitrogen and Phosphorus emissions  (Chapter 6, pp. 49–51)
# Unit: EUR_2025 / kg  (per kg N for air, per kg substance for water)
# Source: Karzai et al. (2025), Anthoff (2025), van der Kamp et al. (2024)
# Note: N air factors refer to 1 kg N, not 1 kg compound
# ──────────────────────────────────────────────────────────────────────────────
_NP_DATA = [
    # (table, substance, pathway, prtp_pct, value_factor, unit, note)
    ("Table 22","NOx",        "air",                     "", 124,   "EUR_2025/kg_N",  "per kg N"),
    ("Table 22","NH3",        "air",                     "", 36.82, "EUR_2025/kg_N",  "per kg N"),
    ("Table 22","N2O",        "air",                      1, 186,   "EUR_2025/kg_N",  "per kg N; 1% PRTP"),
    ("Table 22","N2O",        "air",                      0, 444,   "EUR_2025/kg_N",  "per kg N; 0% PRTP"),
    ("Table 23","Nitrogen",   "groundwater",             "", 2.24,  "EUR_2025/kg",    "limiting substance"),
    ("Table 23","Nitrogen",   "inland_waters",           "", 14.08, "EUR_2025/kg",    "limiting substance"),
    ("Table 23","Nitrogen",   "coastal_marine_waters",   "", 24.86, "EUR_2025/kg",    "limiting substance"),
    ("Table 23","Phosphorus", "inland_waters",           "", 437,   "EUR_2025/kg",    "limiting substance"),
    ("Table 23","Phosphorus", "coastal_marine_waters",   "", 799,   "EUR_2025/kg",    "limiting substance"),
    ("Table 24","Nitrogen",   "surface_water_unknown",   "", 24.86, "EUR_2025/kg",    "unknown limiting substance"),
    ("Table 24","Phosphorus", "surface_water_unknown",   "", 437,   "EUR_2025/kg",    "unknown limiting substance"),
]


def _build_np_rows() -> list[dict]:
    rows = []
    for tbl, substance, pathway, prtp, vf, unit, note in _NP_DATA:
        rows.append({
            "source_table": tbl, "chapter": 6,
            "substance": substance, "pathway": pathway,
            "prtp_pct": prtp, "value_factor": vf, "unit": unit, "note": note,
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Tables 25–27 — Agriculture  (Chapter 7, pp. 53–55)
# Source: Karzai and Hirschfeld (2024)
# ──────────────────────────────────────────────────────────────────────────────
_AGRI_PRODUCTS = [
    # (product, vf_1pct, vf_0pct)  — Table 25, EUR_2025/kg
    ("Milk",                              0.63,  1.35),
    ("Hard_cheese_before_sale",           6.65, 12.46),
    ("Beef_slaughter_weight",            33.51, 52.40),
    ("Beef_dairy_cattle_slaughter_weight", 7.00, 11.80),
    ("Pork_slaughter_weight",             5.83,  9.38),
    ("Poultry_slaughter_weight",          3.16,  6.43),
    ("Eggs",                              2.34,  4.11),
]

_AGRI_FERTILIZER = [
    # (substance, prtp_pct, value_factor)  — Table 26, EUR_2025/kg applied
    ("Nitrogen",   1,  8.40),
    ("Nitrogen",   0, 12.00),
    ("Phosphorus", "", 22.27),
]

_AGRI_SURPLUS = [
    # (substance, prtp_pct, value_factor)  — Table 27, EUR_2025/kg
    ("Nitrogen",   1, 21.06),
    ("Nitrogen",   0, 28.82),
    ("Phosphorus", "", 437),
]


def _build_agriculture_rows() -> list[dict]:
    rows = []
    for product, vf1, vf0 in _AGRI_PRODUCTS:
        rows.append({
            "source_table": "Table 25", "chapter": 7,
            "category": "animal_product", "item": product,
            "prtp_pct": 1, "value_factor": vf1, "unit": "EUR_2025/kg",
            "note": "conventional production; excl. biodiversity, most ecosystem services, animal welfare",
        })
        rows.append({
            "source_table": "Table 25", "chapter": 7,
            "category": "animal_product", "item": product,
            "prtp_pct": 0, "value_factor": vf0, "unit": "EUR_2025/kg",
            "note": "conventional production; excl. biodiversity, most ecosystem services, animal welfare",
        })
    for substance, prtp, vf in _AGRI_FERTILIZER:
        rows.append({
            "source_table": "Table 26", "chapter": 7,
            "category": "fertilizer_application", "item": substance,
            "prtp_pct": prtp, "value_factor": vf, "unit": "EUR_2025/kg_applied",
            "note": "total amount applied incl. absorbed portion",
        })
    for substance, prtp, vf in _AGRI_SURPLUS:
        rows.append({
            "source_table": "Table 27", "chapter": 7,
            "category": "nutrient_surplus", "item": substance,
            "prtp_pct": prtp, "value_factor": vf, "unit": "EUR_2025/kg",
            "note": "excess nutrients emitted to environment",
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Dispatch table — maps key → (builder_fn, fieldnames)
# ──────────────────────────────────────────────────────────────────────────────
_BUILDERS = {
    "ghg":               (_build_ghg_rows,            ["source_table","chapter","emission_year","substance","prtp_pct","value_factor","unit"]),
    "air_pollutants":    (_build_air_rows,             ["source_table","chapter","context","sector","surroundings","emission_height_m","substance","impact_component","value_factor","unit"]),
    "electricity":       (_build_electricity_rows,     ["source_table","chapter","energy_source","component","prtp_pct","value_factor","unit"]),
    "heat":              (_build_heat_rows,            ["source_table","chapter","energy_source","component","prtp_pct","value_factor","unit"]),
    "refrigerants":      (_build_refrigerant_rows,     ["source_table","chapter","classification","category","refrigerant","gwp100","prtp_pct","value_factor","unit"]),
    "transport_vehkm":   (_build_transport_vehkm_rows, ["source_table","chapter","route_type","prtp_pct","vehicle_category","specification","ghg","air_pollutants_exhaust","air_pollutants_abrasion","infra_and_vehicles","energy_supply","total","noise_included","unit"]),
    "transport_pkm_tkm": (_build_transport_pkm_rows,   ["source_table","chapter","vehicle_category","specification","unit","passengers_per_vehicle","tonnes_per_vehicle","total_env_impacts_1pct_prtp","total_env_impacts_0pct_prtp","noise_included"]),
    "noise":             (_build_noise_rows,           ["source_table","chapter","impact_type","dba_class_LDEN","transport_mode","value_factor","unit"]),
    "nitrogen_phosphorus":(_build_np_rows,             ["source_table","chapter","substance","pathway","prtp_pct","value_factor","unit","note"]),
    "agriculture":       (_build_agriculture_rows,     ["source_table","chapter","category","item","prtp_pct","value_factor","unit","note"]),
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────
def _write_excel(rows: list[dict], fieldnames: list[str], cfg: dict) -> Path:
    """Write rows to a formatted .xlsx file. Returns the Excel path."""
    pub = cfg["publication"]
    excel_path: Path = cfg["excel_path"]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Value Factors"

    header_fill = PatternFill("solid", fgColor="1F497D")
    header_font = Font(bold=True, color="FFFFFF")
    header_align = Alignment(horizontal="center", wrap_text=True)

    # Header row
    for col_idx, name in enumerate(fieldnames, 1):
        cell = ws.cell(row=1, column=col_idx, value=name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align

    # Data rows
    for row_idx, row in enumerate(rows, 2):
        for col_idx, name in enumerate(fieldnames, 1):
            ws.cell(row=row_idx, column=col_idx, value=row.get(name, ""))

    ws.freeze_panes = "A2"

    # Metadata sheet
    ws_meta = wb.create_sheet("Metadata")
    meta_rows = [
        ("Title",     cfg["title"]),
        ("Chapter",   f"Chapter {cfg['chapter']}"),
        ("Tables",    ", ".join(cfg.get("tables", []))),
        ("Unit",      cfg.get("unit", "")),
        ("Description", cfg.get("description", "")),
        ("Notes",     cfg.get("notes", "")),
        ("",          ""),
        ("Publication", pub["title"]),
        ("Subtitle",  pub["subtitle"]),
        ("Authors",   pub["authors"]),
        ("Publisher", pub["publisher"]),
        ("Year",      pub["year"]),
        ("ISSN",      pub["issn"]),
        ("Price base", pub["price_base"]),
    ]
    for r, (label, value) in enumerate(meta_rows, 1):
        ws_meta.cell(row=r, column=1, value=label).font = Font(bold=True)
        ws_meta.cell(row=r, column=2, value=value)
    ws_meta.column_dimensions["A"].width = 16
    ws_meta.column_dimensions["B"].width = 70

    wb.save(excel_path)
    return excel_path


def run_table(key: str) -> Path:
    """
    Extract all value factors for table group `key` and write to CSV + Excel.
    Returns the output CSV path.
    """
    cfg = config.get_table_config(key)
    out_path: Path = cfg["csv_path"]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if key not in _BUILDERS:
        raise KeyError(f"No builder for key '{key}'")

    builder_fn, fieldnames = _BUILDERS[key]
    rows = builder_fn()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    _write_excel(rows, fieldnames, cfg)

    n = len(rows)
    logger.info("%-25s → %4d rows  →  %s", key, n, out_path.name)
    return out_path


def run_all() -> dict[str, Path]:
    """Run all table groups and return {key: csv_path}."""
    results = {}
    for key in config.TABLE_GROUPS:
        results[key] = run_table(key)
    return results
