import pdb

from utils import load_fema_data, add_coords, group_by_incident, plot_geo_bubble_map, plot_incident_type_dropdown_map, \
    plot_grouped_map_with_dropdown, plot_grouped_choropleth_with_dropdown, plot_grouped_choropleth_with_dropdown_u

# from utils import load_disaster_data


if __name__ == "__main__":
    df = load_fema_data()
    print(df.columns)
    df = add_coords(df)
    grouped = group_by_incident(df)
    # plot_geo_bubble_map(grouped)
    # plot_incident_type_dropdown_map(df)

    plot_grouped_choropleth_with_dropdown_u(df)
    # Create map
