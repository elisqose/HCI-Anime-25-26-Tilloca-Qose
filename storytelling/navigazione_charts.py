import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _build_source_stats(details):
    """Calcola aggregati per fonte (n_titoli, score_medio, favorites_medio) e palette colori."""
    source_agg = (
        details
        .dropna(subset=['source', 'score'])
        .groupby('source')
        .agg(
            n_titoli=('mal_id', 'count'),
            score_medio=('score', 'mean'),
            favorites_medio=('favorites', 'mean'),
        )
        .reset_index()
        .query('n_titoli >= 30')
        .sort_values('n_titoli', ascending=False)
        .reset_index(drop=True)
    )
    palette = px.colors.qualitative.Alphabet[:len(source_agg)]
    color_map = dict(zip(source_agg['source'], palette))
    return source_agg, color_map


def plot_genre_map(details):
    """Scatter Plotly: ogni genere posizionato per numero di titoli (X) e score medio (Y)."""
    det_g = details.dropna(subset=['genres', 'score']).copy()
    det_g['genre'] = det_g['genres'].str[2:-2].str.split("', '")
    det_g = det_g.explode('genre')
    det_g = det_g[det_g['genre'].str.strip() != '']

    genre_stats = (
        det_g.groupby('genre')
        .agg(n_titoli=('mal_id', 'count'), score_medio=('score', 'mean'))
        .query('n_titoli >= 30')
        .sort_values('score_medio', ascending=False)
        .reset_index()
    )

    score_mean = genre_stats['score_medio'].mean()

    fig = px.scatter(
        genre_stats,
        x='n_titoli',
        y='score_medio',
        color='score_medio',
        color_continuous_scale='RdYlGn',
        hover_name='genre',
        hover_data={'n_titoli': True, 'score_medio': ':.2f'},
        labels={
            'n_titoli': 'Numero di titoli nel genere',
            'score_medio': 'Score medio MAL',
        },
        title='<b>La mappa dei generi: volume e qualità media per ogni territorio del catalogo</b>',
    )

    fig.update_traces(marker=dict(size=10, line=dict(color='white', width=1)))

    custom_offsets = {
        'Girls Love':    dict(xshift=-30, yshift=12),
        'Boys Love':     dict(xshift=40,  yshift=12),
        'Gourmet':       dict(xshift=0,   yshift=-18),
        'Ecchi':         dict(xshift=-25, yshift=0),
        'Slice of Life': dict(xshift=40,  yshift=0),
        'Comedy':        dict(xshift=12,  yshift=-10),
    }
    default_offset = dict(xshift=12, yshift=9)

    for _, row in genre_stats.iterrows():
        off = custom_offsets.get(row['genre'], default_offset)
        fig.add_annotation(
            x=row['n_titoli'], y=row['score_medio'],
            text=row['genre'], showarrow=False,
            font=dict(size=11), **off,
        )

    fig.add_hline(
        y=score_mean, line_dash='dash', line_color='grey', opacity=0.5,
        annotation_text='score medio globale', annotation_position='top right',
        annotation_font_size=11, annotation_font_color='grey',
    )

    fig.update_layout(
        font_size=12, title_font_size=14,
        coloraxis_colorbar=dict(title='Score medio'),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        height=600,
    )
    fig.show()


