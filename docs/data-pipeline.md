# Data pipeline

1. Download or load an official Roma Mobilità GTFS zip.
2. Parse `agency`, `stops`, `routes`, `trips`, `stop_times`, `shapes`, `calendar`, and `calendar_dates`.
3. Validate duplicate IDs, invalid coordinates, missing stops, missing routes and missing shapes.
4. Filter GTFS route types: tram `0`, metro `1`.
5. Export source tables as JSON plus route and stop GeoJSON.
