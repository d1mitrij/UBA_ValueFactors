# Methodology — UBA Value Factors

**Handbook on Environmental Value Factors, Methodological Convention 4.0 (December 2025)**

---

## 1. Conceptual Foundation

### 1.1 Damage-cost approach

The UBA MC 4.0 value factors quantify the **societal cost** of environmental pressures
in monetary terms (EUR at 2025 price levels). The framework is rooted in welfare
economics and the concept of willingness-to-pay to avoid environmental harm:

| Approach | UBA MC 4.0 | Comparison |
|---|---|---|
| Basis | Welfare economics / social cost | Legal liability / market price |
| Scope | Germany-specific context, global for GHG | Jurisdiction-specific |
| Metric | EUR_2025 / unit of pressure | EUR per event or unit |
| PRTP | Two scenarios: 0 % and 1 % | Single discount rate |
| Reference | Eser et al. (2025) | Varies |

### 1.2 Pure Rate of Time Preference (PRTP)

For GHG and derived impacts, two discount rate scenarios are always presented:

| PRTP | Interpretation |
|---|---|
| **0 %** | Equal intergenerational weighting — future damages are as important as present ones |
| **1 %** | Moderate preference for present generations — standard economic convention |

The 0 % PRTP scenario produces substantially higher social cost values for long-lived
gases (CO₂, N₂O) because their warming effect persists over centuries.

---

## 2. Greenhouse Gas Value Factors (Chapter 2)

### 2.1 Source model: GIVE (Anthoff 2025)

GHG social cost values are derived from the **GIVE model** (Greenhouse Impact Value
Estimator), an open-source Integrated Assessment Model developed by Anthoff (2025)
as a successor to the FUND model. Key features:

- Directly models CH₄ and N₂O in addition to CO₂ (no GWP100 proxy required)
- **Equity weighting**: uses German per-capita income as the reference for weighting
  damages across income groups, rather than global average income
- Covers 2020–2050 emission years in the handbook tables

### 2.2 Formula

```
VF[gas, year, prtp]  =  social cost of emissions in EUR_2025 per tonne GHG

- No inflation adjustment needed: values are already expressed in EUR_2025
- Values rise monotonically with emission year (later emissions cause more
  damage as atmospheric concentrations increase)
- Two PRTP columns per gas per year
```

### 2.3 Reference values (Table 1)

| Substance | Emission year | 0 % PRTP | 1 % PRTP | Unit |
|---|---|---|---|---|
| CO₂/CO₂-eq | 2020 | 935 | 310 | EUR_2025/t |
| CO₂/CO₂-eq | 2025 | 990 | 345 | EUR_2025/t |
| CO₂/CO₂-eq | 2030 | 1,050 | 375 | EUR_2025/t |
| CH₄ | 2025 | 9,220 | 5,800 | EUR_2025/t |
| N₂O | 2025 | 282,300 | 118,700 | EUR_2025/t |

---

## 3. Air Pollutant Value Factors (Chapter 3)

### 3.1 Damage pathways

Air pollutant value factors aggregate three damage components:

| Component | Substances affected |
|---|---|
| Health (primary) | PM₂.₅, PMcoarse, PM₁₀, NOₓ, SO₂, NMVOC, NH₃ |
| Crop loss | NOₓ, SO₂ (ozone precursors), NMVOC, NH₃ |
| Material/building damage | NOₓ, SO₂ |

### 3.2 Health impact model

- **Primary source:** van der Kamp et al. (2024); EcoSenseWeb v1.3
- **Dose–response functions:**
  - PM mortality: Chen and Hoek (2020) — replaces the older HRAPIE function
  - NOₓ/SO₂/NH₃: HRAPIE (2013) functions for non-primary impacts
- **Scope:** Germany; results in EUR/t emitted

### 3.3 Three table tiers

| Table | Context | Differentiation |
|---|---|---|
| Table 2 | Unknown/average source | Single row per substance |
| Table 3 | Stationary combustion | By sector × surroundings × emission height |
| Table 4 | Road traffic | By surrounding type (unknown/urban/suburban/rural) |

**Recommendation (UBA):** Use Table 2 when source type is unknown; use Tables 3 or 4
for specific combustion or transport contexts.

---

## 4. Energy Value Factors (Chapter 4)

### 4.1 Electricity (Table 5)

Value factors cover the **full life cycle** including upstream supply chains.
Five components are reported per energy source:

```
total = air_pollutants + greenhouse_gases
      (air_pollutants component is independent of PRTP)
      (greenhouse_gases component × two PRTP variants)
```

Unit: EUR-cent_2025 / kWh_el

### 4.2 Heat (Table 6)

Same five-component structure as electricity.
Unit: EUR-cent_2025 / kWh_final_energy

### 4.3 Refrigerants (Table 7)

GHG value factors are applied to GWP100 values per refrigerant:

```
VF[refrigerant, prtp] = GWP100[refrigerant] × VF[CO₂, 2025, prtp]
```

Unit: EUR_2025 / kg refrigerant lost

---

