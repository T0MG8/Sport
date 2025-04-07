import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import plotly.express as px

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
page = st.sidebar.radio(
    "Kies een optie",
    ["Home", "Gewicht", "Sport", "Instellingen"],
    index=["Home", "Gewicht", "Sport", "Instellingen"].index(st.session_state.page)
)


if page == "Gewicht":
    st.title("Gewicht")
    with st.form(key="vendor_form"):
        vandaag = datetime.date.today().strftime('%d-%m-%Y')
        Datum = st.text_input("Datum", value=vandaag)
        Gewicht = st.text_input(label="Gewicht")

        knop = st.form_submit_button(label="Opslaan")

    if knop:
        if not Datum or not Gewicht:
            st.warning("Vul alle velden in!")
            st.stop()
        
        # Controleer of Datum een string is en zet het om naar een datetime object
        if isinstance(Datum, str):
            Datum = pd.to_datetime(Datum, errors='coerce', dayfirst=True)  # Zet de string om naar datetime, gebruik errors='coerce' om ongeldig formaat af te handelen
        
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

    st.dataframe(existing_data.tail(5))


if page == "Sport":
    st.title("Sport")

    # Lees de lijst met oefeningen uit het tabblad 'Oefeningsoort'
    oefeningsoorten_df = conn.read(worksheet="Oefeningsoort", ttl=5)
    oefeningsoorten_df = oefeningsoorten_df.dropna(how="all")  # Optioneel: verwijder lege rijen

    # Haal de oefeningen uit de kolom 'Oefeningsoort' als lijst
    oefeningen = oefeningsoorten_df["Oefeningsoort"].dropna().tolist()

    hoevaak_opties = [str(i) for i in range(12, 0, -1)]
    
    def frange(start, stop, step):
        while start <= stop:
            yield round(start, 2)
            start += step

    # Reeksen genereren
    optie_1 = list(frange(1.25, 50, 1.25))
    optie_2 = list(frange(2, 40, 2))
    optie_3 = list(frange(55, 150, 5))
    optie_4 = list(frange(1, 25, 1))

    # Alles combineren en unieke waardes behouden
    alle_opties = sorted(set(optie_1 + optie_2 + optie_3 + optie_4))

    # Converteer naar strings
    gewicht_opties = [str(i) for i in alle_opties]



    # Standaard datum
    vandaag = datetime.date.today().strftime('%d-%m-%Y')
    Datum = st.text_input("Datum", value=vandaag)

    # Laad bestaande data
    sport_data = conn.read(worksheet="Oefeningen", ttl=5)
    sport_data = sport_data.dropna(how="all")

    if 'oefeningen' not in st.session_state:
        st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]

    # Dynamische invoervelden
    for i, oefening in enumerate(st.session_state.oefeningen):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            oefening['oef'] = st.selectbox(f'Oefening {i+1}', oefeningen, key=f'oef_{i}')
        with col2:
            oefening['rep'] = st.selectbox(f'Herhalingen {i+1}', hoevaak_opties, key=f'rep_{i}')
        with col3:
            oefening['gewicht'] = st.selectbox(f'Gewicht {i+1} (kg of stand)', gewicht_opties, key=f'gewicht_{i}')

    col1, col2 = st.columns([1, 3])
    with col2:
        if st.button("➕ Extra oefening"):
            st.session_state.oefeningen.append({'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]})
            st.rerun()

    with col1:
        if st.button("✅ Opslaan"):
            if Datum and all(oef['oef'] and oef['rep'] and oef['gewicht'] for oef in st.session_state.oefeningen):
                nieuwe_data = pd.DataFrame([
                    {
                        "Datum": Datum,
                        "Oefening": oef['oef'],
                        "Herhalingen": oef['rep'],
                        "Gewicht": oef['gewicht']
                    } for oef in st.session_state.oefeningen
                ])

                bijgewerkt = pd.concat([sport_data, nieuwe_data], ignore_index=True)
                conn.update(worksheet="Oefeningen", data=bijgewerkt)

                st.success("✅ Gegevens succesvol opgeslagen!")
                st.session_state.oefeningen = [{'oef': oefeningen[0], 'rep': hoevaak_opties[0], 'gewicht': gewicht_opties[0]}]
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.warning("⚠️ Vul alle velden in!")


    st.markdown("### Eerder ingevoerde sportgegevens")
    st.dataframe(sport_data.tail(5))


elif page == "Instellingen":
    st.title("Nieuwe oefening toevoegen")

    oefeningsoorten_df = conn.read(worksheet="Oefeningsoort", ttl=5)
    oefeningen = oefeningsoorten_df["Oefeningsoort"].dropna().tolist()

    nieuwe_oef = st.text_input("Naam van de nieuwe oefening")

    if st.button("📥 Opslaan"):
        if not nieuwe_oef.strip():
            st.warning("⚠️ Oefening mag niet leeg zijn.")
        elif nieuwe_oef.strip() in oefeningen:
            st.warning("⚠️ Deze oefening bestaat al.")
        else:
            oefeningsoorten_df.loc[len(oefeningsoorten_df)] = nieuwe_oef.strip()
            conn.update(worksheet="Oefeningsoort", data=oefeningsoorten_df)
            st.success(f"✅ '{nieuwe_oef.strip()}' toegevoegd.")

            # Ga terug naar sportpagina
            st.session_state.page = "Home"
            st.rerun()


elif page == "Home":
    sport_data = conn.read(worksheet="Oefeningen", ttl=5)
    sport_data = sport_data.dropna(how="all")

    # Zorg dat 'Gewicht' numeriek is (optioneel, als dat soms strings zijn)
    sport_data['Gewicht'] = pd.to_numeric(sport_data['Gewicht'], errors='coerce')

    # Per oefening: vind de rij met het hoogste gewicht
    idx = sport_data.groupby('Oefening')['Gewicht'].idxmax()
    top_rijen = sport_data.loc[idx]

    # Alleen de gewenste kolommen tonen
    kolommen = ['Oefening', 'Gewicht', 'Herhalingen', 'Datum']
    top_rijen = top_rijen[kolommen].sort_values(by='Gewicht', ascending=False)

    # Tabel tonen in Streamlit
    st.title("Zwaarste sets per oefening")
    st.dataframe(top_rijen.reset_index(drop=True))

# ---------------------------------------------------------------------------------------------------------------------
    st.title("Gewicht over de tijd")

    # Zet de 'Datum' kolom om naar een datetime object
    existing_data['Datum'] = pd.to_datetime(existing_data['Datum'], format='%d-%m-%Y')

    # Zorg ervoor dat we alleen de datum zonder tijd weergeven
    existing_data['Datum'] = existing_data['Datum'].dt.date

    # Maak de lijngrafiek
    fig = px.line(existing_data, x='Datum', y='Gewicht')

    # Zet markers aan voor de lijn
    fig.update_traces(mode='lines+markers')  # Voeg markers toe aan de lijn

    # Zet de grid aan voor zowel x- en y-as
    fig.update_layout(
        xaxis=dict(showgrid=True),  # Zet grid aan voor x-as
        yaxis=dict(showgrid=True)   # Zet grid aan voor y-as
    )

    # Toon de grafiek
    st.plotly_chart(fig)

# ---------------------------------------------------------------------------------------------------------------------

    st.title("Gewicht vs Herhalingen")

    oefeningen = sport_data['Oefening'].unique().tolist()
    oefeningen.sort()
    oefeningen_opties = ['Alle Oefeningen'] + oefeningen

    # Dropdown boven de plot
    gekozen_oefening = st.selectbox(
        'Kies een oefening om te tonen:',
        options=oefeningen_opties
    )

    # Data filteren op keuze
    if gekozen_oefening != 'Alle Oefeningen':
        gefilterde_data = sport_data[sport_data['Oefening'] == gekozen_oefening]
    else:
        gefilterde_data = sport_data

    # Plot maken
    fig1 = px.scatter(
        gefilterde_data,
        x='Gewicht',
        y='Herhalingen',
        color='Oefening',
        labels={'Gewicht': 'Gewicht (kg)', 'Herhalingen': 'Aantal Herhalingen'},
        template='plotly_white'
    )

    # Plot tonen
    st.plotly_chart(fig1)






