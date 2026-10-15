import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

st.set_page_config(page_title="TURJALIN - Polres Pelabuhan Belawan", layout="wide")

st.title("🚨 TURJALIN - POLRES PELABUHAN BELAWAN")
st.subheader("Sistem Pemetaan Laka Lantas & Ploting Personel Turjakwali")

# Upload Data Master Laka Lantas
st.sidebar.header("📁 Upload Data Master")
uploaded_file = st.sidebar.file_uploader("Pilih File Excel/CSV", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.sidebar.success("Data Master berhasil dimuat!")
        
        # Validasi Kolom Koordinat
        df['LATTITUDE'] = pd.to_numeric(df['LATTITUDE'], errors='coerce')
        df['LONGITUDE'] = pd.to_numeric(df['LONGITUDE'], errors='coerce')
        df_valid = df.dropna(subset=['LATTITUDE', 'LONGITUDE'])

        # Filter Operasional
        st.sidebar.header("🔍 Filter Wilayah & Kejadian")
        kec_list = ["Semua"] + list(df_valid['KECAMATAN'].dropna().unique())
        selected_kec = st.sidebar.selectbox("Kecamatan", kec_list)
        
        jenis_list = ["Semua"] + list(df_valid['JENIS_LAKA'].dropna().unique())
        selected_jenis = st.sidebar.selectbox("Jenis Laka", jenis_list)

        filtered_df = df_valid.copy()
        if selected_kec != "Semua":
            filtered_df = filtered_df[filtered_df['KECAMATAN'] == selected_kec]
        if selected_jenis != "Semua":
            filtered_df = filtered_df[filtered_df['JENIS_LAKA'] == selected_jenis]

        # Ringkasan Statistik
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Laka Lantas", len(filtered_df))
        c2.metric("Total Kerugian Material", f"Rp {filtered_df['KERMAT'].sum():,.0f}" if 'KERMAT' in filtered_df else "0")
        c3.metric("Korban Jiwa", int(filtered_df['KERUGIAN_JIWA'].sum()) if 'KERUGIAN_JIWA' in filtered_df else "0")
        c4.metric("Titik Rawan (Blackspot)", len(filtered_df['ALAMAT_TKP'].unique()))

        st.markdown("---")

        # Peta Sebaran Hotspot
        st.header("📍 Peta Sebaran Titik Laka Lantas")
        center_lat = filtered_df['LATTITUDE'].mean() if not filtered_df.empty else 3.7800
        center_long = filtered_df['LONGITUDE'].mean() if not filtered_df.empty else 98.6800

        m = folium.Map(location=[center_lat, center_long], zoom_start=13)
        
        heat_data = [[row['LATTITUDE'], row['LONGITUDE']] for _, row in filtered_df.iterrows()]
        if heat_data:
            HeatMap(heat_data, radius=15).add_to(m)

        for _, row in filtered_df.iterrows():
            popup_text = f"""
            <b>ID:</b> {row.get('ID_KEJADIAN', '-')}<br>
            <b>Waktu:</b> {row.get('TANGGAL_KEJADIAN', '-')} ({row.get('JAM_KEJADIAN', '-')})<br>
            <b>TKP:</b> {row.get('ALAMAT_TKP', '-')}<br>
            <b>Penyebab:</b> {row.get('PENYEBAB', '-')}<br>
            <b>Jenis:</b> {row.get('JENIS_LAKA', '-')}
            """
            folium.Marker(
                location=[row['LATTITUDE'], row['LONGITUDE']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color="red", icon="warning", prefix="fa")
            ).add_to(m)

        st_folium(m, width=1100, height=500)

        # Rekomendasi Ploting Personel
        st.header("👮 Rekomendasi Ploting Personel Turjakwali")
        st.write("Daftar lokasi prioritas penempatan personel berdasarkan tingkat kerawanan laka:")
        
        ploting_df = filtered_df.groupby(['KECAMATAN', 'KELURAHAN', 'ALAMAT_TKP']).size().reset_index(name='Jumlah Kejadian')
        ploting_df = ploting_df.sort_values(by='Jumlah Kejadian', ascending=False)
        st.dataframe(ploting_df, use_container_width=True)

    except Exception as e:
        st.error(f"Kesalahan memproses data: {e}")
else:
    st.info("Silakan unggah Data Master Laka Lantas melalui menu di samping kiri.")
