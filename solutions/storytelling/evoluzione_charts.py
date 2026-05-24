import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

DATA_PATH  = '../../datasets_cleaned/'
MAIN_TYPES = ['TV', 'Movie', 'OVA', 'ONA']
TYPE_COLORS = {'TV': '#2196F3', 'Movie': '#FF5722', 'OVA': '#4CAF50', 'ONA': '#FF9800'}

def explode_genres(details):
    """Esplode la colonna 'genres' in righe singole per genere. Ritorna details_ex e generi."""
    details_ex = (
        details.assign(genre=details['genres'].str[2:-2].str.split("', '")) # ogni lista di generi diventa righe separate
        .explode('genre')
    )

    details_ex = details_ex[details_ex['genre'].str.strip() != ''][['mal_id', 'genre']] # rimuove eventuali generi vuoti e tiene solo le colonne necessarie
    generi = details_ex['genre'].value_counts().index     # indice dei generi ordinato per frequenza decrescente
    return details_ex, generi


def filter_main_types(details):
    """Filtra details ai 4 formati principali (TV, Movie, OVA, ONA), popola la colonna 'year' usando start_date dove mancante."""

    details = details[details['type'].isin(MAIN_TYPES)].copy().reset_index(drop=True)  # tiene solo le righe dei 4 formati principali e resetta l'indice

    details['year'] = details['year'].fillna(
        pd.to_datetime(details['start_date'], utc=True, errors='coerce').dt.year
    )                # dove 'year' è null, prova a ricavarlo da start_date
    print(f'details filtrato: {len(details):,} titoli  →  {MAIN_TYPES}')
    return details


def _max_year(details):
    """Ritorna l'anno massimo disponibile nel dataset, escludendo l'anno corrente."""
    return int(min(details['year'].dropna().max(), datetime.datetime.now().year - 1))   # min() garantisce che non si usi l'anno in corso, i cui dati potrebbero essere parziali

# Funzione utilizzata per creare il grafico della composizione del catalogo per formato
def plot_type_distribution(details):
    """Bar chart orizzontale (matplotlib) del numero di titoli per formato (TV, Movie, OVA, ecc.)."""
    type_counts = details['type'].value_counts().reset_index()     # conta i titoli per formato e aggiunge la percentuale sul totale
    type_counts.columns = ['type', 'count']
    type_counts['pct'] = type_counts['count'] / type_counts['count'].sum() * 100

    # dizionario di etichette leggibili per i codici formato
    type_labels = {
        'TV':         'Serie TV',
        'Movie':      'Film',
        'OVA':        'OVA (home video)',
        'ONA':        'ONA (piattaforme digitali)',
        'Music':      'Video musicali',
        'Special':    'Special',
        'TV Special': 'TV Special',
        'CM':         'Spot pubblicitari',
        'PV':         'Promotional Video',
    }
    type_counts['label'] = type_counts['type'].map(type_labels).fillna(type_counts['type'])

    palette = [
        '#2196F3', '#FF5722', '#4CAF50', '#FF9800',
        '#9C27B0', '#009688', '#795548', '#607D8B', '#E91E63',
    ]

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.barh(
        type_counts['label'][::-1], type_counts['count'][::-1],
        color=palette[:len(type_counts)][::-1], edgecolor='white',
    ) # [::-1] inverte l'ordine così la barra più lunga appare in cima

    for bar, (_, row) in zip(bars, type_counts[::-1].iterrows()):
        ax.text(
            bar.get_width() + 60, bar.get_y() + bar.get_height() / 2,
            f"{row['count']:,}  ({row['pct']:.1f}%)",
            va='center', fontsize=9,
        )  # aggiunge l'etichetta con count e % a destra di ogni barra

    ax.set_xlabel('Numero di titoli', fontsize=12)
    ax.set_title('Composizione del catalogo MAL per formato\n', fontsize=13, fontweight='bold')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlim(0, type_counts['count'].max() * 1.28)
    plt.tight_layout()
    plt.show()

