import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="TURJALIN - Polres Pelabuhan Belawan", layout="wide"
)

st.title("🚨 TURJALIN - POLRES PELABUHAN BELAWAN")
st.subheader("Sistem Pemetaan Laka Lantas & Ploting Personel Turjakwali")

# Upload Data Master Laka Lantas
st.sidebar.header("📁 Upload Data Master")
uploaded_file = st.sidebar.file_uploader(
    "Pilih File Excel/CSV", type=["xlsx", "xls", "csv"]
)

df_valid = None

if uploaded_file is not None:
  try:
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.sidebar.success("Data Master berhasil dimuat!")

    # Deteksi otomatis nama kolom Koordinat (Latitude & Longitude)
    lat_col = next(
        (
            c
            for c in df.columns
            if c.strip().upper() in ["LATITUDE", "LATTITUDE", "LAT"]
        ),
        None,
    )
    lon_col = next(
        (
            c
            for c in df.columns
            if c.strip().upper() in ["LONGITUDE", "LONG", "LON"]
        ),
        None,
    )

    if lat_col and lon_col:
      df["LATITUDE"] = pd.to_numeric(df[lat_col], errors="coerce")
      df["LONGITUDE"] = pd.to_numeric(df[lon_col], errors="coerce")
      df_valid = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    else:
      st.error(
          "Kolom Latitude/Longitude tidak ditemukan! Periksa kembali nama kolom"
          " di file Excel Anda."
      )

  except Exception as e:
    st.error(f"Kesalahan memproses data: {e}")

# Filter Wilayah & Penanganan Tampilan Utama
if df_valid is not None and not df_valid.empty:
  st.sidebar.header("🔍 Filter Wilayah & Kejadian")

  # Cek kolom kecamatan jika ada
  kec_col = next(
      (c for c in df_valid.columns if c.strip().upper() == "KECAMATAN"), None
  )
  if kec_col:
    kec_list = ["Semua"] + list(df_valid[kec_col].dropna().unique())
    selected_kec = st.sidebar.selectbox("Kecamatan", kec_list)
    if selected_kec != "Semua":
      df_filtered = df_valid[df_valid[kec_col] == selected_kec]
    else:
      df_filtered = df_valid
  else:
    df_filtered = df_valid

  st.write(
      f"Total Data Kejadian Valid: **{len(df_filtered)}** titik koordinat."
  )

  # Tampilkan Peta Sederhana
  m = folium.Map(
      location=[df_filtered["LATITUDE"].mean(), df_filtered["LONGITUDE"].mean()],
      zoom_start=12,
  )
  for _, row in df_filtered.iterrows():
    folium.Marker(
        location=[row["LATITUDE"], row["LONGITUDE"]],
        popup=row.get("KETERANGAN", "Titik Laka Lantas"),
    ).add_to(m)

  st_folium(m, width=700, height=500)

else:
  st.info(
      "Silakan unggah Data Master Laka Lantas (.xlsx / .csv) melalui menu di"
      " samping kiri."
  )
