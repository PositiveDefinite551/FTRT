import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv
from Backend.process_echr_application_file import process_echr_application_form
load_dotenv()

#st.image("image.png")
st.title("European court of human rights application")
st.markdown(" This tool analyses European Court of Human Rights (ECHR) application")


st.sidebar.header("Settings")
enable_logs = st.sidebar.checkbox("Show processingg logs", value=True)

uploaded_file = st.file_uploader("Upload ECHR application PDF", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

if st.button("Analyse Application"):
    with st.spinner("Analysing..."):
        try: 
            # Call Backend get `results`
            results = process_echr_application_form(tmp_file_path, "Backend/prompts.json", enable_logs=enable_logs)
            st.success("Analysis Complete.")
            tab1, tab2 = st.tabs(["Results", "Raw Data"])
            with tab1:
                    # Display results from Json
                    valid_data = results.get("success_response_json", {})
                    
                    for section_name, fields in valid_data.items():
                        with st.expander(f"Section: {section_name}"):
                            if isinstance(fields, dict):
                                for field, details in fields.items():
                                    # See the structure in README.md
                                    st.subheader(f"Field: {field}")
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("**Given Value:**")
                                        st.info(details.get("given_value", "N/A"))
                                    with col2:
                                        st.write("**Corrected/Suggested:**")
                                        st.success(details.get("corrected_value", "N/A"))
                                    
                                    st.warning(f"**Issue:** {details.get('problem_in_given_value', 'None')}")
                                    st.write(f"*Summary:* {details.get('verification_summary', '')}")
                                    st.divider()
            with tab2:
                st.json(results)

        except Exception as e:
            st.error(f"Something went wrong: {e} ")
        finally:
            os.remove(tmp_file_path)
else:
    st.info("Upload PDF to begin.")
