from __future__ import annotations
import json, logging, math, zipfile
from pathlib import Path
import pandas as pd
import requests
from shapely.geometry import LineString, mapping

log=logging.getLogger(__name__)
REQUIRED=["agency.txt","stops.txt","routes.txt","trips.txt","stop_times.txt","shapes.txt","calendar.txt","calendar_dates.txt"]
METRO_TYPES={1}; TRAM_TYPES={0}

def download_gtfs(url:str, dest:Path)->Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r=requests.get(url, timeout=60); r.raise_for_status(); dest.write_bytes(r.content); return dest

def read_gtfs(zip_path:Path)->dict[str,pd.DataFrame]:
    with zipfile.ZipFile(zip_path) as z:
        names=set(z.namelist()); missing=[f for f in REQUIRED if f not in names]
        if missing: raise ValueError(f"Missing GTFS files: {missing}")
        return {f[:-4]: pd.read_csv(z.open(f), dtype=str, keep_default_na=False) for f in REQUIRED}

def validate(feed:dict[str,pd.DataFrame])->list[str]:
    issues=[]; stops=feed['stops']; routes=feed['routes']; trips=feed['trips']; st=feed['stop_times']
    for tbl, col in [('stops','stop_id'),('routes','route_id'),('trips','trip_id')]:
        d=feed[tbl][col][feed[tbl][col].duplicated()].unique().tolist()
        if d: issues.append(f"duplicate {tbl}.{col}: {d[:10]}")
    lat=pd.to_numeric(stops.stop_lat, errors='coerce'); lon=pd.to_numeric(stops.stop_lon, errors='coerce')
    bad=stops[lat.isna()|lon.isna()|~lat.between(-90,90)|~lon.between(-180,180)]
    if len(bad): issues.append(f"invalid stop coordinates: {len(bad)}")
    missing_stops=set(st.stop_id)-set(stops.stop_id)
    if missing_stops: issues.append(f"stop_times reference missing stops: {len(missing_stops)}")
    missing_routes=set(trips.route_id)-set(routes.route_id)
    if missing_routes: issues.append(f"trips reference missing routes: {len(missing_routes)}")
    if 'shape_id' in trips and len(feed['shapes']):
        miss=set(trips.loc[trips.shape_id!='','shape_id'])-set(feed['shapes'].shape_id)
        if miss: issues.append(f"trips reference missing shapes: {len(miss)}")
    return issues

def filter_modes(feed):
    routes=feed['routes'].copy(); routes['route_type_i']=pd.to_numeric(routes.route_type, errors='coerce').fillna(-1).astype(int)
    keep=routes[routes.route_type_i.isin(METRO_TYPES|TRAM_TYPES)]
    trips=feed['trips'][feed['trips'].route_id.isin(keep.route_id)]
    stop_times=feed['stop_times'][feed['stop_times'].trip_id.isin(trips.trip_id)]
    stops=feed['stops'][feed['stops'].stop_id.isin(stop_times.stop_id)]
    shapes=feed['shapes'][feed['shapes'].shape_id.isin(trips.shape_id)] if 'shape_id' in trips else feed['shapes'].iloc[0:0]
    out=feed.copy(); out.update(routes=keep.drop(columns=['route_type_i']), trips=trips, stop_times=stop_times, stops=stops, shapes=shapes); return out

def _features(feed):
    routes=feed['routes']; trips=feed['trips']; shapes=feed['shapes'].copy(); feats=[]
    if len(shapes):
        shapes['shape_pt_sequence']=pd.to_numeric(shapes.shape_pt_sequence, errors='coerce')
        for sid,g in shapes.sort_values('shape_pt_sequence').groupby('shape_id'):
            coords=[(float(r.shape_pt_lon),float(r.shape_pt_lat)) for _,r in g.iterrows()]
            if len(coords)>1:
                rids=trips[trips.shape_id==sid].route_id.unique().tolist(); route=routes[routes.route_id.isin(rids)].head(1)
                props={'shape_id':sid,'route_ids':rids,'mode':'metro' if (len(route) and str(route.iloc[0].route_type)=='1') else 'tram'}
                feats.append({'type':'Feature','geometry':mapping(LineString(coords)),'properties':props})
    return feats

def export_processed(feed, out:Path):
    out.mkdir(parents=True, exist_ok=True)
    for k,v in feed.items(): v.to_json(out/f'{k}.json', orient='records')
    (out/'routes.geojson').write_text(json.dumps({'type':'FeatureCollection','features':_features(feed)}))
    stop_routes=feed['stop_times'].merge(feed['trips'][['trip_id','route_id']], on='trip_id').groupby('stop_id').route_id.apply(lambda s: sorted(set(s))).to_dict()
    feats=[]
    for _,s in feed['stops'].iterrows():
        feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':[float(s.stop_lon),float(s.stop_lat)]},'properties':{'stop_id':s.stop_id,'stop_name':s.stop_name,'routes':stop_routes.get(s.stop_id,[])}})
    (out/'stops.geojson').write_text(json.dumps({'type':'FeatureCollection','features':feats}))
    return out
