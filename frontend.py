import streamlit as st

st.image("image.png")
st.title("European court of human rights application")

with st.sidebar:
    st.write("A. The Applicant")
    st.write("B. State(s) against which the application is directed")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True, horizontal_alignment="left", width="stretch"):
        
        st.header("A.1. The individual")

        Name = st.text_input("1. Surname")
        Surname = st.text_input("2. First name(s)")
        date_of_birth = st.date_input("3. Date of birth")
        place_of_birth = st.text_input("4. Place of Birth")
        nationality = st.text_input("4. Nationality")
        addres = st.text_input("6. Adress")
        telephone = st.text_input("7. Telephone (including international dialling code)")
        email = st.text_input("8. Email (if any)")
        sex = st.multiselect("9. Sex", ["male", "female"], max_selections=1)

    with col2:
        with st.container(border=True, horizontal_alignment="left", width="stretch"):
            
            st.header("A.2. The Organisation")

            name = st.text_input("10. Name")
            identiification_number = st.text_input("11. Identifiication number (if any)")
            date_of_registration_or_incorporation = st.date_input("12. Date of regsitration or incorporation (if any)")
            activity = st.text_input("13. Activity")
            registered_adress = st.text_input("14. Registered_adress")

st.header("B. State(s) against which the application is directed")

states = st.text_input("State(s) against which the application is directed")

st.header("C. Representative(s) of the individual applicant")

col3, col4 = st.columns(2)


with col3:
    with st.container(border=True, horizontal_alignment="left", width="stretch"):
        
        st.header("C.1")
        a = st.text_input("### TODO", key="1")

with col4:
    with st.container(border=True, horizontal_alignment="left", width="stretch"):
        st.header("C.2.")
        b = st.text_input("### TODO", key="2")

            