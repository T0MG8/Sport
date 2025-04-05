import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import plotly.express as px

st.title("Voeg data toe aan Google Sheet")

# Verbind met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Verkrijg de bestaande data (optioneel, je kunt deze stap ook overslaan als je alleen data wilt toevoegen)
existing_data = conn.read(worksheet="Gewicht", usecols=list(range(2)), ttl=5)
existing_data = existing_data.dropna(how="all")

# Sidebar navigatie
st.sidebar.title("Navigatie")
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Voeg een nieuwe optie "Gewicht" toe
page = st.sidebar.radio("Kies een optie", ["Home","Gewicht"], index=["Home", "Gewicht"].index(st.session_state.page))

if page == "Gewicht":
    st.title("Gewicht")
    with st.form(key="vendor_form"):
        Datum = st.text_input(label="Datum")
        Gewicht = st.text_input(label="Gewicht")

        knop = st.form_submit_button(label="Opslaan")

    if knop:
        if not Datum or not Gewicht:
            st.warning("Vul alle velden in!")
            st.stop()
        
        # Controleer of Datum een string is en zet het om naar een datetime object
        if isinstance(Datum, str):
            Datum = pd.to_datetime(Datum, errors='coerce')  # Zet de string om naar datetime, gebruik errors='coerce' om ongeldig formaat af te handelen
        
        # Controleer of Datum een geldige datetime is
        if not isinstance(Datum, pd.Timestamp):
            st.warning("Ongeldige datum.")
            st.stop()
        
        # Controleer of de datum al bestaat
        if existing_data['Datum'].astype(str).str.contains(str(Datum)).any():
            st.warning("Deze datum is al toegevoegd.")
            st.stop()
        else:
            vendor_data = pd.DataFrame(
                [
                    {
                        "Datum": Datum.strftime("%d-%m-%Y"),
                        "Gewicht": Gewicht
                    }
                ]
            )
                
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            conn.update(worksheet="Gewicht", data=updated_df)

            st.success("Data is succesvol toegevoegd")
            st.rerun()

    st.dataframe(existing_data)

else:
    st.write("Kolom")

    # Zet de 'Datum' kolom om naar een datetime object
    existing_data['Datum'] = pd.to_datetime(existing_data['Datum'], format='%d-%m-%Y')

    # Zorg ervoor dat we alleen de datum zonder tijd weergeven
    existing_data['Datum'] = existing_data['Datum'].dt.date

    # Maak de lijngrafiek
    fig = px.line(existing_data, x='Datum', y='Gewicht', title='Gewicht over de tijd')

    # Zet markers aan voor de lijn
    fig.update_traces(mode='lines+markers')  # Voeg markers toe aan de lijn

    # Zet de grid aan voor zowel x- en y-as
    fig.update_layout(
        xaxis=dict(showgrid=True),  # Zet grid aan voor x-as
        yaxis=dict(showgrid=True)   # Zet grid aan voor y-as
    )

    # Toon de grafiek
    st.plotly_chart(fig)











# # Functie om gegevens op te slaan in Google Sheets
# def save_to_gsheet(data, sheet_name):
#     # Converteer de data naar een lijst van lijsten (aangezien GSheetsConnection append verwacht)
#     values = [list(row.values()) for row in data]
    
#     # Voeg de data toe aan het Google Sheet
#     conn.append(worksheet=sheet_name, values=values)
#     st.success("Data succesvol opgeslagen!")

# # Maak inputvelden voor datum en gewicht
# datum = st.date_input("Selecteer de datum", min_value=datetime.date(2020, 1, 1), max_value=datetime.date.today())
# gewicht = st.number_input("Voer je gewicht in", min_value=30.0, max_value=200.0, step=0.1)

# # Maak een knop om de data op te slaan
# if st.button("Opslaan"):
#     # Maak een lijst van de nieuwe rij
#     new_row = [{"Datum": str(datum), "Gewicht": gewicht}]
    
#     # Sla de data op in Google Sheets
#     save_to_gsheet(new_row, sheet_name="Gewicht")

# # Toon de bestaande gegevens
# st.dataframe(existing_data)


#     if os.path.exists(bestandsnaam):
#         try:
#             os.chdir(repo_path)
#             subprocess.run(['git', 'add', bestandsnaam], check=True)
#             commit_message = f"Update {bestandsnaam} op {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#             subprocess.run(['git', 'commit', '-m', commit_message], check=True)
#             subprocess.run(['git', 'push', 'origin', 'main'], check=True)
#             print("✅ Gegevens succesvol gesynchroniseerd naar GitHub!")
#         except subprocess.CalledProcessError as e:
#             print(f"Fout bij Git-commando: {e}")
#     else:
#         print("⚠️ Het bestand bestaat niet.")

# # Sidebar navigatie
# st.sidebar.title("Navigatie")
# if 'page' not in st.session_state:
#     st.session_state.page = "Home"

# # Voeg een nieuwe optie "Gewicht" toe
# page = st.sidebar.radio("Kies een optie", ["Home", "Formulier", "Gewicht"], index=["Home", "Formulier", "Gewicht"].index(st.session_state.page))