#Funzione utilizzata per creare il grafico dell'evoluzione dei format nel tempo
def plot_format_evolution(details):
    """Line chart Plotly dell'andamento annuale dei 4 formati principali dal 1990 ad oggi."""
    details_plot = details.copy()
    # recupera l'anno da start_date per le righe che non ce l'hanno già
    details_plot['year'] = details_plot['year'].fillna(
        pd.to_datetime(details_plot['start_date'], utc=True, errors='coerce').dt.year
    )
    max_yr = _max_year(details_plot)

    # conta i titoli per (anno, formato) nell'intervallo 1990–max_yr
    type_year = (
        details_plot
        .dropna(subset=['year'])
        .query('type in @MAIN_TYPES and year >= 1990 and year <= @max_yr')
        .groupby(['year', 'type'])
        .size()
        .reset_index(name='count')
    )

    fig = go.Figure()
    # aggiunge una linea per ciascuno dei 4 formati principali
    for t in MAIN_TYPES:
        d = type_year[type_year['type'] == t].sort_values('year')
        fig.add_trace(go.Scatter(
            x=d['year'], y=d['count'],
            mode='lines+markers', name=t,
            line=dict(color=TYPE_COLORS[t], width=2.2),
            marker=dict(size=5),
            # hovertemplate personalizzato: mostra nome formato, anno e conteggio
            hovertemplate='<b>%{fullData.name}</b><br>Anno: %{x:.0f}<br>Titoli: %{y}<extra></extra>',
        ))

    fig.update_layout(
        title=dict(
            text=(
                f"Evoluzione della produzione per formato (1990–{max_yr})<br>"
            ),
            font=dict(size=15),
        ),
        xaxis=dict(title='Anno', tickformat='d'),   # tickformat='d' forza interi (no decimali)
        yaxis=dict(title='Numero di titoli prodotti'),
        legend=dict(font=dict(size=11)),
        hovermode='x unified',   # mostra tutti i formati insieme al passaggio del mouse
        template='plotly_white',
        width=980, height=480,
    )
    fig.show()

# Funzione utilizzata per creare il grafico della distrubuzione di ogni genere
def plot_genre_pie(details_ex):
    """Donut chart Plotly con la distribuzione percentuale dei top 15 generi nel catalogo."""
    # conta i titoli per genere e prende i 15 più frequenti
    genre_totals = (
        details_ex['genre']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'genre', 'count': 'count'})
    )

    fig = go.Figure(go.Pie(
        labels=genre_totals['genre'],
        values=genre_totals['count'],
        hole=0.35,          # foro centrale che trasforma il pie in donut
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Titoli: %{value:,}<br>%{percent}<extra></extra>',
        textfont=dict(size=11),
    ))
    fig.update_layout(
        title=dict(
            text='Distribuzione dei titoli per genere<br>',
            font=dict(size=15),
        ),
        legend=dict(font=dict(size=11), orientation='v'),
        width=1000, height=750,
    )
    fig.show()

