import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Mijn App", layout="wide")

tab1, tab2, tab3, tab4= st.tabs(["🏠 Home", "🏋️‍♂️ Sport", "⚖️ Gewicht", "⚙️ Instellingen"])

# ---------------------------------------------------------------------------------------------------------------------

# Verbind met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Verkrijg de bestaande data (optioneel, je kunt deze stap ook overslaan als je alleen data wilt toevoegen)
existing_data = conn.read(worksheet="Gewicht", usecols=list(range(2)), ttl=5)
existing_data = existing_data.dropna(how="all")

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

with tab3:
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

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

with tab2:
    st.title("Sport")

    # Lees de lijst met oefeningen uit het tabblad 'Oefeningsoort'
    oefeningsoorten_df = conn.read(worksheet="Oefeningsoort", ttl=5)
    oefeningsoorten_df = oefeningsoorten_df.dropna(how="all")  # Optioneel: verwijder lege rijen

    # Haal de oefeningen uit de kolom 'Oefeningsoort' als lijst
    oefeningen = oefeningsoorten_df["Oefeningsoort"].dropna().tolist()

    hoevaak_opties = [str(i) for i in range(10, 0, -1)]
    
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


    # Filter de data op de datum van vandaag
    vandaag_df = sport_data[sport_data["Datum"] == vandaag]

    # Toon de gefilterde gegevens
    st.markdown("### Eerder ingevoerde sportgegevens van vandaag")
    st.dataframe(vandaag_df)


# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

with tab4:
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

    st.markdown("---")
    st.subheader("📉 Laatste 5 gewichtsmetingen verwijderen")

    # Laatste 5 rijen tonen
    if not existing_data.empty:
        # Laatste 5 rijen ophalen
        laatste_rijen = existing_data.tail(5).copy()
        laatste_rijen['Weergave'] = laatste_rijen['Datum'].astype(str) + " - " + laatste_rijen['Gewicht'].astype(str) + " kg"

        # Selectie van te verwijderen rij
        geselecteerd = st.selectbox("Kies een meting om te verwijderen:", options=laatste_rijen['Weergave'].tolist())

        if st.button("🗑️ Verwijder geselecteerde meting"):
            # De rij verwijderen
            index_te_verwijderen = laatste_rijen[laatste_rijen['Weergave'] == geselecteerd].index[0]
            existing_data = existing_data.drop(index_te_verwijderen).reset_index(drop=True)

            # Sheet bijwerken
            conn.update(worksheet="Gewicht", data=existing_data)
            st.success(f"✅ Meting '{geselecteerd}' verwijderd.")
            st.rerun()
    else:
        st.info("Er zijn nog geen gewichtsmetingen opgeslagen.")


    st.markdown("---")
    st.subheader("🏋️ Laatste 5 sportoefeningen verwijderen")

    # Laad bestaande sportdata
    sport_data = conn.read(worksheet="Oefeningen", ttl=5)
    sport_data = sport_data.dropna(how="all")

    if not sport_data.empty:
        # Laatste 5 rijen ophalen
        laatste_oefeningen = sport_data.tail(5).copy()

        # Maak een weergavekolom voor selectie
        laatste_oefeningen['Weergave'] = (
            laatste_oefeningen['Datum'].astype(str) + " | " +
            laatste_oefeningen['Oefening'].astype(str) + " | " +
            laatste_oefeningen['Herhalingen'].astype(str) + "x | " +
            laatste_oefeningen['Gewicht'].astype(str) + "kg"
        )

        geselecteerde_oef = st.selectbox("Kies een oefening om te verwijderen:", options=laatste_oefeningen['Weergave'].tolist())

        if st.button("🗑️ Verwijder geselecteerde oefening"):
            index_te_verwijderen = laatste_oefeningen[laatste_oefeningen['Weergave'] == geselecteerde_oef].index[0]
            sport_data = sport_data.drop(index_te_verwijderen).reset_index(drop=True)

            # Sheet bijwerken
            conn.update(worksheet="Oefeningen", data=sport_data)
            st.success(f"✅ Oefening '{geselecteerde_oef}' verwijderd.")
            st.rerun()
    else:
        st.info("Er zijn nog geen oefeningen opgeslagen.")

# ---------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------