## 5. Transport Value Factors (Chapter 5)

### 5.1 Per vehicle km (Tables 8–16)

Five components are reported per vehicle/route/PRTP combination:

| Component | Description |
|---|---|
| `ghg` | Greenhouse gas emissions (fuel combustion + upstream) |
| `air_pollutants_exhaust` | Exhaust PM, NOₓ, SO₂ emissions |
| `air_pollutants_abrasion` | Tyre/brake/road abrasion particles |
| `infra_and_vehicles` | Infrastructure provision + vehicle manufacturing |
| `energy_supply` | Upstream energy supply chain |

**Noise is not included** in vehicle-km factors (reported separately in Tables 19–20).

Route types: `all_routes`, `motorway`, `rural`, `urban`.

### 5.2 Per passenger-km and tonne-km (Tables 17–18)

Derived from vehicle-km values by dividing by occupation/utilization rates
(Table 17). Total environmental impact only (no component breakdown).

### 5.3 Traffic noise (Tables 19–20)

Value factors in EUR_2025 per person per year, by:
- dB(A) class (L_DEN): 45–49, 50–54, 55–59, 60–64, 65–69, 70–74, ≥75
- Transport mode: road, rail, air

Table 19: annoyance excl. sleep disturbance.
Table 20: cognitive impairment in children.
Additional health endpoints (ischemic heart disease, stroke, etc.) are detailed
in the full handbook but not tabulated as standalone value factors.

Source: Bieler and Sutter (2022); WHO exposure–response functions (Guski et al. 2017).

---

## 6. Nitrogen and Phosphorus Value Factors (Chapter 6)

### 6.1 Air emissions (Table 22)

Value factors per kg **N** (not per kg compound):

| Substance | Pathway | Value | Unit |
|---|---|---|---|
| NOₓ | Air | 124 | EUR_2025/kg N |
| NH₃ | Air | 36.82 | EUR_2025/kg N |
| N₂O | Air (1 % PRTP) | 186 | EUR_2025/kg N |
| N₂O | Air (0 % PRTP) | 444 | EUR_2025/kg N |

### 6.2 Water emissions (Tables 23–24)

Factors apply the **limiting-substance assumption**: in any given water body,
either N or P is limiting for eutrophication — only the limiting nutrient contributes
damage. Results are therefore **lower bounds** on the true damage.

Source: Karzai et al. (2025).

---

## 7. Agriculture Value Factors (Chapter 7)

Three sub-tables cover different agricultural interventions:

| Table | Category | Item | Unit |
|---|---|---|---|
| Table 25 | Animal products | Milk, cheese, beef, pork, poultry, eggs | EUR_2025/kg |
| Table 26 | Fertilizer application | N (total applied), P | EUR_2025/kg applied |
| Table 27 | Nutrient surplus | N excess, P excess | EUR_2025/kg |

**Scope limitations (UBA note):** These value factors exclude biodiversity impacts,
most ecosystem services, and animal welfare costs. They represent partial lower bounds.

Source: Karzai and Hirschfeld (2024).

---

## 8. Price Base and Inflation

All values are expressed in **EUR_2025** (price level of 2025):

> Prices are adjusted for inflation using Destatis Consumer Price Index data
> (cumulative CPI increase through end of 2024 applied to the 2025 base).

Unlike steen-vf1 (which applies a year-specific EU HICP deflator to produce
year-nominal coefficients), UBA MC 4.0 values are published as a single
EUR_2025 figure per cell — no additional deflation step is applied in this pipeline.

---

## 9. Known Limitations

- **Germany-specific context** for air pollutant and transport factors
  (EcoSenseWeb v1.3 uses German population density and receptor data).
- **No country variation** for GHG values — the GIVE model produces a global
  social cost; no regional disaggregation is available.
- **Noise factors for annoyance only** — health endpoint values (IHD, stroke,
  hypertension) are described in the handbook text but not tabulated as
  standalone value factors in the handbook tables.
- **Agriculture factors exclude key impacts** — biodiversity, animal welfare,
  and most ecosystem services are not monetised.

---

## 10. References

- Eser, N., Matthey, A., Bünger, B. (2025). *Handbook on Environmental Value Factors.
  MC 4.0.* German Environment Agency (UBA). ISSN 2363-832X.
- Anthoff, D. (2025). GIVE model documentation.
- van der Kamp, J. et al. (2024). Air pollutant value factors for Germany.
- Chen, J., Hoek, G. (2020). Long-term exposure to PM and all-cause mortality.
  *Environmental Health Perspectives*.
- Walther, C. et al. (2024b). Energy and transport emission factors.
- Walther, C. et al. (2024c). Transport value factor methodology.
- Karzai, S. et al. (2025). Nitrogen and phosphorus value factors.
- Karzai, S., Hirschfeld, J. (2024). Agricultural value factors.
- Bieler, C., Sutter, D. (2022). Noise value factors.
- Guski, R. et al. (2017). WHO Environmental Noise Guidelines, Europe.

---

*Document Version 1.0 | Last Updated 2026-03-05 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