# Funzione per creare grafico animato del cambiamento di ogni genere per anno
def plot_genre_animation(details, details_ex, generi):
    """Bar chart orizzontale animato con la quota % degli 8 generi top anno per anno.
    Include slider e pulsanti Play/Pausa; stampa anche il genere dominante prima e dopo il sorpasso."""
    max_yr = _max_year(details)

    # unisce i generi esplosi con l'anno del titolo, filtra periodo e generi rilevanti
    genre_year = (
        details_ex
        .merge(details[['mal_id', 'year']], on='mal_id')
        .dropna(subset=['year'])
        .query('year >= 1990 and year <= @max_yr')
        .query('genre in @generi')
        .groupby(['year', 'genre'])
        .size()
        .reset_index(name='count')
    )

    top8 = details_ex['genre'].value_counts().head(8).index
    # pivot: righe = anno, colonne = genere, valori = conteggio assoluto
    pivot_abs = (
        genre_year
        .query('genre in @top8')
        .pivot(index='year', columns='genre', values='count')
        .fillna(0)[top8]
    )
    # normalizza per anno: divide ogni cella per il totale della riga → quota percentuale
    pivot_pct = pivot_abs.div(pivot_abs.sum(axis=1), axis=0) * 100

    # associa un colore a ciascuno degli 8 generi usando la palette Set2 di Plotly
    palette = dict(zip(top8, px.colors.qualitative.Set2[:len(top8)]))
    years   = sorted(pivot_pct.index.astype(int))
    x_max   = pivot_pct.values.max() * 1.18   # asse x leggermente più largo delle barre

    def make_bar(year):
        """Crea un oggetto go.Bar orizzontale con i dati di un singolo anno, ordinato per quota."""
        row = pivot_pct.loc[year].sort_values(ascending=True)   # ascending=True → barra più lunga in cima
        return go.Bar(
            x=row.values.round(2), y=list(row.index),
            orientation='h',
            marker_color=[palette[g] for g in row.index],
            text=[f'{v:.1f}%' for v in row.values],
            textposition='outside', cliponaxis=False,
            hovertemplate='<b>%{y}</b><br>Quota: %{x:.1f}%<extra></extra>',
        )

    # un Frame per ogni anno: Plotly anima passando da un frame all'altro
    frames = [go.Frame(data=[make_bar(y)], name=str(y)) for y in years]
    fig    = go.Figure(data=[make_bar(years[0])], frames=frames)

    fig.update_layout(
        title=dict(
            text='Quota percentuale per genere nella produzione anime',
            font=dict(size=15),
        ),
        xaxis=dict(title='Percentuale del totale annuo', range=[0, x_max], ticksuffix='%', fixedrange=True),
        yaxis=dict(title='', fixedrange=True),
        template='plotly_white',
        width=900, height=480,
        showlegend=False,
        updatemenus=[dict(
            type='buttons', showactive=False, y=0.5, x=1.05, xanchor='left', yanchor='middle',
            buttons=[
                dict(label='▶  Play', method='animate',
                     args=[None, dict(frame=dict(duration=300, redraw=True),
                                      fromcurrent=True,
                                      transition=dict(duration=200, easing='cubic-in-out'))]),
                dict(label='⏸  Pausa', method='animate',
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode='immediate',
                                        transition=dict(duration=0))]),
            ],
        )],
        # slider sotto il grafico: un passo per ogni anno
        sliders=[dict(
            active=0,
            currentvalue=dict(prefix='Anno: ', font=dict(size=13)),
            pad=dict(t=10),
            steps=[
                dict(method='animate', label=str(y),
                     args=[[str(y)], dict(frame=dict(duration=300, redraw=True),
                                          mode='immediate',
                                          transition=dict(duration=200))])
                for y in years
            ],
        )],
    )
    fig.show()

# Funzione per creare grafico generi in base al genere dell'utente
def plot_gender_genres(ratings, profiles, details_ex, generi):
    """Grouped bar chart Plotly della distribuzione dei generi anime per genere utente (Male, Female, Non-Binary), calcolata sugli anime con status 'completed'."""
    # filtra i profili con genere esplicito (esclude 'Non-Disclosed' e valori null)
    profiles_gen = profiles.loc[profiles['gender'].isin(['Male', 'Female', 'Non-Binary'])]
    # join tra i rating completati e i profili con genere noto
    r_gen = (
        ratings
        .query("status == 'completed'")
        .merge(profiles_gen[['username', 'gender']], on='username')
    )

    # conta le occorrenze per (genere utente, genere anime) e calcola la % sul totale del gruppo
    counts_gen = (
        r_gen
        .merge(details_ex, left_on='anime_id', right_on='mal_id')
        .query('genre in @generi')
        .groupby(['gender', 'genre'])
        .size()
        .reset_index(name='count')
    )
    # transform('sum') replica il totale del gruppo su ogni riga → divisione per normalizzare
    counts_gen['pct'] = (
        counts_gen['count']
        / counts_gen.groupby('gender')['count'].transform('sum')
        * 100
    )

    # pivot: righe = genere anime, colonne = genere utente, valori = % — ordinato per Female
    pivot_gen = (
        counts_gen
        .pivot(index='genre', columns='gender', values='pct')
        .fillna(0)
        .sort_values('Female', ascending=False)
    )

    groups = [('Female', '#e07b8a'), ('Non-Binary', '#8e6bbf'), ('Male', '#5c8ee0')]
    fig = go.Figure()
    for col, color in groups:
        if col not in pivot_gen.columns:
            continue
        fig.add_trace(go.Bar(
            name=col,
            x=pivot_gen.index.tolist(),
            y=pivot_gen[col].round(2),
            marker_color=color,
            hovertemplate='<b>%{x}</b><br>' + col + ': %{y:.2f}%<extra></extra>',
        ))

    fig.update_layout(
        barmode='group',   # barre affiancate per confronto diretto tra generi utente
        title=dict(
            text='Distribuzione dei generi per genere utente (solo anime completati)<br>',
            font=dict(size=15),
        ),
        xaxis=dict(title='Genere Anime', tickangle=-40),
        yaxis=dict(title='% sul totale completato per gruppo', ticksuffix='%'),
        legend=dict(title='Genere utente', font=dict(size=11)),
        template='plotly_white',
        hovermode='x unified',
        width=1000, height=520,
    )
    fig.show()

