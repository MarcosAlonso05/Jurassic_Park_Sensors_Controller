import sys
import os
import reactivex as rx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logging_config import setup_logging
from app.core.state import running_system
from app.services.stream_manager import JurassicStreamManager
from app.services.simulator import SensorSimulator
from app.api.routes import router

from app.models.infrastructure import Park, Habitat, HabitatDimensions
from app.models.dinosaur import Dinosaur, DinoCategory

setup_logging()

# == INITIAL SETUP ==

def setup_infrastructure():
    rex = Dinosaur(
        name="Rexy", species="T-Rex", category=DinoCategory.TERRESTRIAL, 
        health_points=100, heart_rate=60
    )
    blue = Dinosaur(
        name="Blue", species="Velociraptor", category=DinoCategory.TERRESTRIAL, 
        health_points=95, heart_rate=110
    )
    mosa = Dinosaur(
        name="The Queen", species="Mosasaurus", category=DinoCategory.AQUATIC, 
        health_points=100, heart_rate=35
    )
    
    paddock_rex = Habitat(
        name="T-Rex Paddock", 
        size=HabitatDimensions(x=800, y=800, z=25), 
        mean_temperature=28.0, 
        dinosaur_ids=[rex.id]
    )
    
    raptor_pen = Habitat(
        name="Raptor Pen", 
        size=HabitatDimensions(x=100, y=100, z=15), 
        mean_temperature=26.0, 
        dinosaur_ids=[blue.id]
    )
    
    lagoon = Habitat(
        name="Lagoon", 
        size=HabitatDimensions(x=1500, y=1000, z=80), 
        mean_temperature=20.0, 
        dinosaur_ids=[mosa.id]
    )

    park = Park(name="Jurassic Park - Isla Nublar")
    park.add_habitat(paddock_rex)
    park.add_habitat(raptor_pen)
    park.add_habitat(lagoon)
    
    return park, [rex, blue, mosa]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> SYSTEM BOOT: INITIATING JURASSIC PARK PROTOCOLS...")
    
    park, dinos = setup_infrastructure()
    
    running_system["park"] = park
    
    manager = JurassicStreamManager(park, dinos)
    manager.initialize()
    running_system["manager"] = manager
    
    simulator = SensorSimulator(park, dinos)
    running_system["simulator"] = simulator
    
    sensor_stream = rx.merge(
        simulator.create_temperature_stream(2.0),
        simulator.create_motion_stream(3.0),
        simulator.create_heart_rate_stream(1.0)
    )
    
    sub = sensor_stream.subscribe(
        on_next=lambda x: manager.on_sensor_data(x),
        on_error=lambda e: print(f"CRITICAL STREAM ERROR: {e}")
    )
    
    print(">>> SYSTEM ONLINE: SENSORS ACTIVE.")
    
    yield
    
    print(">>> SYSTEM SHUTDOWN.")
    sub.dispose()

app = FastAPI(
    title="Jurassic Park Reactive System",
    description="Real-time sensor monitoring using RxPY and FastAPI",
    version="2.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(router)

# == ENTRY POINT ==
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)