# Architecture

The platform is split into ingestion (`backend/app/data`), API (`backend/app/api`), simulation (`backend/app/simulation`), schemas (`backend/app/models`), React UI (`frontend/src`) and Cesium rendering. The simulation engine has no Cesium dependency and returns serializable vehicle state DTOs. Processed artifacts are stored under `data/processed`; this keeps the MVP simple while preserving a clean boundary for SQLite/PostGIS repositories.