# Funzione utilizzata per il grafico delle generazioni
def plot_generation_radar(ratings, profiles, details_ex, generi):
    """Spider/radar chart Plotly con il profilo dei generi completati per generazione (Boomer, Gen X, Millennial, Gen Z), classificate tramite l'anno di nascita."""
    # estrae l'anno di nascita come numero, scartando le righe non convertibili
    profiles_bday = profiles.dropna(subset=['birthday']).copy()
    profiles_bday['birth_year'] = pd.to_numeric(profiles_bday['birthday'], errors='coerce')
    profiles_bday = profiles_bday.dropna(subset=['birth_year'])

    # classifica ogni utente nella propria generazione tramite intervalli di anni di nascita
    bins   = [0, 1945, 1964, 1980, 1996, 2012, 9999]
    labels = ['Silent', 'Boomer', 'Gen X', 'Millennial', 'Gen Z', 'Gen Alpha']
    profiles_bday['generation'] = pd.cut(profiles_bday['birth_year'], bins=bins, labels=labels)

    gen_focus  = ['Boomer', 'Gen X', 'Millennial', 'Gen Z']
    gen_colors = {'Boomer': '#e07b3a', 'Gen X': '#8e6bbf', 'Millennial': '#5c8ee0', 'Gen Z': '#4caf7d'}

    # join tra rating completati e utenti con generazione nota
    r_cohort = (
        ratings
        .query("status == 'completed'")
        .merge(
            profiles_bday.loc[profiles_bday['generation'].isin(gen_focus), ['username', 'generation']],
            on='username',
        )
    )

    # conta per (generazione, genere) e normalizza sul totale completato per generazione
    counts_cohort = (
        r_cohort
        .merge(details_ex, left_on='anime_id', right_on='mal_id')
        .query('genre in @generi')
        .groupby(['generation', 'genre'])
        .size()
        .reset_index(name='count')
    )
    counts_cohort['pct'] = (
        counts_cohort['count']
        / counts_cohort.groupby('generation')['count'].transform('sum')
        * 100
    )

    all_genres = list(generi)
    # pivot: righe = generazione, colonne = genere, riordinato secondo gen_focus
    gen_pivot  = (
        counts_cohort
        .pivot(index='generation', columns='genre', values='pct')
        .fillna(0)
        .reindex(gen_focus)[all_genres]
    )

    # il radar richiede che il primo e l'ultimo punto coincidano per chiudere il poligono
    categories = all_genres + [all_genres[0]]
    fig = go.Figure()
    for gen in gen_focus:
        values = gen_pivot.loc[gen].tolist() + [gen_pivot.loc[gen].tolist()[0]]
        fig.add_trace(go.Scatterpolar(
            r=values, theta=categories,
            fill='toself', fillcolor=gen_colors[gen],
            line=dict(color=gen_colors[gen], width=2),
            opacity=0.25,   # trasparenza per vedere la sovrapposizione tra generazioni
            name=gen,
            hovertemplate='<b>' + gen + '</b><br>%{theta}: %{r:.2f}%<extra></extra>',
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, ticksuffix='%', tickfont=dict(size=9), gridcolor='lightgrey'),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        title=dict(
            text='Profilo dei generi completati per generazione<br>',
            font=dict(size=15),
        ),
        legend=dict(font=dict(size=11)),
        template='plotly_white',
        width=800, height=800,
    )
    fig.show()

