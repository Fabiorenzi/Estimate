from pydantic import BaseModel

class Stop(BaseModel):
    stop_id: str; stop_name: str; stop_lat: float; stop_lon: float; routes: list[str] = []
class Route(BaseModel):
    route_id: str; route_short_name: str|None=None; route_long_name: str|None=None; route_type: int; route_color: str|None=None
class VehicleState(BaseModel):
    vehicle_id: str; route_id: str; trip_id: str; mode: str; lat: float; lon: float; heading: float; speed_mps: float; next_stop_id: str|None; next_stop_name: str|None; progress: float; distance_m: float
class SimulationRequest(BaseModel):
    service_date: str; time: str; speed: float = 1.0; modes: list[str] = ["metro", "tram"]
