import streamlit as st
import pandas as pd
import os
from datetime import datetime  # Import voor de datumfunctie

# Laad het Excel-bestand (als het nog niet bestaat, maak het dan)
excel_bestand = 'Data sporten.xlsx'

# Controleer of het bestand al bestaat
if os.path.exists(excel_bestand):
    df = pd.read_excel(excel_bestand)
else:
    # Maak een lege DataFrame met de juiste kolommen als het bestand niet bestaat
    df = pd.DataFrame(columns=['Datum', 'Oefening', 'Bericht'])

# Functie om de gegevens op te slaan in het Excel-bestand
def save_to_excel(Datum, oefening, bericht):
    global df  # Zorg ervoor dat we de globale df gebruiken
    new_data = pd.DataFrame([[Datum, oefening, bericht]], columns=['Datum', 'Oefening', 'Bericht'])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(excel_bestand, index=False)

# Sidebar knop voor navigatie
st.sidebar.title("Navigatie")
if 'page' not in st.session_state:
    st.session_state.page = "Home"  # Standaard pagina is "Home"

# Radio button voor navigatie
page = st.sidebar.radio("Kies een optie", ["Home", "Formulier"], index=["Home", "Formulier"].index(st.session_state.page))

# Lijst met opties voor oefening
oefeningen = ['Dumbell Press', 'Zittend Roeien Cables', 'Incline Bench Press', 'Tricep Extencion']

# Als de gebruiker 'Formulier' kiest, toon de formulier sectie
if page == "Formulier":
    st.title('Formulier om Excel-bestand bij te werken')

    # Stel standaard de datum van vandaag in
    vandaag = datetime.today().strftime('%Y-%m-%d')  # Formatteer als YYYY-MM-DD

    if 'Datum' not in st.session_state:
        st.session_state.Datum = vandaag  # Standaardwaarde is de datum van vandaag

    # Zorg ervoor dat 'oefening' een geldige standaardwaarde heeft
    if 'oefening' not in st.session_state or st.session_state.oefening not in oefeningen:
        st.session_state.oefening = oefeningen[0]  # Eerste optie als standaardwaarde

    if 'bericht' not in st.session_state:
        st.session_state.bericht = ""

    # Invoervelden
    Datum = st.text_input('Datum', value=st.session_state.Datum)  # Datum staat standaard op vandaag

    # Dropdownmenu voor 'Oefening'
    oefening = st.selectbox('Oefening', oefeningen, index=oefeningen.index(st.session_state.oefening))

    bericht = st.text_area('Bericht', value=st.session_state.bericht)

    # Wanneer de knop wordt ingedrukt, sla de gegevens op in het Excel-bestand
    if st.button('Opslaan'):
        if Datum and oefening and bericht:
            save_to_excel(Datum, oefening, bericht)
            st.success('Gegevens succesvol opgeslagen in Excel!')

            # Leeg de velden na het opslaan
            st.session_state.Datum = vandaag  # Na opslaan blijft de datum van vandaag staan
            st.session_state.oefening = oefeningen[0]  # Zet terug naar de standaardoptie
            st.session_state.bericht = ""

            # Zet de pagina terug naar 'Home' en herlaad de app
            st.session_state.page = "Home"
            st.experimental_rerun()
        else:
            st.error('Vul alle velden in!')

# Als de gebruiker 'Home' kiest, toon een welkomstbericht
else:
    st.title("Welkom op de Homepagina")
    st.write("Klik op de 'Formulier' optie in de sidebar om gegevens in te vullen.")