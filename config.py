"""
config.py — UBA Methodological Convention 4.0 (December 2025)
Handbook on Environmental Value Factors

Defines all table groups, their metadata and output paths.
Mirrors the steen-vf1/eps_value_factors/config.py pattern.
"""

from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
THIS_DIR = Path(__file__).parent
OUTPUT_DIR = THIS_DIR / "output"

# ──────────────────────────────────────────────────────────────────────────────
# Publication metadata
# ──────────────────────────────────────────────────────────────────────────────
PUBLICATION = {
    "title":     "Handbook on Environmental Value Factors",
    "subtitle":  "Methodological Convention 4.0 for the Assessment of Environmental Impacts",
    "authors":   "Nadia Eser, Dr. Astrid Matthey, Dr. Björn Bünger",
    "publisher": "German Environment Agency (UBA), Dessau-Roßlau",
    "year":      2025,
    "month":     "December",
    "issn":      "2363-832X",
    "price_base": "EUR_2025",
}

# ──────────────────────────────────────────────────────────────────────────────
# Table groups  (analogous to steen-vf1 INDICATORS dict)
# ──────────────────────────────────────────────────────────────────────────────
TABLE_GROUPS = {
    "ghg": {
        "id":          "01",
        "title":       "Greenhouse Gas Emissions",
        "chapter":     2,
        "tables":      ["Table 1"],
        "description": "Social cost of CO2/CO2-eq, CH4 and N2O by emission year (2020-2050)",
        "unit":        "EUR_2025/t",
        "notes":       "Two PRTP scenarios: 0% (equal intergenerational weighting) and 1% PRTP. "
                       "Source: adapted GIVE model (Anthoff 2025) with equity weighting.",
    },
    "air_pollutants": {
        "id":          "02",
        "title":       "Air Pollutant Emissions",
        "chapter":     3,
        "tables":      ["Table 2", "Table 3", "Table 4"],
        "description": "Average and differentiated value factors for PM2.5, PMcoarse, PM10, "
                       "NOx, SO2, NMVOC, NH3 by source type and surroundings",
        "unit":        "EUR_2025/t",
        "notes":       "Health + crop + material/building impacts. "
                       "Source: van der Kamp et al. (2024), EcoSenseWeb v1.3, HRAPIE/Chen&Hoek(2020).",
    },
    "electricity": {
        "id":          "03",
        "title":       "Electric Power Generation",
        "chapter":     4,
        "tables":      ["Table 5"],
        "description": "Value factors per kWh for electricity generation in Germany incl. upstream chains",
        "unit":        "EUR-cent_2025/kWh_el",
        "notes":       "Air pollutant + GHG components. Two PRTP scenarios. "
                       "Source: Walther et al. (2024b), van der Kamp et al. (2024), Anthoff (2025).",
    },
    "heat": {
        "id":          "04",
        "title":       "Heat Generation",
        "chapter":     4,
        "tables":      ["Table 6"],
        "description": "Value factors per kWh final energy for household heat generation in Germany",
        "unit":        "EUR-cent_2025/kWh_final_energy",
        "notes":       "Two PRTP scenarios. Source: Walther et al. (2024b), van der Kamp et al. (2024).",
    },
    "refrigerants": {
        "id":          "05",
        "title":       "Refrigerants",
        "chapter":     4,
        "tables":      ["Table 7"],
        "description": "GWP100 values and value factors per kg of refrigerant loss",
        "unit":        "EUR_2025/kg_refrigerant",
        "notes":       "Based on CO2 value factors × GWP100. Source: Walther et al. (2024b).",
    },
    "transport_vehkm": {
        "id":          "06",
        "title":       "Passenger and Freight Transport — per vehicle km",
        "chapter":     5,
        "tables":      ["Table 8", "Table 9", "Table 10", "Table 11",
                        "Table 12", "Table 13", "Table 14", "Table 15", "Table 16"],
        "description": "Value factors per vehicle km by vehicle type, route type and PRTP scenario",
        "unit":        "EUR-cent_2025/vehicle_km",
        "notes":       "Route types: all_routes, motorway, rural, urban. "
                       "Noise not included (see Table 19/20). "
                       "Source: Walther et al. (2024c), van der Kamp et al. (2024), Anthoff (2025).",
    },
    "transport_pkm_tkm": {
        "id":          "07",
        "title":       "Passenger and Freight Transport — per Pkm or tkm",
        "chapter":     5,
        "tables":      ["Table 17", "Table 18"],
        "description": "Occupation/utilization rates and value factors per passenger-km or tonne-km",
        "unit":        "EUR-cent_2025/Pkm_or_tkm",
        "notes":       "Derived from veh.km factors × occupation/utilization rate. "
                       "Source: TREMOD 6.51, Bundesnetzagentur (2024).",
    },
    "noise": {
        "id":          "08",
        "title":       "Traffic Noise",
        "chapter":     5,
        "tables":      ["Table 19", "Table 20"],
        "description": "Value factors for noise-related annoyance, cognitive impairment and health "
                       "impacts by dB(A) class and transport mode",
        "unit":        "EUR_2025/person/year",
        "notes":       "L_DEN values. YLD + YLL components. "
                       "Source: Bieler and Sutter (2022), WHO ERF (Guski et al. 2017).",
    },
    "nitrogen_phosphorus": {
        "id":          "09",
        "title":       "Nitrogen and Phosphorus Emissions",
        "chapter":     6,
        "tables":      ["Table 22", "Table 23", "Table 24"],
        "description": "Value factors for N emissions to air, and N/P emissions to water",
        "unit":        "EUR_2025/kg",
        "notes":       "Per kg N (not per kg compound). N/P water factors are lower bounds "
                       "(limiting-substance assumption). Source: Karzai et al. (2025).",
    },
    "agriculture": {
        "id":          "10",
        "title":       "Agriculture",
        "chapter":     7,
        "tables":      ["Table 25", "Table 26", "Table 27"],
        "description": "Value factors for animal products, fertilizer use and nutrient surpluses",
        "unit":        "EUR_2025/kg",
        "notes":       "Excl. biodiversity, most ecosystem services and animal welfare. "
                       "Source: Karzai and Hirschfeld (2024).",
    },
}


def get_output_path(key: str) -> Path:
    """Return the CSV output path for a given table group key."""
    cfg = TABLE_GROUPS[key]
    filename = f"{cfg['id']:>02}_uba4_{key}.csv"
    return OUTPUT_DIR / filename


def get_excel_path(key: str) -> Path:
    """Return the Excel (.xlsx) output path for a given table group key."""
    cfg = TABLE_GROUPS[key]
    filename = f"{cfg['id']:>02}_uba4_{key}.xlsx"
    return OUTPUT_DIR / filename


def get_table_config(key: str) -> dict:
    """Return the full config dict for a table group, with output path appended."""
    if key not in TABLE_GROUPS:
        raise KeyError(f"Unknown table group '{key}'. Available: {list(TABLE_GROUPS)}")
    cfg = TABLE_GROUPS[key].copy()
    cfg["key"] = key
    cfg["csv_path"] = get_output_path(key)
    cfg["excel_path"] = get_excel_path(key)
    cfg["publication"] = PUBLICATION
    return cfg
