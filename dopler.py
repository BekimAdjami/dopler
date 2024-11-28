import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Title and Sidebar
st.title("Doppler Ultrasound Analyzer (Right and Left Sides)")
st.sidebar.header("Data Input")
input_option = st.sidebar.radio("Choose Input Method:", ("Manual Entry", "Upload CSV"))

# Functions for Calculations
def calculate_ratios(psv_ica, psv_cca):
    """Calculate ICA/CCA Velocity Ratio"""
    if psv_cca > 0:
        return psv_ica / psv_cca
    else:
        return None

def calculate_mean_velocity(psv, edv):
    """Calculate Mean Velocity (Time-Averaged Maximum Velocity)"""
    if psv > 0 and edv >= 0:
        return (psv + (2 * edv)) / 3
    else:
        return None

def calculate_lindegaard_ratio(mean_acm, psv_cca):
    """Calculate Lindegaard Ratio"""
    if mean_acm is not None and psv_cca > 0:
        return mean_acm / psv_cca
    else:
        return None

def interpret_ratio(ratio):
    """Interpret ICA/CCA Ratio"""
    if ratio is None:
        return "Invalid data: cannot interpret ratio."
    if ratio > 4.0:
        return "Severe Stenosis (>70%)"
    elif ratio > 2.0:
        return "Moderate Stenosis (50-69%)"
    else:
        return "Normal"

def generate_report(data):
    """Generate a downloadable Excel report"""
    buffer = BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    data.to_excel(writer, sheet_name="Doppler Data", index=False)
    writer.save()
    buffer.seek(0)
    return buffer

# Manual Entry
if input_option == "Manual Entry":
    st.subheader("Enter Doppler Data (Right and Left Sides)")

    # Right Side
    st.write("**Right Side**")
    psv_ica_r = st.number_input("Right ICA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_ica_r")
    edv_ica_r = st.number_input("Right ICA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_ica_r")
    psv_cca_r = st.number_input("Right CCA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_cca_r")
    edv_cca_r = st.number_input("Right CCA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_cca_r")
    psv_acm_r = st.number_input("Right MCA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_acm_r")
    edv_acm_r = st.number_input("Right MCA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_acm_r")

    # Left Side
    st.write("**Left Side**")
    psv_ica_l = st.number_input("Left ICA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_ica_l")
    edv_ica_l = st.number_input("Left ICA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_ica_l")
    psv_cca_l = st.number_input("Left CCA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_cca_l")
    edv_cca_l = st.number_input("Left CCA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_cca_l")
    psv_acm_l = st.number_input("Left MCA Peak Systolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="psv_acm_l")
    edv_acm_l = st.number_input("Left MCA End Diastolic Velocity (cm/s)", min_value=0.0, format="%.2f", key="edv_acm_l")

    # Perform Calculations
    data = {
        "Side": ["Right", "Left"],
        "ICA/CCA Ratio": [
            calculate_ratios(psv_ica_r, psv_cca_r), 
            calculate_ratios(psv_ica_l, psv_cca_l)
        ],
        "MCA Mean Velocity": [
            calculate_mean_velocity(psv_acm_r, edv_acm_r), 
            calculate_mean_velocity(psv_acm_l, edv_acm_l)
        ],
        "Lindegaard Ratio": [
            calculate_lindegaard_ratio(calculate_mean_velocity(psv_acm_r, edv_acm_r), psv_cca_r),
            calculate_lindegaard_ratio(calculate_mean_velocity(psv_acm_l, edv_acm_l), psv_cca_l),
        ],
    }

    results = pd.DataFrame(data)
    results["Interpretation"] = results["ICA/CCA Ratio"].apply(interpret_ratio)

    # Display Results
    st.subheader("Calculated Results")
    st.write(results)

    # Visualizations
    st.subheader("Visualizations")
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))

    # Bar Chart for PSV
    arteries = ["ICA", "CCA", "MCA"]
    right_psv = [psv_ica_r, psv_cca_r, psv_acm_r]
    left_psv = [psv_ica_l, psv_cca_l, psv_acm_l]
    ax[0, 0].bar(arteries, right_psv, color="blue", alpha=0.6, label="Right Side")
    ax[0, 0].bar(arteries, left_psv, color="orange", alpha=0.6, label="Left Side")
    ax[0, 0].set_title("Peak Systolic Velocities (Right vs Left)")
    ax[0, 0].set_ylabel("Velocity (cm/s)")
    ax[0, 0].legend()

    # Line Plot for Mean Velocities
    mean_right = [calculate_mean_velocity(psv_ica_r, edv_ica_r), calculate_mean_velocity(psv_cca_r, edv_cca_r), calculate_mean_velocity(psv_acm_r, edv_acm_r)]
    mean_left = [calculate_mean_velocity(psv_ica_l, edv_ica_l), calculate_mean_velocity(psv_cca_l, edv_cca_l), calculate_mean_velocity(psv_acm_l, edv_acm_l)]
    ax[0, 1].plot(arteries, mean_right, marker="o", label="Right Mean Velocities", color="blue")
    ax[0, 1].plot(arteries, mean_left, marker="o", label="Left Mean Velocities", color="orange")
    ax[0, 1].set_title("Mean Velocities (Right vs Left)")
    ax[0, 1].set_ylabel("Velocity (cm/s)")
    ax[0, 1].legend()

    # Scatter Plot for MCA Mean Velocities
    ax[1, 0].scatter([1, 2], results["MCA Mean Velocity"], color=["blue", "orange"], label=["Right", "Left"])
    ax[1, 0].set_title("MCA Mean Velocities")
    ax[1, 0].set_xticks([1, 2])
    ax[1, 0].set_xticklabels(["Right", "Left"])
    ax[1, 0].set_ylabel("Velocity (cm/s)")

    # Pie Chart for Interpretation Distribution
    interpretation_counts = results["Interpretation"].value_counts()
    ax[1, 1].pie(interpretation_counts, labels=interpretation_counts.index, autopct="%1.1f%%", colors=["green", "yellow", "red"])
    ax[1, 1].set_title("Interpretation Distribution")

    st.pyplot(fig)

# CSV Upload
elif input_option == "Upload CSV":
    st.subheader("Upload Doppler Data CSV")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Uploaded Data", data)

        # Perform Calculations on Uploaded Data
        data["ICA/CCA Ratio"] = data.apply(lambda row: calculate_ratios(row["PSV_ICA"], row["PSV_CCA"]), axis=1)
        data["MCA Mean Velocity"] = data.apply(lambda row: calculate_mean_velocity(row["PSV_MCA"], row["EDV_MCA"]), axis=1)
        data["Lindegaard Ratio"] = data.apply(lambda row: calculate_lindegaard_ratio(row["MCA Mean Velocity"], row["PSV_CCA"]), axis=1)
        data["Interpretation"] = data["ICA/CCA Ratio"].apply(interpret_ratio)
        st.write("Calculated Results", data)

        # Download Button
        report = generate_report(data)
        st.download_button(label="Download Results as Excel", data=report, file_name="doppler_results.xlsx", mime="application/vnd.ms-excel")