with tab1:

    st.markdown("---")
    sport_data = conn.read(worksheet="Oefeningen", ttl=5)
    sport_data = sport_data.dropna(how="all")

    # Zorg dat 'Gewicht' en 'Herhalingen' numeriek zijn
    sport_data['Gewicht'] = pd.to_numeric(sport_data['Gewicht'], errors='coerce')
    sport_data['Herhalingen'] = pd.to_numeric(sport_data['Herhalingen'], errors='coerce')

    # Sorteer eerst op Gewicht (aflopend), dan Herhalingen (aflopend)
    gesorteerd = sport_data.sort_values(by=['Oefening', 'Gewicht', 'Herhalingen'], ascending=[True, False, False])

    # Neem de eerste rij per oefening (dus hoogste gewicht, en bij gelijk gewicht hoogste herhalingen)
    top_rijen = gesorteerd.groupby('Oefening', as_index=False).first()

    # Alleen de gewenste kolommen tonen
    kolommen = ['Oefening', 'Gewicht', 'Herhalingen', 'Datum']
    top_rijen = top_rijen[kolommen].sort_values(by='Gewicht', ascending=False)

    # Tabel tonen in Streamlit
    st.title("Zwaarste sets per oefening")
    st.dataframe(top_rijen.reset_index(drop=True))


# ---------------------------------------------------------------------------------------------------------------------
    st.markdown("---")
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

    st.markdown("---")
    # Zorg dat Datum datetime is
    sport_data['Datum'] = pd.to_datetime(sport_data['Datum'], format='%d-%m-%Y', errors='coerce')

    # Unieke datums pakken (dus dubbele dagen eruit)
    unieke_dagen = sport_data[['Datum']].drop_duplicates().copy()

    # Weeknummer en Jaar toevoegen
    unieke_dagen['Weeknummer'] = unieke_dagen['Datum'].dt.isocalendar().week
    unieke_dagen['Jaar'] = unieke_dagen['Datum'].dt.isocalendar().year

    # Groeperen op Jaar + Weeknummer en aantal unieke dagen tellen
    trainings_frequentie = unieke_dagen.groupby(['Jaar', 'Weeknummer']).size().reset_index(name='AantalDagen')

    # Voor de x-as maken we een string zoals "2024-W13" voor overzicht
    trainings_frequentie['Week'] = 'Week ' + trainings_frequentie['Weeknummer'].astype(str)

    # Plotten
    fig_hist = px.bar(
        trainings_frequentie,
        x='Week',
        y='AantalDagen',
        labels={'AantalDagen': 'Unieke trainingsdagen', 'Week': 'Week'},
        title='Aantal unieke trainingsdagen per week',
    )

    fig_hist.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(dtick=1),
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.title("Aantal keer gesport per week")
    st.plotly_chart(fig_hist, use_container_width=True)

# ---------------------------------------------------------------------------------------------------------------------
    st.markdown("---")
    st.title("Gewicht vs Herhalingen")

    # Dropdown voor oefeningselectie
    oefeningen = sport_data['Oefening'].unique().tolist()
    oefeningen.sort()
    oefeningen_opties = ['Alle Oefeningen'] + oefeningen

    gekozen_oefening = st.selectbox(
        'Kies een oefening om te tonen:',
        options=oefeningen_opties
    )

    # Filter de data
    if gekozen_oefening != 'Alle Oefeningen':
        gefilterde_data = sport_data[sport_data['Oefening'] == gekozen_oefening]
    else:
        gefilterde_data = sport_data

    # Zorg dat Datum een datetime-object is
    gefilterde_data['Datum'] = pd.to_datetime(gefilterde_data['Datum'])

    # Plot maken
    fig1 = px.scatter(
        gefilterde_data,
        x='Datum',
        y='Gewicht',
        size='Herhalingen',
        color='Herhalingen',
        labels={
            'Datum': 'Datum',
            'Gewicht': 'Gewicht (kg)',
            'Herhalingen': 'Aantal Herhalingen'
        },
        title=f"Progressie {'voor ' + gekozen_oefening if gekozen_oefening != 'Alle Oefeningen' else 'voor alle oefeningen'}",
        color_continuous_scale=['green', 'yellow', 'red'],
        size_max=30,
        template='plotly_white',
        hover_data=['Oefening', 'Herhalingen']
    )

    # Toon de grafiek
    st.plotly_chart(fig1)
    st.markdown("---")