import type {VehicleState} from '../types';
const API=import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
export async function getJson<T>(path:string):Promise<T>{const r=await fetch(`${API}${path}`); if(!r.ok) throw new Error(await r.text()); return r.json();}
export const fetchRoutes=()=>getJson<GeoJSON.FeatureCollection>('/routes.geojson');
export const fetchStops=()=>getJson<GeoJSON.FeatureCollection>('/stops.geojson');
export const fetchVehicles=(date:string,time:string,modes:string[])=>getJson<VehicleState[]>(`/vehicles?service_date=${date}&time=${time}&modes=${modes.join(',')}`);
