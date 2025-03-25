import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import plotly.express as px
import subprocess

# Laad het Excel-bestand (of maak een nieuwe DataFrame als het niet bestaat)
excel_bestand = 'Data sporten.xlsx'

# Als het bestand bestaat, lees dan alle bladen in, anders maak de lege dataframes
if os.path.exists(excel_bestand):
    df = pd.read_excel(excel_bestand, sheet_name=None)  # Lees alle bladen in als een dict
else:
    # Maak een nieuwe dictionary met de benodigde bladen als DataFrames
    df = {
        'Oefeningen': pd.DataFrame(columns=['Datum', 'Oefening', 'Hoevaak', 'Gewicht']),
        'Gewicht': pd.DataFrame(columns=['Datum', 'Gewicht', 'Gewichtmeting'])
    }

# Functie om gegevens op te slaan
def save_to_excel(data, sheet_name):
    global df
    if sheet_name not in df:
        # Maak een nieuw DataFrame aan als het blad nog niet bestaat
        df[sheet_name] = pd.DataFrame(columns=data[0].keys())
    
    # Voeg de nieuwe data toe aan het juiste blad
    df[sheet_name] = pd.concat([df[sheet_name], pd.DataFrame(data)], ignore_index=True)
    
    # Schrijf naar het Excel-bestand, meerdere bladen tegelijk
    with pd.ExcelWriter(excel_bestand, engine='xlsxwriter') as writer:
        for sheet, data_frame in df.items():
            data_frame.to_excel(writer, sheet_name=sheet, index=False)

# Functie voor synchronisatie naar GitHub
def sync_to_github():
    repo_path = '/pad/naar/jouw/repository'  # Het pad naar je Git-repository
    bestandsnaam = os.path.join(repo_path, 'Data sporten.xlsx')

    if os.path.exists(bestandsnaam):
        try:
            os.chdir(repo_path)
            subprocess.run(['git', 'add', bestandsnaam], check=True)
            commit_message = f"Update {bestandsnaam} op {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("✅ Gegevens succesvol gesynchroniseerd naar GitHub!")
        except subprocess.CalledProcessError as e:
            print(f"Fout bij Git-commando: {e}")
    else:
        print("⚠️ Het bestand bestaat niet.")

# Sidebar navigatie
st.sidebar.title("Navigatie")
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Voeg een nieuwe optie "Gewicht" toe
page = st.sidebar.radio("Kies een optie", ["Home", "Formulier", "Gewicht"], index=["Home", "Formulier", "Gewicht"].index(st.session_state.page))

# Oefening- en herhalingsopties
oefeningen = ['Dumbell Press', 'Zittend Roeien Cables', 'Incline Bench Press', 'Tricep Extencion', 'Lat Pull Down', 'Shoulder Press', 'Overhead Extencion', 'Dips voor Borst', 'Cable Crossover Flyes (Bank)', '']
hoevaak_opties = ['10x', '9x', '8x', '7x', '6x', '5x', '4x', '3x', '2x', '1x']
gewicht_opties = ['5kg', '10kg', '12kg', '14kg', '16kg', '18kg','20kg', '22kg', '24kg', '26kg', '28kg', '30kg', '32kg', '34kg', '36kg', '38kg', '40kg', '45kg', '50g', '55kg', '60kg', '70kg', '80kg', '90kg', '100kg', '110kg',' 120kg', '130kg','stand 1', 'stand 2', 'stand 3', 'stand 4', 'stand 5', 'stand 6', 'stand 7', 'stand 8', 'stand 9','stand 10', 'stand 11', 'stand 12','stand 13', 'stand 14', 'stand 15', 'stand 16', 'stand 17', 'stand 18', 'stand 19','stand 20','stand 21','stand 22','stand 23', 'stand 24', 'stand 25']

