import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv
from Backend.process_echr_application_file import process_echr_application_form

load_dotenv()

st.title("European court of human rights application")
st.markdown("This tool analyses European Court of Human Rights (ECHR) application")

st.sidebar.header("Settings")
enable_logs = st.sidebar.checkbox("Show processing logs", value=True)

uploaded_file = st.file_uploader("Upload ECHR application PDF", type="pdf")
tmp_file_path = None

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name


def render_value(value):
    if isinstance(value, (dict, list)):
        st.json(value)
    elif value is None:
        st.write("N/A")
    else:
        st.write(str(value))


def render_fields(data, level=0):
    if isinstance(data, dict):
        for key, value in data.items():

            # Field result object
            if isinstance(value, dict) and any(
                k in value for k in [
                    "given_value",
                    "corrected_value",
                    "problem_in_given_value",
                    "verification_summary",
                    "confidence"
                ]
            ):
                st.subheader(f"Field: {key}")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Given Value:**")
                    render_value(value.get("given_value", "N/A"))

                with col2:
                    st.write("**Corrected/Suggested:**")
                    render_value(value.get("corrected_value", "N/A"))

                st.warning(f"**Issue:** {value.get('problem_in_given_value', 'None')}")
                st.write(f"*Summary:* {value.get('verification_summary', '')}")
                st.write(f"**Confidence:** {value.get('confidence', 'N/A')}")
                st.divider()

            # Nested section
            else:
                with st.expander(f"Section: {key}", expanded=level == 0):
                    render_fields(value, level + 1)

    else:
        render_value(data)


if st.button("Analyse Application"):
    if uploaded_file is None or tmp_file_path is None:
        st.error("Please upload a PDF first.")
    else:
        with st.spinner("Analysing..."):
            try:
                results = process_echr_application_form(
                    tmp_file_path,
                    "Backend/prompts.json",
                    enable_logs=enable_logs
                )

                # If backend returns JSON string, convert it to dict
                if isinstance(results, str):
                    results = json.loads(results)

                st.success("Analysis Complete.")

                tab1, tab2 = st.tabs(["Results", "Raw Data"])

                with tab1:
                    valid_data = results.get("success_response_json", {})
                    render_fields(valid_data)

                with tab2:
                    st.json(results)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

            finally:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
else:
    st.info("Upload PDF to begin.")