import zipfile
from pathlib import Path
from app.data.gtfs import read_gtfs, validate, filter_modes, export_processed
from app.simulation.engine import SimulationEngine, parse_time

def make_zip(p:Path):
    files={
    'agency.txt':'agency_id,agency_name,agency_url,agency_timezone\na,ATAC,http://x,Europe/Rome\n',
    'routes.txt':'route_id,agency_id,route_short_name,route_long_name,route_type,route_color\nM,a,M,A,1,1976D2\nT,a,8,Tram 8,0,E53935\nB,a,64,Bus,3,888888\n',
    'trips.txt':'route_id,service_id,trip_id,shape_id\nM,W,M1,sm\nT,W,T1,st\nB,W,B1,sb\n',
    'stop_times.txt':'trip_id,arrival_time,departure_time,stop_id,stop_sequence\nM1,08:00:00,08:00:00,A,1\nM1,08:10:00,08:10:00,B,2\nT1,08:00:00,08:00:00,C,1\nT1,08:05:00,08:05:00,D,2\nB1,08:00:00,08:00:00,A,1\n',
    'stops.txt':'stop_id,stop_name,stop_lat,stop_lon\nA,Termini,41.901,12.501\nB,Colosseo,41.891,12.492\nC,Tram A,41.88,12.47\nD,Tram B,41.89,12.48\n',
    'shapes.txt':'shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\nsm,41.901,12.501,1\nsm,41.891,12.492,2\nst,41.88,12.47,1\nst,41.89,12.48,2\nsb,41,12,1\nsb,42,13,2\n',
    'calendar.txt':'service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\nW,1,1,1,1,1,1,1,20260101,20261231\n',
    'calendar_dates.txt':'service_id,date,exception_type\n'}
    with zipfile.ZipFile(p,'w') as z:
        for k,v in files.items(): z.writestr(k,v)

def test_parse_validate_filter_export_sim(tmp_path):
    zp=tmp_path/'gtfs.zip'; make_zip(zp); feed=read_gtfs(zp)
    assert validate(feed)==[]
    f=filter_modes(feed); assert set(f['routes'].route_id)=={'M','T'}
    export_processed(f,tmp_path/'out'); assert (tmp_path/'out/routes.geojson').exists()
    vs=SimulationEngine(f).vehicles_at('2026-07-02','08:02:30',['tram'])
    assert len(vs)==1 and vs[0].route_id=='T' and 0 < vs[0].progress < 1

def test_parse_time_over_24h(): assert parse_time('25:01:02')==90062
