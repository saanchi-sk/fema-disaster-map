# FEMA Disaster Declarations Map

This project uses the [FEMA Disaster Declarations API](https://www.fema.gov/api/open/v1/FemaWebDisasterDeclarations) to map and visualize areas in the U.S. that have received the most federal disaster declarations based on their incident type.

## Overview

- Fetches FEMA disaster data using Python's `requests`
- Parses and geocodes by state using centroids
- Displays visualizations to show hotspots of federal disaster declarations by location and type

## Features

- Group incidents by type (e.g., Severe Weather, Earthquake)
- Interactive maps with dropdown filters
- Color-coded choropleth maps with black state outlines
- Hover info for disaster counts by state
![Animated FEMA Map](fema_disasters.gif)

  

## Requirements

Install dependencies with:
pip install -r requirements.txt

### Clone the repository

```bash
git clone https://github.com/saanchi-sk/fema-disaster-map.git
cd fema-disaster-map