def plot_hall_of_fame(details):
    """Due bar chart orizzontali affiancati: top 10 per favorites e top 10 per score."""
    top_score = (
        details
        .query('scored_by >= 10000')
        .nlargest(10, 'score')
        [['title', 'score', 'favorites', 'year']]
        .reset_index(drop=True)
    )
    top_fav = (
        details
        .nlargest(10, 'favorites')
        [['title', 'favorites', 'score']]
        .reset_index(drop=True)
    )

    in_both    = set(top_score['title']) & set(top_fav['title'])
    COLOR_BOTH = '#F4863E'
    COLOR_SOLO = '#5B8DB8'

    def trunc(t, n=18):
        return t[:n] + '...' if len(t) > n else t

    fav_titles_r   = top_fav['title'][::-1].tolist()
    fav_values_r   = top_fav['favorites'][::-1].tolist()
    score_titles_r = top_score['title'][::-1].tolist()
    score_values_r = top_score['score'][::-1].tolist()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=['Top 10 per Favorites', 'Top 10 per Score'],
        vertical_spacing=0.14,
    )

    fig.add_trace(go.Bar(
        y=[trunc(t) for t in fav_titles_r], x=fav_values_r, orientation='h',
        marker_color=[COLOR_BOTH if t in in_both else COLOR_SOLO for t in fav_titles_r],
        hovertext=fav_titles_r,
        hovertemplate='<b>%{hovertext}</b><br>Favorites: %{x:,}<extra></extra>',
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=[trunc(t) for t in score_titles_r], x=score_values_r, orientation='h',
        marker_color=[COLOR_BOTH if t in in_both else COLOR_SOLO for t in score_titles_r],
        hovertext=score_titles_r,
        hovertemplate='<b>%{hovertext}</b><br>Score: %{x:.2f}<extra></extra>',
        showlegend=False,
    ), row=2, col=1)

    fig.add_trace(go.Bar(x=[None], y=[None], orientation='h',
                         marker_color=COLOR_BOTH, name='Appare in più classifiche'))
    fig.add_trace(go.Bar(x=[None], y=[None], orientation='h',
                         marker_color=COLOR_SOLO, name='Solo in questa'))

    fig.update_layout(
        height=800, plot_bgcolor='white', paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='top', y=-0.08,
                    xanchor='center', x=0.5, font_size=12),
        margin=dict(b=120),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', zeroline=False)
    fig.update_yaxes(showgrid=False, tickfont_size=11)
    fig.update_xaxes(title_text='Numero di Favorites', row=1, col=1)
    fig.update_xaxes(
        range=[top_score['score'].min() - 0.3, top_score['score'].max() + 0.15],
        title_text='Score MAL', row=2, col=1,
    )
    fig.show()


def plot_source_distribution(details):
    """Due bar chart orizzontali: numero di titoli per fonte e score medio per fonte."""
    source_agg, color_map = _build_source_stats(details)
    source_score = source_agg.sort_values('score_medio', ascending=True)

    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.22,
        subplot_titles=['Numero di titoli per fonte', 'Score medio MAL per fonte'],
    )

    fig.add_trace(go.Bar(
        y=source_agg['source'], x=source_agg['n_titoli'], orientation='h',
        marker_color=[color_map[s] for s in source_agg['source']],
        hovertemplate='<b>%{y}</b><br>Titoli: %{x:,}<extra></extra>',
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        y=source_score['source'], x=source_score['score_medio'].round(2), orientation='h',
        marker_color=[color_map[s] for s in source_score['source']],
        hovertemplate='<b>%{y}</b><br>Score medio: %{x:.2f}<extra></extra>',
        showlegend=False,
    ), row=1, col=2)

    fig.update_layout(
        height=520,
        title=dict(text='<b>Da dove nascono gli anime: distribuzione e qualità media per fonte</b>',
                   x=0.5, font_size=14),
        plot_bgcolor='white', paper_bgcolor='white',
    )
    fig.update_xaxes(showgrid=True, gridcolor='#f0f0f0', zeroline=False,
                     title_text='Titoli', row=1, col=1)
    fig.update_xaxes(
        showgrid=True, gridcolor='#f0f0f0', zeroline=False,
        range=[source_score['score_medio'].min() - 0.3, source_score['score_medio'].max() + 0.15],
        title_text='Score medio', row=1, col=2,
    )
    fig.update_yaxes(showgrid=False)
    fig.show()


