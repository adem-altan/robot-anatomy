import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- Config ---
RESULTS_DIR = "data/results"

# --- Load available result files ---
@st.cache_data
def load_csv_files():
    csv_files = {
        f.replace("_results.csv", ""): os.path.join(RESULTS_DIR, f)
        for f in os.listdir(RESULTS_DIR)
        if f.endswith("_results.csv")
    }
    return csv_files

# --- Load Data ---
def load_data(file_path):
    return pd.read_csv(file_path)

# --- Streamlit UI ---
st.set_page_config(page_title="Sensor Evaluation Dashboard", layout="centered")
st.title("📊 Depth Sensor Evaluation Dashboard")

csv_files = load_csv_files()
materials = list(csv_files.keys())

selected = st.multiselect("Select materials to compare:", materials, default=materials[:1])

if selected:
    dataframes = [load_data(csv_files[m]) for m in selected]

    # Determine global distance range
    all_distances = pd.concat([df["expected_distance_m"] for df in dataframes])
    min_dist = float(all_distances.min())
    max_dist = float(all_distances.max())

    # Add distance slider
    st.sidebar.subheader("🔍 Filter by Distance Range")
    dist_range = st.sidebar.slider("Distance (m)", min_value=round(min_dist, 3), max_value=round(max_dist, 3),
                                   value=(round(min_dist, 3), round(max_dist, 3)), step=0.005)

    # Filter data
    filtered_dfs = [
        df[(df["expected_distance_m"] >= dist_range[0]) & (df["expected_distance_m"] <= dist_range[1])]
        for df in dataframes
    ]

    # Summary stats
    st.subheader("📊 Summary Statistics")
    for mat, df in zip(selected, filtered_dfs):
        st.markdown(f"**{mat.capitalize()}**")
        st.write({
            "Avg RMSE (mm)": round(df["rmse_mm"].mean(), 2),
            "Min RMSE (mm)": round(df["rmse_mm"].min(), 2),
            "Max RMSE (mm)": round(df["rmse_mm"].max(), 2),
            "Avg Completeness (%)": round(df["completeness_percent"].mean(), 2)
        })

    # --- Combined Comparison Graphs ---
    st.subheader("📊 RMSE vs Distance (All Materials)")
    combined_rmse_df = pd.concat(
        [df.assign(Material=label) for df, label in zip(filtered_dfs, selected)]
    )
    fig_rmse = px.line(combined_rmse_df, x="expected_distance_m", y="rmse_mm", color="Material",
                    labels={"expected_distance_m": "Distance (m)", "rmse_mm": "RMSE (mm)"},
                    title="RMSE vs Distance (Comparison)")
    st.plotly_chart(fig_rmse, use_container_width=True)

    st.subheader("📊 Completeness vs Distance (All Materials)")
    fig_comp = px.line(combined_rmse_df, x="expected_distance_m", y="completeness_percent", color="Material",
                    labels={"expected_distance_m": "Distance (m)", "completeness_percent": "Completeness (%)"},
                    title="Completeness vs Distance (Comparison)")
    st.plotly_chart(fig_comp, use_container_width=True)

    # --- Individual Graphs (Optional) ---
    st.subheader("📉 Individual Material Graphs")
    for df, label in zip(filtered_dfs, selected):
        st.markdown(f"### {label.capitalize()}")

        fig = px.line(df, x="expected_distance_m", y="rmse_mm", title=f"RMSE - {label}",
                    labels={"expected_distance_m": "Distance (m)", "rmse_mm": "RMSE (mm)"})
        st.plotly_chart(fig, use_container_width=True)

        fig = px.line(df, x="expected_distance_m", y="completeness_percent", title=f"Completeness - {label}",
                    labels={"expected_distance_m": "Distance (m)", "completeness_percent": "Completeness (%)"})
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select at least one material to view graphs.")