# # Oefening- en herhalingsopties
# oefeningen = ['Dumbell Press', 'Zittend Roeien Cables', 'Incline Bench Press', 'Tricep Extencion', 'Lat Pull Down', 'Shoulder Press', 'Overhead Extencion', 'Dips voor Borst', 'Cable Crossover Flyes (Bank)', '']
# hoevaak_opties = ['10x', '9x', '8x', '7x', '6x', '5x', '4x', '3x', '2x', '1x']
# gewicht_opties = ['5kg', '10kg', '12kg', '14kg', '16kg', '18kg','20kg', '22kg', '24kg', '26kg', '28kg', '30kg', '32kg', '34kg', '36kg', '38kg', '40kg', '45kg', '50g', '55kg', '60kg', '70kg', '80kg', '90kg', '100kg', '110kg',' 120kg', '130kg','stand 1', 'stand 2', 'stand 3', 'stand 4', 'stand 5', 'stand 6', 'stand 7', 'stand 8', 'stand 9','stand 10', 'stand 11', 'stand 12','stand 13', 'stand 14', 'stand 15', 'stand 16', 'stand 17', 'stand 18', 'stand 19','stand 20','stand 21','stand 22','stand 23', 'stand 24', 'stand 25']

# if page == "Formulier":
#     st.title('Formulier om Excel-bestand bij te werken')

#     # Standaard datum
#     vandaag = datetime.today().strftime('%Y-%m-%d')
#     Datum = st.text_input('Datum', value=vandaag)

#     # Initialiseer lijst voor oefeningen, herhalingen en gewichten
#     if 'oefeningen' not in st.session_state:
#         st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]

#     # Toon de dynamische invoervelden
#     for i, oefening in enumerate(st.session_state.oefeningen):
#         col1, col2, col3 = st.columns([2, 1, 1])  # Voeg een extra kolom voor gewicht toe
#         with col1:
#             oefening['oef'] = st.selectbox(f'Oefening {i+1}', oefeningen, index=oefeningen.index(oefening['oef']), key=f'oef_{i}')
#         with col2:
#             oefening['rep'] = st.selectbox(f'Hoevaak {i+1}', hoevaak_opties, index=hoevaak_opties.index(oefening['rep']), key=f'rep_{i}')
#         with col3:  # Het nieuwe dropdownmenu voor gewicht
#             oefening['gewicht'] = st.selectbox(f'Gewicht {i+1}', gewicht_opties, index=gewicht_opties.index(oefening['gewicht']), key=f'gewicht_{i}')

#     # Knoppen: Extra oefening & Opslaan
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         if st.button('➕ Extra oefening'):
#             st.session_state.oefeningen.append({'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]})
#             st.rerun()

#     with col2:
#         if st.button('✅ Opslaan'):
#             if Datum and all(oef['oef'] and oef['rep'] and oef['gewicht'] for oef in st.session_state.oefeningen):
#                 data = [{'Datum': Datum, 'Oefening': oef['oef'], 'Hoevaak': oef['rep'], 'Gewicht': oef['gewicht']} for oef in st.session_state.oefeningen]
#                 save_to_excel(data, 'Oefeningen')
#                 st.success('✅ Gegevens succesvol opgeslagen!')

#                 # Synchroniseer met GitHub
#                 sync_to_github()

#                 # Wacht 3 seconden voordat de pagina verandert
#                 time.sleep(5)

#                 # Reset en terug naar Home
#                 st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]
#                 st.session_state.page = "Home"
#                 st.rerun()
#             else:
#                 st.error('⚠️ Vul alle velden in!')

# elif page == "Gewicht":
#     st.title("Gewicht")
    
#     # Voer gewicht in
#     vandaag = datetime.today().strftime('%Y-%m-%d')
#     Datum1 = st.text_input('Datum', value=vandaag)
#     Gewichtmeting = st.text_input("Voer je Gewichtmeting in", value="")

#     if st.button("✅ Opslaan Gewicht"):
#         if Datum1 and Gewichtmeting:
#             data = [{'Datum': Datum1, 'Gewichtmeting': Gewichtmeting}]
#             save_to_excel(data, 'Gewicht')
#             st.success("✅ Gewicht en Gewichtmeting succesvol opgeslagen!")

#             # Synchroniseer met GitHub
#             sync_to_github()

#             time.sleep(3)  # Wacht 3 seconden voor navigatie terug naar Home
#             st.session_state.page = "Home"
#             st.rerun()
#         else:
#             st.error("⚠️ Vul zowel het gewicht als de meting in!")
# else:
#     # Data inlezen van het Excel-bestand, specifiek het blad 'Gewicht'
#     df = pd.read_excel('Data sporten.xlsx', sheet_name='Gewicht')

#     # Verwijder eventuele spaties rondom de kolomnamen
#     df.columns = df.columns.str.strip()

#     # Zorg ervoor dat de datumkolom als een datum wordt gelezen
#     df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')  # errors='coerce' voor ongeldige datums

#     # Verwijder de tijd van de datumkolom (alleen de datum behouden)
#     df['Datum'] = df['Datum'].dt.date

#     # Maak een lijndiagram met Plotly
#     fig1 = px.line(df, x='Datum', y='Gewichtmeting', 
#               title='Gewicht meting over de tijd',
#               labels={'Datum': 'Datum', 'Gewichtmeting': 'Gewichtmeting (kg)'})

#     # Het interactieve diagram weergeven in de Streamlit app
#     st.plotly_chart(fig1)






