from jupyter_dash import JupyterDash
JupyterDash.infer_jupyter_proxy_config()

import base64
import os
import logging
import pandas as pd

import dash_leaflet as dl
from dash import dcc, html
import plotly.express as px
from dash import dash_table
from dash.dependencies import Input, Output

from logging_config import configure_logging
from data.mongo_repo import AnimalRepository
from services.query_service import build_rescue_query, validate_filter_type
from services.ranking_service import criteria_for_filter, rank_results
from services.result_service import sanitize_rows

logger = logging.getLogger("grazioso.app")

configure_logging()

repo = AnimalRepository()
repo.ensure_indexes()

app = JupyterDash(__name__)

image_filename = "Grazioso Salvare Logo.png"
encoded_image = ""
if os.path.exists(image_filename):
    encoded_image = base64.b64encode(open(image_filename, "rb").read()).decode()

app.layout = html.Div([
    html.Center(html.Img(
        src=f"data:image/png;base64,{encoded_image}" if encoded_image else None,
        style={"width": "200px", "display": "block"} if encoded_image else {"display": "none"},
    )),
    html.Center(html.B(html.H1("SNHU CS-340 Dashboard"))),
    html.H1("Project Two - Daniel Beale", style={"textAlign": "center", "color": "#2c3e50"}),
    html.Hr(),

    html.Div([
        html.Label("Select Rescue Type:", style={"font-weight": "bold"}),
        dcc.RadioItems(
            id="filter-type",
            options=[
                {"label": "All", "value": "all"},
                {"label": "Water Rescue", "value": "water"},
                {"label": "Mountain or Wilderness Rescue", "value": "mountain"},
                {"label": "Disaster or Individual Tracking", "value": "disaster"},
            ],
            value="all",
            inline=True,
        )
    ], style={"textAlign": "center"}),

    html.Hr(),

    dash_table.DataTable(
        id="datatable-id",
        columns=[],
        data=[],
        editable=False,
        filter_action="none",
        sort_action="custom",
        sort_mode="multi",
        sort_by=[],
        page_action="custom",
        page_current=0,
        page_size=10,
        row_selectable="single",
        selected_rows=[0],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "minWidth": "100px", "maxWidth": "200px", "whiteSpace": "normal"},
        style_header={"backgroundColor": "rgb(230,230,230)", "fontWeight": "bold"},
    ),

    html.Br(),
    html.Hr(),

    # Chart + Map side-by-side (summary is below, not inside the flex row)
    html.Div(style={"display": "flex"}, children=[
        html.Div(id="graph-id", style={"flex": "1", "paddingRight": "10px"}),
        html.Div(id="map-id", style={"flex": "1", "paddingLeft": "10px"}),
    ]),

    html.Hr(),
    html.Div(id="summary-id"),
])


@app.callback(
    Output("datatable-id", "data"),
    Output("datatable-id", "columns"),
    Input("filter-type", "value"),
    Input("datatable-id", "page_current"),
    Input("datatable-id", "page_size"),
    Input("datatable-id", "sort_by"),
)
def update_table(filter_type, page_current, page_size, sort_by):
    """
    Server-side pagination and sorting using MongoDB skip/limit and sort.
    Algorithmic enhancement: compute match_score and rank results.
    Predictable failure behavior: empty output on invalid input / DB errors.
    """
    try:
        validate_filter_type(filter_type)
    except ValueError:
        logger.warning("Invalid filter type received: %s", filter_type)
        return [], []

    if not repo.ping():
        logger.error("Database unavailable for query")
        return [], []

    query = build_rescue_query(filter_type)
    criteria = criteria_for_filter(filter_type)

    # Mongo sort is ONLY for real DB fields. match_score is computed after retrieval.
    mongo_sort = None
    if sort_by:
        mongo_sort = [(s["column_id"], 1 if s["direction"] == "asc" else -1) for s in sort_by]

    # Pagination
    page_current = page_current or 0
    page_size = page_size or 10
    skip = page_current * page_size

    # Read page slice
    rows = repo.read(query, sort=mongo_sort, skip=skip, limit=page_size)
    rows = sanitize_rows(rows)

    if not rows:
        return [], []

    # Rank page results (adds match_score)
    ranked = rank_results(rows, criteria)

    # Default ordering: highest score first. If user chose sorts, keep their order by not overriding.
    if not sort_by:
        ranked = sorted(ranked, key=lambda r: r.get("match_score", 0), reverse=True)

    cols = [{"name": c, "id": c, "deletable": False, "selectable": True} for c in ranked[0].keys()]

    logger.info("update_table ok filter=%s page=%d results=%d", filter_type, page_current, len(ranked))
    return ranked, cols


