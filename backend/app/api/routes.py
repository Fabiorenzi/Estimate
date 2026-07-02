import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.data.gtfs import read_gtfs, validate, filter_modes, export_processed, download_gtfs
from app.simulation.engine import SimulationEngine
router=APIRouter()
_cache={}
def load_feed():
    if 'feed' not in _cache:
        p=settings.raw_dir/'rome_gtfs.zip'
        if not p.exists(): raise HTTPException(404,'GTFS not loaded. POST /api/ingest/download or place zip in data/raw/rome_gtfs.zip')
        _cache['feed']=filter_modes(read_gtfs(p))
    return _cache['feed']
@router.get('/health')
def health(): return {'status':'ok'}
@router.post('/ingest/download')
def ingest_download():
    p=download_gtfs(settings.gtfs_url, settings.raw_dir/'rome_gtfs.zip'); feed=filter_modes(read_gtfs(p)); issues=validate(feed); export_processed(feed, settings.processed_dir); _cache['feed']=feed; return {'zip':str(p),'issues':issues}
@router.post('/ingest/process')
def ingest_process():
    feed=filter_modes(read_gtfs(settings.raw_dir/'rome_gtfs.zip')); issues=validate(feed); export_processed(feed, settings.processed_dir); _cache['feed']=feed; return {'issues':issues}
@router.get('/routes.geojson')
def routes_geojson(): return json.loads((settings.processed_dir/'routes.geojson').read_text())
@router.get('/stops.geojson')
def stops_geojson(): return json.loads((settings.processed_dir/'stops.geojson').read_text())
@router.get('/validation')
def validation(): return {'issues':validate(load_feed())}
@router.get('/vehicles')
def vehicles(service_date:str,time:str,modes:str='metro,tram'):
    return [v.model_dump() for v in SimulationEngine(load_feed()).vehicles_at(service_date,time,modes.split(','))]
