# Rome Metro & Tram 3D Digital Twin MVP

A production-oriented MVP for a reusable transport digital twin platform. It ingests Rome GTFS static data, validates and filters Metro (`route_type=1`) and Tram (`route_type=0`) service, exposes FastAPI endpoints, and visualizes scheduled vehicle movement in a CesiumJS 3D dashboard.

## Official Rome GTFS source
Roma Servizi per la Mobilità documents GTFS open data on its Open Data/AVM page. The API default points at `https://romamobilita.it/sites/default/files/rome_static_gtfs.zip`. If the publisher changes the URL, set `GTFS_URL` or place a compatible GTFS zip at `data/raw/rome_gtfs.zip`.

## Run locally
```bash
docker compose up --build
curl -X POST http://localhost:8000/api/ingest/download
open http://localhost:5173
```
If download is unavailable, copy the official GTFS zip to `data/raw/rome_gtfs.zip` and run:
```bash
curl -X POST http://localhost:8000/api/ingest/process
```

## API
- `GET /api/health`
- `POST /api/ingest/download`
- `POST /api/ingest/process`
- `GET /api/routes.geojson`
- `GET /api/stops.geojson`
- `GET /api/validation`
- `GET /api/vehicles?service_date=2026-07-02&time=08:00:00&modes=metro,tram`

## What works
- GTFS parsing for required static files.
- Validation for missing references, invalid coordinates and duplicate IDs.
- Metro/tram filtering and GeoJSON/JSON export.
- Rendering routes/stops in Cesium, with metro below ground and tram at surface.
- Independent Python simulation engine producing vehicle states from schedules.
- Dashboard controls, layer toggles, speed/date/time controls and inspectors.

## Limitations
- Vehicle interpolation currently uses stop-to-stop straight-line interpolation; shape-distance interpolation is a next step.
- SQLite/PostGIS persistence boundary is configured but MVP primarily reads processed files in memory.
- GTFS-RT is intentionally not implemented, but API and engine boundaries leave room for it.
