import pandas as pd
import requests
import folium
from urllib.parse import quote

# =========================
# 1) EDIT THESE VALUES
# =========================
ACCESS_TOKEN = "pk.eyJ1IjoiY2VjaWxpYW1tdXJwaHkiLCJhIjoiY21tMTFkNjU3MDRweDJ3b2c3Zjd6NThmZSJ9.0hGueEPJtzWFLvq4Pjab8Q"

# From your style URL: mapbox://styles/USERNAME/STYLE_ID
USERNAME = "ceciliammurphy"
STYLE_ID = "cmmaos5fy002o01qnd2l1a2hx"

CSV_PATH = "hometown_locations.csv"
OUTPUT_HTML = "hometown_map.html"

# =========================
# 2) MAPBOX TILE URL (CUSTOM BASEMAP)
# =========================
tiles = f"https://api.mapbox.com/styles/v1/{USERNAME}/{STYLE_ID}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={ACCESS_TOKEN}"

# =========================
# 3) GEOCODING FUNCTION
# =========================
def geocode_address(address: str, access_token: str):
    """
    Uses Mapbox forward geocoding to convert an address -> (lat, lon).
    Returns (None, None) if it fails.
    """
    q = quote(address)
    geocode_url = f"https://api.mapbox.com/search/geocode/v6/forward?q={q}&access_token={access_token}"
    r = requests.get(geocode_url, timeout=20)
    r.raise_for_status()
    data = r.json()

    try:
        lon, lat = data["features"][0]["geometry"]["coordinates"]  # [lon, lat]
        return lat, lon
    except (KeyError, IndexError, TypeError):
        return None, None

# =========================
# 4) READ CSV
# =========================
df = pd.read_csv(CSV_PATH)

# REQUIRED columns (spelling must match)
required_cols = ["Name", "Address", "Type", "Description", "Image_URL"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Missing column in CSV: {col}. Your headers must be: {required_cols}")

# =========================
# 5) TEST WITH 2–3 FIRST (recommended)
# =========================
# Uncomment to test small batch:
# df = df.head(3)

# =========================
# 6) GEOCODE ALL LOCATIONS
# =========================
lat_list, lon_list = [], []

for _, row in df.iterrows():
    address = row["Address"]
    lat, lon = geocode_address(address, ACCESS_TOKEN)
    lat_list.append(lat)
    lon_list.append(lon)

df["Latitude"] = lat_list
df["Longitude"] = lon_list

# Drop any that didn't geocode
df = df.dropna(subset=["Latitude", "Longitude"]).copy()

if df.empty:
    raise ValueError("No rows geocoded successfully. Check token + addresses.")

# =========================
# 7) CREATE MAP (CUSTOM MAPBOX BASEMAP)
# =========================
center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles=tiles,
    attr="Mapbox"
)

# =========================
# 8) COLOR/SYMBOL BY TYPE
# =========================
# Folium allowed colors:
# red, blue, green, purple, orange, darkred, lightred, beige, darkblue,
# darkgreen, cadetblue, darkpurple, white, pink, lightblue, lightgreen,
# gray, black, lightgray

type_to_color = {
    "Restaurant": "pink",
    "Cafe": "orange",
    "School": "blue",
    "Park": "green",
    "Cultural": "purple",
    "Historical": "darkred",
    "Sports": "cadetblue",
    "Church": "darkpurple",
    "Shopping": "lightblue",
}

# =========================
# 9) ADD MARKERS + POPUPS (NAME + DESC + IMAGE)
# =========================
for _, row in df.iterrows():
    name = row["Name"]
    desc = row["Description"]
    loc_type = row["Type"]
    img_url = row["Image_URL"]

    lat = row["Latitude"]
    lon = row["Longitude"]

    color = type_to_color.get(loc_type, "gray")

    popup_html = f"""
    <div style="width:260px;">
        <h4 style="margin:0 0 6px 0;">{name}</h4>
        <p style="margin:0 0 8px 0;">{desc}</p>
        <img src="{img_url}" style="width:240px; border-radius:8px;" />
        <p style="margin:8px 0 0 0;"><em>Type: {loc_type}</em></p>
    </div>
    """

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

# =========================
# 10) SAVE HTML
# =========================
m.save(OUTPUT_HTML)
print(f"✅ Saved: {OUTPUT_HTML}")