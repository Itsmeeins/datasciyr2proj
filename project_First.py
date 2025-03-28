import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Load Data
def load_data():
    file_path = "df_corrected_by_province.csv"  # Ensure the file is uploaded in the Streamlit app
    df = pd.read_csv(file_path)
    return df

df = load_data()

# Define darker cluster colors
cluster_colors = {
    "Cluster 0": "#8B0000",
    "Cluster 1": "#006400",
    "Cluster 2": "#B8860B",
    "Cluster 3": "#800080"
}

# Define property types based on KMeans clusters (อิงจาก insight ล่าสุด)
property_types = {
    "All": "ทั้งหมด",
    "Cluster 0": "บ้านราคาถูกมาก / ไม่แนะนำลงทุน",
    "Cluster 1": "คอนโด / ทาวน์โฮม",
    "Cluster 2": "บ้านเดี่ยว / โครงการครบวงจร",
    "Cluster 3": "บ้านราคาถูก / ร่วมรัฐ"
}


# Streamlit UI
st.title("Housing Investment Clustering Map")
st.write("This map shows the clustered areas based on housing demand.")

# Dropdown for selecting property type
selected_property = st.selectbox("Select a Property Type for Investment", list(property_types.values()))

# Dropdown for selecting province
provinces = ["All"] + sorted(df["Province"].unique().tolist())
selected_province = st.selectbox("Select a Province", provinces)

# Filter clusters based on selection
if selected_property == "ทั้งหมด":
    filtered_df = df.copy()
else:
    selected_clusters = [k for k, v in property_types.items() if v == selected_property]
    filtered_df = df[df["KMeans_Cluster"].astype(str).isin([s.split()[-1] for s in selected_clusters])]

# Apply province filter if a specific province is selected
if selected_province != "All":
    filtered_df = filtered_df[filtered_df["Province"] == selected_province]

# Calculate map center dynamically
if selected_province == "All":
    map_center = [df["LAT"].mean(), df["LONG"].mean()]
else:
    province_df = df[df["Province"] == selected_province]
    map_center = [province_df["LAT"].mean(), province_df["LONG"].mean()]

# Initialize Folium Map centered on selected province
m = folium.Map(
    location=map_center, 
    zoom_start=10, 
    control_scale=True,
    width="100%", 
    height="100%",
    fullscreen_control=True
)

# Add Markers to Map with larger size
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row["LAT"], row["LONG"]],
        radius=8,  # Bigger marker size
        color=cluster_colors.get(row["KMeans_Cluster"], "#800080"),  # Default dark purple
        fill=True,
        fill_color=cluster_colors.get(row["KMeans_Cluster"], "#800080"),
        fill_opacity=0.85,  # Adjust opacity for better visibility
        popup=f"Location: {row['Sub District']}, {row['Province']}\nCluster: {row['KMeans_Cluster']}"
    ).add_to(m)

# Display Map inside a container to ensure full width
with st.container():
    folium_static(m, width=1000, height=600)  # Adjust height if needed

# Add Cluster Legend with dark colors
st.markdown("### 🔹 Cluster Legend (คำอธิบายสี) 🔹")
legend_html = """
<div style="display: flex; flex-wrap: wrap; gap: 15px;">
    <div style="display: flex; align-items: center;">
        <div style="width: 20px; height: 20px; background-color: #8B0000; margin-right: 10px;"></div>
        <span>Cluster 0: บ้านราคาถูกมาก / ไม่แนะนำลงทุน</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width: 20px; height: 20px; background-color: #006400; margin-right: 10px;"></div>
        <span>Cluster 1: คอนโด / ทาวน์โฮม</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width: 20px; height: 20px; background-color: #B8860B; margin-right: 10px;"></div>
        <span>Cluster 2: บ้านเดี่ยว / โครงการครบวงจร</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width: 20px; height: 20px; background-color: #800080; margin-right: 10px;"></div>
        <span>Cluster 3: บ้านราคาถูก / โครงการร่วมรัฐ</span>
    </div>
</div>
"""

st.markdown(legend_html, unsafe_allow_html=True)