def plot_source_scatter(details):
    """Scatter Plotly: ogni anime posizionato per n. valutazioni (X, log) e score (Y), colorato per fonte."""
    source_agg, color_map = _build_source_stats(details)
    ndet_src = (
        details
        .dropna(subset=['source', 'score', 'scored_by'])
        .query('scored_by >= 0 and source in @source_agg.source.tolist()')
        .copy()
    )

    fig = px.scatter(
        ndet_src.sort_values('source'),
        x='scored_by', y='score',
        color='source', color_discrete_map=color_map,
        hover_name='title',
        hover_data={'source': True, 'scored_by': ':,', 'score': ':.2f', 'year': True, 'type': True},
        labels={
            'scored_by': 'Numero di valutazioni (scala log)',
            'score': 'Score MAL',
            'source': 'Fonte',
        },
        title='<b>Qualità e popolarità per fonte: ogni punto è un anime</b>',
        log_x=True, opacity=0.55,
    )
    fig.update_traces(marker=dict(size=5, line=dict(width=0.3, color='white')))
    fig.update_layout(
        height=560, plot_bgcolor='white', paper_bgcolor='white',
        title_font_size=14,
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        legend=dict(title='Fonte', font_size=11),
    )
    fig.show()


def plot_drop_heatmap(details, stats):
    """Heatmap Plotly del tasso di abbandono medio (%) per ogni combinazione genere × fonte."""
    top_genres = (
        details.dropna(subset=['genres'])
        .assign(genre=lambda d: d['genres'].str[2:-2].str.split("', '"))
        .explode('genre')
        .pipe(lambda d: d[d['genre'].str.strip() != ''])
        ['genre'].value_counts().head(12).index.tolist()
    )
    main_sources = ['Manga', 'Light novel', 'Visual novel', 'Novel', 'Web manga', 'Game', 'Original']

    merged = (
        stats
        .assign(
            engaged=lambda d: d['watching'] + d['completed'] + d['on_hold'] + d['dropped'],
            drop_rate=lambda d: d['dropped'] / d['engaged'].replace(0, float('nan')),
        )
        .merge(details[['mal_id', 'source', 'genres']], on='mal_id')
        .assign(genre=lambda d: d['genres'].str[2:-2].str.split("', '"))
        .explode('genre')
        .pipe(lambda d: d[d['genre'].str.strip() != ''])
    )

    pivot = (
        merged
        .query('genre in @top_genres and source in @main_sources')
        .groupby(['source', 'genre'])['drop_rate']
        .mean()
        .unstack(fill_value=float('nan'))
        .reindex(main_sources)[top_genres]
        * 100
    )

    genre_order = pivot.mean(axis=0).sort_values(ascending=False).index
    pivot = pivot[genre_order]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale='YlOrRd',
        zmin=4, zmax=25,
        text=pivot.round(1).astype(str).values,
        texttemplate='%{text}%',
        textfont=dict(size=11),
        hovertemplate='<b>%{y} — %{x}</b><br>Tasso di abbandono: %{z:.1f}%<extra></extra>',
        colorbar=dict(title='Abbandono (%)', ticksuffix='%'),
    ))

    fig.update_layout(
        title=dict(text='<b>Tasso di abbandono per genere e fonte: quali anime si finiscono davvero?</b>',
                   font_size=14),
        xaxis=dict(title='Genere', tickangle=-35),
        yaxis=dict(title='Fonte', autorange='reversed'),
        plot_bgcolor='white', paper_bgcolor='white',
        height=380,
    )
    fig.show()


def plot_hidden_gems(details):
    """Scatter Plotly dei titoli con score ≥ 8.0 e tra 200 e 4.999 valutazioni."""
    hidden_all = (
        details
        .query('score >= 8.0 and scored_by >= 200 and scored_by < 5000')
        .sort_values('score', ascending=False)
        .reset_index(drop=True)
    )

    n_found = len(hidden_all)

    fig = px.scatter(
        hidden_all,
        x='scored_by', y='score',
        color='source',
        hover_name='title',
        hover_data={'source': True, 'scored_by': ':,', 'score': ':.2f', 'year': True, 'type': True},
        labels={
            'scored_by': 'Numero di valutazioni  ←  più raro   /   più conosciuto  →',
            'score': 'Score MAL',
            'source': 'Fonte',
        },
        title=f'<b>{n_found} capolavori nascosti: score ≥ 8.0, meno di 5.000 valutazioni</b>',
    )

    fig.update_traces(marker=dict(size=11, line=dict(width=0.8, color='white')))
    fig.update_layout(
        height=580, plot_bgcolor='white', paper_bgcolor='white',
        title_font_size=14,
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', zeroline=False),
        legend=dict(title='Fonte', font_size=11),
    )
    fig.show()
