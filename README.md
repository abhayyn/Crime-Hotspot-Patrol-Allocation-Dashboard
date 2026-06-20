# Crime Hotspot & Patrol Allocation Dashboard

An interactive dashboard that ranks Indian districts by a composite crime-risk score, built to support law-enforcement patrol and resource allocation decisions.

## What it does

- Computes a transparent, explainable **risk score (0–100)** per district per month, combining:
  - Case volume
  - State-level crime rate (per lakh population)
  - Enforcement gap (inverse of chargesheeting rate)
- Ranks districts into a live **Patrol Priority Index**
- Visualizes hotspots on an interactive India map
- Lets you filter by month and state
- Drills into any district for a monthly trend chart and crime-type breakdown

## Data honesty / methodology

State-level numbers (national crime rate, state crime rates, IPC case totals, chargesheeting rates) are **real figures from NCRB's published "Crime in India 2022" report**. District- and month-level numbers are a **modeled disaggregation** of those real totals (split by population share and a seasonal pattern), since NCRB does not freely publish a granular district × month × crime-type dataset. This is disclosed in the dashboard footer and in the full project report.

See `Project_Report.docx` / `Project_Report.pdf` for full methodology, the risk-score formula, and the law-enforcement use cases this tool supports.

## Files

| File | Description |
|---|---|
| `CrimeDashboard.jsx` | Self-contained React dashboard (data embedded, no backend needed) |
| `crime_dataset.csv` | Full district × month × crime-type dataset |
| `district_risk_scores.csv` | Aggregated district × month risk scores |
| `build_dataset.py` | Script that builds the dataset from NCRB state-level anchors |
| `enrich_dataset.py` | Adds coordinates and computes the risk score |

## Tech stack

Python (pandas, numpy) for data processing · React + Recharts for the dashboard · no API keys or backend required.