# Funzione utilizzata per creare grafico sulla geografia
def plot_country_map(ratings, profiles, details_ex, generi):
    """Mappa Plotly che mostra per ogni paese il genere con la deviazione positiva più alta rispetto alla media globale. L'hover mostra i top 5 generi distintivi."""
    paesi = profiles['location'].dropna().value_counts().index
    profiles_loc = profiles.loc[profiles['location'].isin(paesi), ['username', 'location']]

    # conta le occorrenze per (paese, genere) sugli anime completati
    counts_country = (
        ratings
        .query("status == 'completed'")
        .merge(profiles_loc, on='username')
        .merge(details_ex, left_on='anime_id', right_on='mal_id')
        .query('genre in @generi')
        .groupby(['location', 'genre'])
        .size()
        .reset_index(name='count')
    )
    # percentuale di ogni genere sul totale completato per paese
    counts_country['pct'] = (
        counts_country['count']
        / counts_country.groupby('location')['count'].transform('sum')
        * 100
    )

    # media globale di ogni genere tra tutti i paesi
    global_avg = counts_country.groupby('genre')['pct'].mean()
    # deviazione = quanto il paese si discosta dalla media globale per quel genere
    counts_country['deviation'] = counts_country.apply(
        lambda row: row['pct'] - global_avg[row['genre']], axis=1
    )

    # pivot: righe = paese, colonne = genere, valori = deviazione dalla media globale
    country_deviation = (
        counts_country
        .pivot(index='location', columns='genre', values='deviation')
        .fillna(0)[generi]
    )
    # ordina i paesi per "distintività" totale (somma dei valori assoluti delle deviazioni)
    country_deviation = country_deviation.loc[
        country_deviation.abs().sum(axis=1).sort_values(ascending=False).index
    ]

    # dizionario nome paese → codice ISO
    iso_map = pd.Series({
        'Japan': 'JPN', 'United States': 'USA', 'Germany': 'DEU',
        'United Kingdom': 'GBR', 'Thailand': 'THA', 'Argentina': 'ARG',
        'China': 'CHN', 'Spain': 'ESP', 'France': 'FRA', 'Australia': 'AUS',
        'Mexico': 'MEX', 'South Korea': 'KOR', 'Turkey': 'TUR', 'Italy': 'ITA',
        'Indonesia': 'IDN', 'Brazil': 'BRA', 'Vietnam': 'VNM', 'South Africa': 'ZAF',
        'Philippines': 'PHL', 'Egypt': 'EGY', 'India': 'IND', 'Canada': 'CAN',
    })

    def top5_deviation(country):
        """Ritorna i 5 generi con deviazione positiva più alta per un paese, con i relativi valori."""
        if country not in country_deviation.index:
            return [''] * 5, [0.0] * 5
        row = country_deviation.loc[country].sort_values(ascending=False).head(5)
        return list(row.index), list(row.values)

    # per ogni paese: genere dominante (massima deviazione) e codice ISO
    map_data = (
        country_deviation
        .idxmax(axis=1)
        .reset_index()
        .rename(columns={'location': 'country', 0: 'dominant_genre'})
        .assign(iso=lambda df: df['country'].map(iso_map))
        .dropna(subset=['iso'])   # scarta paesi non presenti nel dizionario iso_map
    )
    # aggiunge colonne g1–g5 e dev1–dev5 per i top 5 generi distintivi (usate nell'hover)
    for k in range(5):
        map_data[f'g{k+1}']   = map_data['country'].apply(lambda c: top5_deviation(c)[0][k])
        map_data[f'dev{k+1}'] = map_data['country'].apply(lambda c: round(top5_deviation(c)[1][k], 2))

    fig = px.choropleth(
        map_data,
        locations='iso', color='dominant_genre', hover_name='country',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title='Genere più guardato rispetto alla media globale per paese',
        labels={'dominant_genre': 'Genere più sopra la media'},
        # custom_data passa i 10 valori (5 generi + 5 deviazioni) al template hover
        custom_data=['g1','dev1','g2','dev2','g3','dev3','g4','dev4','g5','dev5'],
    )
    fig.update_traces(
        hovertemplate=(
            '<b>%{hovertext}</b><br><br>'
            'Generi più sopra la media globale:<br>'
            '1. %{customdata[0]}: %{customdata[1]:+.2f}%<br>'
            '2. %{customdata[2]}: %{customdata[3]:+.2f}%<br>'
            '3. %{customdata[4]}: %{customdata[5]:+.2f}%<br>'
            '4. %{customdata[6]}: %{customdata[7]:+.2f}%<br>'
            '5. %{customdata[8]}: %{customdata[9]:+.2f}%'
            '<extra></extra>'
        )
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type='natural earth'),
        legend_title_text='Genere più sopra media',
        margin=dict(l=0, r=0, t=40, b=0),
        height=500,
    )
    fig.show()
