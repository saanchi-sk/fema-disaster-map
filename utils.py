import pdb

import pandas as pd
import requests
import plotly.express as px

from constants import FEMA_API
import plotly.graph_objects as go


# US State Centroids (for plotting)
import pandas as pd
import requests
import plotly.express as px
from constants import FEMA_API

# US State Centroids (for plotting with full state names)
state_coords = {
    "Alabama": (32.806671, -86.791130), "Alaska": (61.370716, -152.404419), "Arizona": (33.729759, -111.431221),
    "Arkansas": (34.969704, -92.373123), "California": (36.116203, -119.681564), "Colorado": (39.059811, -105.311104),
    "Connecticut": (41.597782, -72.755371), "Delaware": (39.318523, -75.507141), "Florida": (27.766279, -81.686783),
    "Georgia": (33.040619, -83.643074), "Hawaii": (21.094318, -157.498337), "Idaho": (44.240459, -114.478828),
    "Illinois": (40.349457, -88.986137), "Indiana": (39.849426, -86.258278), "Iowa": (42.011539, -93.210526),
    "Kansas": (38.526600, -96.726486), "Kentucky": (37.668140, -84.670067), "Louisiana": (31.169546, -91.867805),
    "Maine": (44.693947, -69.381927), "Maryland": (39.063946, -76.802101), "Massachusetts": (42.230171, -71.530106),
    "Michigan": (43.326618, -84.536095), "Minnesota": (45.694454, -93.900192), "Mississippi": (32.741646, -89.678696),
    "Missouri": (38.456085, -92.288368), "Montana": (46.921925, -110.454353), "Nebraska": (41.125370, -98.268082),
    "Nevada": (38.313515, -117.055374), "New Hampshire": (43.452492, -71.563896), "New Jersey": (40.298904, -74.521011),
    "New Mexico": (34.840515, -106.248482), "New York": (42.165726, -74.948051), "North Carolina": (35.630066, -79.806419),
    "North Dakota": (47.528912, -99.784012), "Ohio": (40.388783, -82.764915), "Oklahoma": (35.565342, -96.928917),
    "Oregon": (44.572021, -122.070938), "Pennsylvania": (40.590752, -77.209755), "Rhode Island": (41.680893, -71.511780),
    "South Carolina": (33.856892, -80.945007), "South Dakota": (44.299782, -99.438828), "Tennessee": (35.747845, -86.692345),
    "Texas": (31.054487, -97.563461), "Utah": (40.150032, -111.862434), "Vermont": (44.045876, -72.710686),
    "Virginia": (37.769337, -78.169968), "Washington": (47.400902, -121.490494), "West Virginia": (38.491226, -80.954571),
    "Wisconsin": (44.268543, -89.616508), "Wyoming": (42.755966, -107.302490), "District of Columbia": (38.897438, -77.026817),
    "Puerto Rico": (18.220833, -66.590149)
}

# Load FEMA disaster data
def load_fema_data():
    response = requests.get(FEMA_API)
    response.raise_for_status()
    data = response.json()["FemaWebDisasterDeclarations"]
    df = pd.DataFrame(data)
    df = df.rename(columns={
        "disasterNumber": "disaster_number",
        "stateName": "state_name",
        "incidentType": "incident_type",
        "declarationDate": "declaration_date",
        "disasterName": "disaster_name"
    })
    return df

# Add lat/lon from full state names
def add_coords(df):
    df["state_name_clean"] = df["state_name"].str.strip().str.title()
    df["latitude"] = df["state_name_clean"].map(lambda x: state_coords.get(x, (None, None))[0])
    df["longitude"] = df["state_name_clean"].map(lambda x: state_coords.get(x, (None, None))[1])
    return df.dropna(subset=["latitude", "longitude"])

# Group by state and incident type
def group_by_incident(df):
    return (
        df.groupby(["state_name", "incident_type", "latitude", "longitude"])
        .size()
        .reset_index(name="disaster_count")
    )

# Plot by incident type
def plot_geo_bubble_map(df_grouped):
    fig = px.scatter_geo(
        df_grouped,
        lat="latitude",
        lon="longitude",
        color="incident_type",
        size="disaster_count",
        hover_name="state_name",
        hover_data=["incident_type", "disaster_count"],
        title="FEMA Disaster Declarations by State and Incident Type",
        projection="albers usa",
        template="plotly_dark"
    )
    fig.update_layout(legend_title_text="Incident Type")
    fig.show()