if page == "Formulier":
    st.title('Formulier om Excel-bestand bij te werken')

    # Standaard datum
    vandaag = datetime.today().strftime('%Y-%m-%d')
    Datum = st.text_input('Datum', value=vandaag)

    # Initialiseer lijst voor oefeningen, herhalingen en gewichten
    if 'oefeningen' not in st.session_state:
        st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]

    # Toon de dynamische invoervelden
    for i, oefening in enumerate(st.session_state.oefeningen):
        col1, col2, col3 = st.columns([2, 1, 1])  # Voeg een extra kolom voor gewicht toe
        with col1:
            oefening['oef'] = st.selectbox(f'Oefening {i+1}', oefeningen, index=oefeningen.index(oefening['oef']), key=f'oef_{i}')
        with col2:
            oefening['rep'] = st.selectbox(f'Hoevaak {i+1}', hoevaak_opties, index=hoevaak_opties.index(oefening['rep']), key=f'rep_{i}')
        with col3:  # Het nieuwe dropdownmenu voor gewicht
            oefening['gewicht'] = st.selectbox(f'Gewicht {i+1}', gewicht_opties, index=gewicht_opties.index(oefening['gewicht']), key=f'gewicht_{i}')

    # Knoppen: Extra oefening & Opslaan
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button('➕ Extra oefening'):
            st.session_state.oefeningen.append({'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]})
            st.rerun()

    with col2:
        if st.button('✅ Opslaan'):
            if Datum and all(oef['oef'] and oef['rep'] and oef['gewicht'] for oef in st.session_state.oefeningen):
                data = [{'Datum': Datum, 'Oefening': oef['oef'], 'Hoevaak': oef['rep'], 'Gewicht': oef['gewicht']} for oef in st.session_state.oefeningen]
                save_to_excel(data, 'Oefeningen')
                st.success('✅ Gegevens succesvol opgeslagen!')

                # Synchroniseer met GitHub
                sync_to_github()

                # Wacht 3 seconden voordat de pagina verandert
                time.sleep(5)

                # Reset en terug naar Home
                st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error('⚠️ Vul alle velden in!')

elif page == "Gewicht":
    st.title("Gewicht")
    
    # Voer gewicht in
    vandaag = datetime.today().strftime('%Y-%m-%d')
    Datum1 = st.text_input('Datum', value=vandaag)
    Gewichtmeting = st.text_input("Voer je Gewichtmeting in", value="")

    if st.button("✅ Opslaan Gewicht"):
        if Datum1 and Gewichtmeting:
            data = [{'Datum': Datum1, 'Gewichtmeting': Gewichtmeting}]
            save_to_excel(data, 'Gewicht')
            st.success("✅ Gewicht en Gewichtmeting succesvol opgeslagen!")

            # Synchroniseer met GitHub
            sync_to_github()

            time.sleep(3)  # Wacht 3 seconden voor navigatie terug naar Home
            st.session_state.page = "Home"
            st.rerun()
        else:
            st.error("⚠️ Vul zowel het gewicht als de meting in!")
else:
    # Data inlezen van het Excel-bestand, specifiek het blad 'Gewicht'
    df = pd.read_excel('Data sporten.xlsx', sheet_name='Gewicht')

    # Verwijder eventuele spaties rondom de kolomnamen
    df.columns = df.columns.str.strip()

    # Zorg ervoor dat de datumkolom als een datum wordt gelezen
    df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')  # errors='coerce' voor ongeldige datums

    # Verwijder de tijd van de datumkolom (alleen de datum behouden)
    df['Datum'] = df['Datum'].dt.date

    # Maak een lijndiagram met Plotly
    fig1 = px.line(df, x='Datum', y='Gewichtmeting', 
              title='Gewicht meting over de tijd',
              labels={'Datum': 'Datum', 'Gewichtmeting': 'Gewichtmeting (kg)'})

    # Het interactieve diagram weergeven in de Streamlit app
    st.plotly_chart(fig1)






