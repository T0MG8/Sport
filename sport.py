import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time  # Voor vertraging bij succesbericht

# Laad het Excel-bestand (of maak een nieuwe DataFrame als het niet bestaat)
excel_bestand = 'Data sporten.xlsx'
if os.path.exists(excel_bestand):
    df = pd.read_excel(excel_bestand)
else:
    df = pd.DataFrame(columns=['Datum', 'Oefening', 'Hoevaak'])

# Functie om gegevens op te slaan
def save_to_excel(data):
    global df
    df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    df.to_excel(excel_bestand, index=False)

# Sidebar navigatie
st.sidebar.title("Navigatie")
if 'page' not in st.session_state:
    st.session_state.page = "Home"

page = st.sidebar.radio("Kies een optie", ["Home", "Formulier"], index=["Home", "Formulier"].index(st.session_state.page))

# Oefening- en herhalingsopties
oefeningen = ['Dumbell Press', 'Zittend Roeien Cables', 'Incline Bench Press', 'Tricep Extencion']
hoevaak_opties = ['3x 10', '3x 9', '3x 8', '3x 7', '3x 6']

if page == "Formulier":
    st.title('Formulier om Excel-bestand bij te werken')

    # Standaard datum
    vandaag = datetime.today().strftime('%Y-%m-%d')
    Datum = st.text_input('Datum', value=vandaag)

    # Initialiseer lijst voor oefeningen
    if 'oefeningen' not in st.session_state:
        st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0]}]

    # Toon de dynamische invoervelden
    for i, oefening in enumerate(st.session_state.oefeningen):
        col1, col2 = st.columns([2, 1])
        with col1:
            oefening['oef'] = st.selectbox(f'Oefening {i+1}', oefeningen, index=oefeningen.index(oefening['oef']), key=f'oef_{i}')
        with col2:
            oefening['rep'] = st.selectbox(f'Hoevaak {i+1}', hoevaak_opties, index=hoevaak_opties.index(oefening['rep']), key=f'rep_{i}')

    # Knoppen: Extra oefening & Opslaan
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button('➕ Extra oefening'):
            st.session_state.oefeningen.append({'oef': oefeningen[0], 'rep': hoevaak_opties[0]})
            st.rerun()

    with col2:
        if st.button('✅ Opslaan'):
            if Datum and all(oef['oef'] and oef['rep'] for oef in st.session_state.oefeningen):
                data = [{'Datum': Datum, 'Oefening': oef['oef'], 'Hoevaak': oef['rep']} for oef in st.session_state.oefeningen]
                save_to_excel(data)
                st.success('✅ Gegevens succesvol opgeslagen!')

                # Wacht 3 seconden voordat de pagina verandert
                time.sleep(3)

                # Reset en terug naar Home
                st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0]}]
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error('⚠️ Vul alle velden in!')

else:
    st.title("Welkom op de Homepagina")
    st.write("Klik op de 'Formulier' optie in de sidebar om gegevens in te vullen.")
