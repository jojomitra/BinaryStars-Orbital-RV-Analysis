# streamlit_app.py

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import sys
import os

from rv_orbital_fitting_with_advanced_gui import readinp, readcsv_custom, fitorb, orbsave, orbplot_streamlit, orb
from orb6_loader import parse_orb6_table

# --- Load & cache the live ORB6 catalog (including StarRef) ---
@st.cache_data(show_spinner=False)
def load_published_orbits():
    df = parse_orb6_table()
    return df.set_index("StarRef", drop=False)

published_df = load_published_orbits()


# --- Redirect stdout to display logs ---
class StreamlitRedirect(io.StringIO):
    def __init__(self):
        super().__init__()
        self.output = ""

    def write(self, msg):
        self.output += msg

    def flush(self):
        pass

# --- Streamlit App Layout ---
st.title("Python Implementation of Tokovinin's Binary Star ORBITX Code")
st.markdown("""Python Implementation of Tokovinin’s original OrbitX code which helps calculate and display the orbital elements of binary star systems. 
            This version has been improved and made more useful by 
            Prof. Mashhoor Al-Wardat and Dr. Mohammed Hussien Talafha.
            
            """)
st.markdown("Upload a `.inp or.csv` file and run the orbital fitting process below.")

# HM:--- Step 0: Optionally overlay a published ORB6 orbit ------------
if published_df.empty:
    st.subheader("Step 0: Overlay a published ORB6 orbit (optional)")
    st.warning("⚠️ No ORB6 data found (orb6.txt is missing or empty). Skipping overlay.")
    el_old = None
else:
    st.subheader("Step 0: Overlay a published ORB6 orbit (optional)")
    starref_list = [""] + published_df["StarRef"].tolist()
    selected_starref = st.selectbox("Pick a published REF code from ORB6:", starref_list)

    if selected_starref:
        row = published_df.loc[selected_starref]
        starid = row["StarID"]
        el_old = np.zeros(10)
        el_old[0] = float(row["P"])
        el_old[1] = float(row["T"])
        el_old[2] = float(row["e"])
        el_old[3] = float(row["a"])
        el_old[4] = float(row["Omega"])
        el_old[5] = float(row["omega"])
        el_old[6] = float(row["i"])
        el_old[7:10] = 0.0   # no published RV data → K1=K2=V0=0

        st.markdown(
            f"Overlaying published orbit for **REF {selected_starref}** (WDS {starid})<br>"
            f"P={el_old[0]:.4f}, T={el_old[1]:.4f}, e={el_old[2]:.4f}, a={el_old[3]:.4f},<br>"
            f"Ω={el_old[4]:.2f}, ω={el_old[5]:.2f}, i={el_old[6]:.2f}",
            unsafe_allow_html=True
        )
    else:
        el_old = None
# HM:--- End Step 0 ---------------------------------------------------



# --- Input file selection ---
st.subheader("Step 1: Select or Upload an File")

example_files = [
    "GL765_Test1.inp",
    "HD_New.inp",
    "HIP12780 _FIN379_Parallax1.inp",
    "HIP51360.inp",
    "HIP53206.inp",
    "HIP72217_parallax1.inp",
    "HIP72217_parallax2.inp"
]

use_example = st.checkbox("Use any one of the preloaded example files to visualise")

st.markdown("Link to the Example Input Files https://github.com/mtalafha90/Input_tutorials_RV_Orbits") 

uploaded_file = None
selected_example = None

if use_example:
    selected_example = st.selectbox("Choose an example .inp file:", example_files)
else:
    uploaded_file = st.file_uploader("Choose an .inp or.csv file", type=["inp","csv"])
# End Change1 Made by HM (02/06/2025)


fix_params = st.multiselect(
    "Select parameters to **fix during fitting**:",
    ['P', 'T', 'e', 'a', 'W', 'w', 'i', 'K1', 'K2', 'V0'],
    default=['K1', 'K2', 'V0']
)

run = st.button("Run Orbital Fit")

if (uploaded_file or selected_example) and run:
        with st.spinner("Running orbital fitting..."):
            os.makedirs("temp_data", exist_ok=True)
            # Decide file source
            if uploaded_file:
                path = os.path.join("temp_data", uploaded_file.name)
                with open(path, "wb") as f:
                    f.write(uploaded_file.read())
            elif selected_example:
                # Set absolute path for local example
                source_path = os.path.join("input_data", selected_example)
                path = os.path.join("temp_data", selected_example)
                os.makedirs("temp_data", exist_ok=True)
                with open(source_path, "rb") as src, open(path, "wb") as dst:
                    dst.write(src.read())
            buffer = StreamlitRedirect()
            sys.stdout = buffer
            sys.stderr = buffer
            try:
                if path.endswith(".csv"):
                    readcsv_custom(path)
                else:
                    readinp(path)
                orb.fixel = np.ones(10, dtype=int)
                for i, name in enumerate(orb.elname):
                    if name in fix_params:
                        orb.fixel[i] = 0
                fitorb()
                orbsave()
                st.subheader("Process Output Log")
                st.text(buffer.output)
                st.subheader("Visual Orbit")
                figs = orbplot_streamlit(el_old=el_old)
                for fig in figs:
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
# End Change2 Made by HM (02/06/2025)

