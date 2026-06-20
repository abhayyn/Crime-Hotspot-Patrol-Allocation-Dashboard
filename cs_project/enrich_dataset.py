"""
enrich_dataset.py
Adds approximate district lat/lng (for map plotting) and a computed
'risk_score' (0-100) per district-month, used to drive the hotspot map
and patrol resource allocation logic in the dashboard.

risk_score combines:
  - case volume (normalized within dataset)
  - state crime rate per lakh (severity context)
  - inverse chargesheet rate (lower enforcement follow-through => higher risk weight)
This is a transparent, explainable formula (not a black-box ML model),
which is appropriate for a law-enforcement decision-support tool where
explainability matters more than raw predictive accuracy.
"""
import pandas as pd
import numpy as np

df = pd.read_csv("/home/claude/project/data/crime_data.csv")

# Approximate district centroid coordinates (public knowledge, illustrative precision)
coords = {
    "Lucknow": (26.8467, 80.9462), "Kanpur Nagar": (26.4499, 80.3319), "Ghaziabad": (28.6692, 77.4538),
    "Agra": (27.1767, 78.0081), "Varanasi": (25.3176, 82.9739), "Prayagraj": (25.4358, 81.8463),
    "Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567), "Nagpur": (21.1458, 79.0882),
    "Thane": (19.2183, 72.9781), "Nashik": (19.9975, 73.7898),
    "Indore": (22.7196, 75.8577), "Bhopal": (23.2599, 77.4126), "Jabalpur": (23.1815, 79.9864), "Gwalior": (26.2183, 78.1828),
    "Ernakulam": (9.9816, 76.2999), "Thiruvananthapuram": (8.5241, 76.9366), "Kozhikode": (11.2588, 75.7804), "Thrissur": (10.5276, 76.2144),
    "Jaipur": (26.9124, 75.7873), "Jodhpur": (26.2389, 73.0243), "Kota": (25.2138, 75.8648), "Udaipur": (24.5854, 73.7125),
    "New Delhi": (28.6139, 77.2090), "South Delhi": (28.5245, 77.2066), "North West Delhi": (28.7041, 77.1025), "East Delhi": (28.6279, 77.2773),
    "Ahmedabad": (23.0225, 72.5714), "Surat": (21.1702, 72.8311), "Vadodara": (22.3072, 73.1812), "Rajkot": (22.3039, 70.8022),
    "Kolkata": (22.5726, 88.3639), "North 24 Parganas": (22.6190, 88.4338), "Howrah": (22.5958, 88.2636), "Murshidabad": (24.1833, 88.2667),
    "Bengaluru Urban": (12.9716, 77.5946), "Mysuru": (12.2958, 76.6394), "Belagavi": (15.8497, 74.4977), "Dakshina Kannada": (12.8438, 75.2479),
    "Chennai": (13.0827, 80.2707), "Coimbatore": (11.0168, 76.9558), "Madurai": (9.9252, 78.1198), "Tiruchirappalli": (10.7905, 78.7047),
    "Patna": (25.5941, 85.1376), "Gaya": (24.7955, 84.9994), "Muzaffarpur": (26.1209, 85.3647), "Bhagalpur": (25.2425, 86.9842),
    "Gurugram": (28.4595, 77.0266), "Faridabad": (28.4089, 77.3178), "Hisar": (29.1492, 75.7217), "Panipat": (29.3909, 76.9635),
    "Hyderabad": (17.3850, 78.4867), "Rangareddy": (17.3000, 78.3500), "Warangal Urban": (17.9689, 79.5941),
    "Ludhiana": (30.9010, 75.8573), "Amritsar": (31.6340, 74.8723), "Jalandhar": (31.3260, 75.5762),
    "Khordha": (20.1809, 85.6170), "Cuttack": (20.4625, 85.8830), "Ganjam": (19.3870, 84.6909),
}

df["lat"] = df["district"].map(lambda d: coords.get(d, (22.0, 79.0))[0])
df["lng"] = df["district"].map(lambda d: coords.get(d, (22.0, 79.0))[1])

agg = df.groupby(["state", "district", "month", "lat", "lng",
                   "state_crime_rate_per_lakh", "state_chargesheet_rate_pct"], as_index=False)["cases"].sum()

agg["vol_norm"] = (agg["cases"] - agg["cases"].min()) / (agg["cases"].max() - agg["cases"].min())
agg["rate_norm"] = (agg["state_crime_rate_per_lakh"] - agg["state_crime_rate_per_lakh"].min()) / \
                    (agg["state_crime_rate_per_lakh"].max() - agg["state_crime_rate_per_lakh"].min())
agg["enforcement_gap"] = (100 - agg["state_chargesheet_rate_pct"]) / 100

agg["risk_score"] = (
    0.55 * agg["vol_norm"] +
    0.25 * agg["rate_norm"] +
    0.20 * agg["enforcement_gap"]
) * 100
agg["risk_score"] = agg["risk_score"].round(1)

def risk_band(score):
    if score >= 65: return "Critical"
    if score >= 45: return "High"
    if score >= 25: return "Moderate"
    return "Low"

agg["risk_band"] = agg["risk_score"].apply(risk_band)

agg.to_csv("/home/claude/project/data/district_risk_scores.csv", index=False)
df.to_csv("/home/claude/project/data/crime_data.csv", index=False)

print("District-month risk rows:", len(agg))
print(agg[["state","district","month","cases","risk_score","risk_band"]].sort_values("risk_score", ascending=False).head(10))
