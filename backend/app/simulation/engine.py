from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import math
import pandas as pd
from app.models.schemas import VehicleState

def parse_time(t:str)->int:
    h,m,s=[int(x) for x in t.split(':')]; return h*3600+m*60+s

def bearing(a,b):
    lat1,lon1,lat2,lon2=map(math.radians,[a[0],a[1],b[0],b[1]])
    y=math.sin(lon2-lon1)*math.cos(lat2); x=math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(lon2-lon1)
    return (math.degrees(math.atan2(y,x))+360)%360

def hav(a,b):
    R=6371000; la1,lo1,la2,lo2=map(math.radians,[a[0],a[1],b[0],b[1]])
    dlat=la2-la1; dlon=lo2-lo1
    q=math.sin(dlat/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(q))

def interp(a,b,f): return (a[0]+(b[0]-a[0])*f, a[1]+(b[1]-a[1])*f)

@dataclass
class SimulationEngine:
    feed: dict[str,pd.DataFrame]
    def active_service_ids(self, d:date):
        cal=self.feed['calendar']; ids=set()
        if len(cal):
            wd=d.strftime('%A').lower(); ymd=int(d.strftime('%Y%m%d'))
            for _,r in cal.iterrows():
                if int(r.start_date)<=ymd<=int(r.end_date) and str(r.get(wd,'0'))=='1': ids.add(r.service_id)
        cd=self.feed['calendar_dates']
        if len(cd):
            for _,r in cd[cd.date==d.strftime('%Y%m%d')].iterrows():
                (ids.add if str(r.exception_type)=='1' else ids.discard)(r.service_id)
        return ids
    def vehicles_at(self, service_date:str, time_str:str, modes:list[str]):
        t=parse_time(time_str); d=date.fromisoformat(service_date); services=self.active_service_ids(d)
        routes=self.feed['routes'].copy(); routes['mode']=routes.route_type.map(lambda x:'metro' if str(x)=='1' else 'tram' if str(x)=='0' else 'other')
        route_modes=routes[routes['mode'].isin(modes)][['route_id','mode']]
        trips=self.feed['trips'][self.feed['trips'].service_id.isin(services)].merge(route_modes,on='route_id')
        st=self.feed['stop_times'][self.feed['stop_times'].trip_id.isin(trips.trip_id)].copy()
        if st.empty: return []
        st['arr']=st.arrival_time.map(parse_time); st['dep']=st.departure_time.map(parse_time); st['seq']=pd.to_numeric(st.stop_sequence, errors='coerce')
        stops=self.feed['stops'].set_index('stop_id'); out=[]
        for trip_id,g in st.sort_values('seq').groupby('trip_id'):
            rows=list(g.itertuples())
            for a,b in zip(rows, rows[1:]):
                if a.dep<=t<=b.arr and a.stop_id in stops.index and b.stop_id in stops.index:
                    sa=stops.loc[a.stop_id]; sb=stops.loc[b.stop_id]; dur=max(1,b.arr-a.dep); f=(t-a.dep)/dur
                    p=interp((float(sa.stop_lat),float(sa.stop_lon)),(float(sb.stop_lat),float(sb.stop_lon)),f); dist=hav((float(sa.stop_lat),float(sa.stop_lon)),p)
                    tr=trips[trips.trip_id==trip_id].iloc[0]
                    out.append(VehicleState(vehicle_id=f"{trip_id}:{a.stop_sequence}",route_id=tr.route_id,trip_id=trip_id,mode=tr['mode'],lat=p[0],lon=p[1],heading=bearing((float(sa.stop_lat),float(sa.stop_lon)),(float(sb.stop_lat),float(sb.stop_lon))),speed_mps=hav((float(sa.stop_lat),float(sa.stop_lon)),(float(sb.stop_lat),float(sb.stop_lon)))/dur,next_stop_id=b.stop_id,next_stop_name=str(sb.stop_name),progress=f,distance_m=dist))
                    break
        return out