@app.callback(
    Output("datatable-id", "style_data_conditional"),
    Input("datatable-id", "selected_columns"),
)
def update_styles(selected_columns):
    selected_columns = selected_columns or []
    return [{"if": {"column_id": i}, "background_color": "#D2F3FF"} for i in selected_columns]


@app.callback(
    Output("graph-id", "children"),
    Input("filter-type", "value"),
)
def update_graph(filter_type):
    """
    Database enhancement: server-side aggregation for breed counts.
    """
    try:
        validate_filter_type(filter_type)
    except ValueError:
        return [html.H5("Invalid filter.")]

    if not repo.ping():
        return [html.H5("Database unavailable.")]

    query = build_rescue_query(filter_type)
    counts = repo.aggregate_breed_counts(query)

    if not counts:
        return [html.H5("No data available for this filter.")]

    fig = px.bar(
        counts,
        x="breed",
        y="count",
        title="Breed Distribution for Selected Rescue Type",
        labels={"breed": "Breed", "count": "Number of Dogs"},
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return [dcc.Graph(figure=fig)]


@app.callback(
    Output("summary-id", "children"),
    Input("filter-type", "value"),
)
def update_summary(filter_type):
    """
    Database enhancement: additional aggregation rollups for decision-making.
    """
    try:
        validate_filter_type(filter_type)
    except ValueError:
        return html.P("Invalid filter.")

    if not repo.ping():
        return html.P("Database unavailable.")

    query = build_rescue_query(filter_type)

    sex_counts = repo.aggregate_sex_counts(query) if hasattr(repo, "aggregate_sex_counts") else []
    age_summary = repo.aggregate_age_summary(query) if hasattr(repo, "aggregate_age_summary") else []

    parts = []
    if sex_counts:
        parts.append(html.H4("Outcome Sex Breakdown"))
        parts.append(html.Ul([html.Li(f"{r.get('sex_upon_outcome')}: {r.get('count')}") for r in sex_counts]))

    if age_summary:
        s = age_summary[0]
        parts.append(html.H4("Age Summary (weeks)"))
        parts.append(html.P(
            f"Min: {s.get('min_weeks')}, Max: {s.get('max_weeks')}, Avg: {round(float(s.get('avg_weeks', 0)), 2)}"
        ))

    if not parts:
        return html.P("No summary data available.")

    return html.Div(parts)


@app.callback(
    Output("map-id", "children"),
    Input("datatable-id", "derived_virtual_data"),
    Input("datatable-id", "derived_virtual_selected_rows"),
)
def update_map(viewData, selected_rows):
    """
    Update map to show location of selected dog record.
    Includes predictable behavior if location fields are missing/malformed.
    """
    dff = pd.DataFrame(viewData) if viewData else pd.DataFrame()
    if dff.empty:
        return [html.H5("No location data to display.")]

    row = (selected_rows[0] if selected_rows else 0)
    row = min(max(row, 0), len(dff) - 1)

    # Prefer named columns if present; fallback to original positional indexing.
    lat = None
    lon = None

    if "location_lat" in dff.columns and "location_long" in dff.columns:
        try:
            lat = float(dff.loc[dff.index[row], "location_lat"])
            lon = float(dff.loc[dff.index[row], "location_long"])
        except Exception:
            lat = None
            lon = None

    if lat is None or lon is None:
        try:
            lat = float(dff.iloc[row, 13])
            lon = float(dff.iloc[row, 14])
        except Exception:
            return [html.H5("Location fields unavailable for selected record.")]

    tooltip = str(dff.iloc[row, 4]) if dff.shape[1] > 4 else "Selected"
    popup_text = str(dff.iloc[row, 9]) if dff.shape[1] > 9 else ""

    return [
        dl.Map(
            style={"width": "1000px", "height": "500px"},
            center=[30.75, -97.48],
            zoom=10,
            children=[
                dl.TileLayer(id="base-layer-id"),
                dl.Marker(
                    position=[lat, lon],
                    children=[
                        dl.Tooltip(tooltip),
                        dl.Popup([html.H1("Animal Name"), html.P(popup_text)]),
                    ],
                ),
            ],
        )
    ]


app.run_server()