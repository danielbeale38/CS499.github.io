# --- Data Manipulation / Model ---
username = os.getenv("AAC_USERNAME", "myTester")
password = os.getenv("AAC_PASSWORD", "Panda367")
shelter = AnimalShelter(username, password)

df = pd.DataFrame.from_records(shelter.read({}))
if not df.empty and "_id" in df.columns:
    df.drop(columns=["_id"], inplace=True)

# ---- Update Data Table ----
@app.callback(Output('datatable-id', 'data'),
              [Input('filter-type', 'value')])
def update_dashboard(filter_type):
    query = get_query(filter_type)
    filtered_df = pd.DataFrame.from_records(shelter.read(query))
    if not filtered_df.empty and "_id" in filtered_df.columns:
        filtered_df.drop(columns=["_id"], inplace=True)
    return filtered_df.to_dict("records")

# ---- Breed Distribution Chart (true counts) ----
@app.callback(Output('graph-id', "children"),
              [Input('datatable-id', "derived_virtual_data")])
def update_graph(viewData):
    dff = pd.DataFrame(viewData) if viewData else pd.DataFrame()
    if dff.empty or "breed" not in dff.columns:
        return [html.H5("No data available for this filter.")]

    counts = (
        dff["breed"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
        .rename(columns={"index": "breed", "breed": "count"})
    )

    fig = px.bar(
        counts,
        x="breed",
        y="count",
        title="Breed Distribution for Selected Rescue Type",
        labels={"breed": "Breed", "count": "Number of Dogs"},
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return [dcc.Graph(figure=fig)]

# ---- Geolocation Map (use column names, not positions) ----
LAT_COL = "location_lat"   # change to your actual field name
LON_COL = "location_long"  # change to your actual field name
LABEL_COL = "breed"        # or "name"
POPUP_COL = "name"         # change if your dataset uses a different field

@app.callback(Output('map-id', "children"),
              [Input('datatable-id', "derived_virtual_data"),
               Input('datatable-id', "derived_virtual_selected_rows")])
def update_map(viewData, index):
    dff = pd.DataFrame(viewData) if viewData else pd.DataFrame()
    if dff.empty or LAT_COL not in dff.columns or LON_COL not in dff.columns:
        return [html.H5("No location data to display.")]

    row = (index[0] if index else 0)

    lat = dff.iloc[row][LAT_COL]
    lon = dff.iloc[row][LON_COL]
    if pd.isna(lat) or pd.isna(lon):
        return [html.H5("Selected record has no coordinates.")]

    tooltip_text = str(dff.iloc[row].get(LABEL_COL, "Selected Animal"))
    popup_text = str(dff.iloc[row].get(POPUP_COL, ""))

    return [
        dl.Map(
            style={"width": "1000px", "height": "500px"},
            center=[30.75, -97.48],
            zoom=10,
            children=[
                dl.TileLayer(id="base-layer-id"),
                dl.Marker(
                    position=[float(lat), float(lon)],
                    children=[
                        dl.Tooltip(tooltip_text),
                        dl.Popup([html.H1("Animal"), html.P(popup_text)]),
                    ],
                ),
            ],
        )
    ]