def plot_incident_type_dropdown_map(df):
    """
    Creates an interactive dropdown-based geo map of FEMA disaster declarations by incident type.

    Parameters:
        df (pd.DataFrame): Must contain 'incident_type', 'state_name_clean', 'latitude', 'longitude'
    """
    # Get unique incident types
    incident_types = df["incident_type"].dropna().unique()
    fig = go.Figure()

    # Create a trace for each incident type
    for i, incident in enumerate(incident_types):
        df_filtered = df[df["incident_type"] == incident]
        grouped = df_filtered.groupby(
            ["state_name_clean", "latitude", "longitude"]
        ).size().reset_index(name="disaster_count")

        fig.add_trace(go.Scattergeo(
            lon=grouped["longitude"],
            lat=grouped["latitude"],
            text=grouped["state_name_clean"] + "<br>Count: " + grouped["disaster_count"].astype(str),
            marker=dict(
                size=grouped["disaster_count"],
                sizemode='area',
                sizeref=2.*max(grouped["disaster_count"])/100**2,
                sizemin=4,
                color="lightskyblue",
                line_width=0.5
            ),
            name=incident,
            visible=(i == 0)  # Show only the first by default
        ))

    # Add dropdown buttons
    buttons = []
    for i, incident in enumerate(incident_types):
        visible = [False] * len(incident_types)
        visible[i] = True
        buttons.append(dict(
            label=incident,
            method="update",
            args=[{"visible": visible},
                  {"title": f"FEMA Disaster Declarations: {incident}"}]
        ))

    # Final layout
    fig.update_layout(
        title=f"FEMA Disaster Declarations: {incident_types[0]}",
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(10, 10, 10)",
        ),
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.05,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )]
    )

    fig.show()


def plot_grouped_map_with_dropdown(df):
    """
    Plots FEMA disaster declarations by grouped incident type with dropdown interaction.
    Color = disaster count (yellow to red), Hover = state + count
    """

    # Step 1: Incident group mapping
    incident_group_map = {
        "Hurricane": "Severe Weather", "Tornado": "Severe Weather",
        "Severe Storm": "Severe Weather", "Severe Ice Storm": "Severe Weather",
        "Tropical Storm": "Severe Weather", "Straight-Line Winds": "Severe Weather",
        "Coastal Storm": "Severe Weather",

        "Flood": "Water-related", "Dam/Levee Break": "Water-related", "Mud/Landslide": "Water-related",

        "Snowstorm": "Winter Weather", "Winter Storm": "Winter Weather",

        "Fire": "Fire",
        "Earthquake": "Earthquake", "Volcanic Eruption": "Earthquake",

        "Biological": "Other", "Other": "Other"
    }

    # Step 2: Group incident types
    df["incident_group"] = df["incident_type"].map(incident_group_map).fillna("Other")

    # Step 3: Group by incident group + location
    incident_groups = df["incident_group"].unique()
    fig = go.Figure()

    for i, group in enumerate(incident_groups):
        df_group = df[df["incident_group"] == group]
        grouped = df_group.groupby(["state_name_clean", "latitude", "longitude"]) \
                          .size().reset_index(name="disaster_count")

        fig.add_trace(go.Scattergeo(
            lat=grouped["latitude"],
            lon=grouped["longitude"],
            hoverinfo="text",
            text=grouped["state_name_clean"] + "<br>Count: " + grouped["disaster_count"].astype(str),
            marker=dict(
                size=grouped["disaster_count"],
                sizemode="area",
                sizeref=2.*max(grouped["disaster_count"])/100**2,
                sizemin=4,
                color=grouped["disaster_count"],
                colorscale="YlOrRd",
                colorbar_title="Disaster Count",
                line_width=0.5
            ),
            name=group,
            visible=(i == 0)  # Show only the first group
        ))

    # Step 4: Dropdown buttons
    buttons = []
    for i, group in enumerate(incident_groups):
        visibility = [j == i for j in range(len(incident_groups))]
        buttons.append(dict(
            label=group,
            method="update",
            args=[{"visible": visibility},
                  {"title": f"FEMA Declarations: {group}"}]
        ))

    # Step 5: Layout
    fig.update_layout(
        title=f"FEMA Declarations: {incident_groups[0]}",
        title_x=0.5,
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(10, 10, 10)"
        ),
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.05,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )]
    )

    fig.show()
def plot_grouped_choropleth_with_dropdown(df):
    """
    Creates a choropleth map of FEMA declarations by incident group.
    - Uses a dropdown menu to switch between grouped incident types.
    - Colors full states based on disaster count (YlOrRd scale).
    - Shows only state name and count in hover.
    """

    # Step 1: Group similar incident types
    incident_group_map = {
        "Hurricane": "Severe Weather", "Tornado": "Severe Weather",
        "Severe Storm": "Severe Weather", "Severe Ice Storm": "Severe Weather",
        "Tropical Storm": "Severe Weather", "Straight-Line Winds": "Severe Weather",
        "Coastal Storm": "Severe Weather",

        "Flood": "Water-related", "Dam/Levee Break": "Water-related", "Mud/Landslide": "Water-related",
        "Snowstorm": "Winter Weather", "Winter Storm": "Winter Weather",

        "Fire": "Fire", "Earthquake": "Earthquake", "Volcanic Eruption": "Other",
        "Biological": "Other", "Other": "Other"
    }

    df["incident_group"] = df["incident_type"].map(incident_group_map).fillna("Other")

    # Step 2: Ensure state codes are clean 2-letter codes
    df["stateCode"] = df["stateCode"].str.strip().str.upper()

    # Step 3: Get unique groups and build traces
    incident_groups = df["incident_group"].dropna().unique()
    fig = go.Figure()

    for i, group in enumerate(incident_groups):
        grouped = df[df["incident_group"] == group] \
                    .groupby("stateCode") \
                    .size().reset_index(name="disaster_count")

        fig.add_trace(go.Choropleth(
            locations=grouped["stateCode"],
            z=grouped["disaster_count"],
            locationmode="USA-states",
            colorscale="YlOrRd",
            colorbar_title="Disaster Count",
            text=grouped["stateCode"] + "<br>Count: " + grouped["disaster_count"].astype(str),
            hoverinfo="text",
            marker_line_color="black",  # ← Black state boundaries
            marker_line_width=1.2,
            visible=(i == 0)
        ))

    # Step 4: Create dropdown buttons
    buttons = []
    for i, group in enumerate(incident_groups):
        visibility = [j == i for j in range(len(incident_groups))]
        buttons.append(dict(
            label=group,
            method="update",
            args=[
                {"visible": visibility},
                {"title": {"text": f"FEMA Declarations: {group}", "x": 0.5}}
            ]
        ))

    # Step 5: Layout
    fig.update_layout(
        title=f"FEMA Declarations: {incident_groups[0]}",
        title_x=0.5,
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            # landcolor="rgb(10, 10, 10)"
            landcolor="white",  # ← white land
            bgcolor="white",  # ← white background behind globe
            lakecolor="lightblue",
            showlakes=True,
            coastlinecolor="gray",
            showcoastlines=True

        ),
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.05,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )]
    )

    fig.show()

def plot_grouped_choropleth_with_dropdown_u(df):
    # Incident type to group mapping
    incident_group_map = {
        "Hurricane": "Severe Weather", "Tornado": "Severe Weather",
        "Severe Storm": "Severe Weather", "Severe Ice Storm": "Severe Weather",
        "Tropical Storm": "Severe Weather", "Straight-Line Winds": "Severe Weather",
        "Coastal Storm": "Severe Weather",

        "Flood": "Water-related", "Dam/Levee Break": "Water-related", "Mud/Landslide": "Water-related",
        "Snowstorm": "Winter Weather", "Winter Storm": "Winter Weather",

        "Fire": "Fire", "Earthquake": "Earthquake", "Volcanic Eruption": "Other",
        "Biological": "Other", "Other": "Other"
    }

    df["incident_group"] = df["incident_type"].map(incident_group_map).fillna("Other")
    df["stateCode"] = df["stateCode"].str.strip().str.upper()

    # All US states + territories
    all_states = pd.Series([
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
        "DC", "PR", "GU", "AS", "VI", "MP"
    ], name="stateCode")

    # Unique incident groups
    incident_groups = df["incident_group"].dropna().unique()
    fig = go.Figure()

    for i, group in enumerate(incident_groups):
        grouped = df[df["incident_group"] == group] \
            .groupby("stateCode") \
            .size().reindex(all_states, fill_value=0) \
            .reset_index(name="disaster_count")

        fig.add_trace(go.Choropleth(
            locations=grouped["stateCode"],
            z=grouped["disaster_count"],
            locationmode="USA-states",
            zmin=0,
            colorscale=[[0.0, "white"]] + [[(i + 1) / len(px.colors.sequential.YlOrRd), c] for i, c in
                                           enumerate(px.colors.sequential.YlOrRd)],
            colorbar_title="Disaster Count",
            text=grouped["stateCode"] + "<br>Count: " + grouped["disaster_count"].astype(str),
            hoverinfo="text",
            marker_line_color="black",
            marker_line_width=1.2,
            visible=(i == 0)
        ))

    # Dropdown menu for incident group selection
    buttons = []
    for i, group in enumerate(incident_groups):
        visibility = [j == i for j in range(len(incident_groups))]
        buttons.append(dict(
            label=group,
            method="update",
            args=[
                {"visible": visibility},
                {"title": {"text": f"FEMA Declarations: {group}", "x": 0.5}}
            ]
        ))

    # Final layout
    fig.update_layout(
        title=f"FEMA Declarations: {incident_groups[0]}",
        title_x=0.5,
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="white",
            bgcolor="white",
            lakecolor="lightblue",
            showlakes=True,
            showcoastlines=True,
            coastlinecolor="gray"
        ),
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.05,
            xanchor="left",
            y=1.1,
            yanchor="top"
        )]
    )

    fig.show()
