import asyncio
import sys
import os
import logging
from contextlib import asynccontextmanager
import reactivex as rx
from reactivex import operators as ops
from fastapi import FastAPI

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.infrastructure import Park, Habitat, HabitatDimensions
from app.models.dinosaur import Dinosaur, DinoCategory
from app.services.stream_manager import JurassicStreamManager
from app.services.simulator import SensorSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainController")

def setup_infrastructure():
    """
    Crea los datos base del parque: Dinos y Hábitats.
    """
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
    
    lagoon = Habitat(
        name="Lagoon", 
        size=HabitatDimensions(x=1500, y=1000, z=80), 
        mean_temperature=20.0, 
        dinosaur_ids=[mosa.id]
    )

    park = Park(name="Jurassic Park - Isla Nublar")
    park.add_habitat(paddock_rex)
    park.add_habitat(lagoon)
    
    return park, [rex, blue, mosa]

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(">>> BOOTING JURASSIC PARK SYSTEMS...")
    
    park, dinos = setup_infrastructure()
    
    stream_manager = JurassicStreamManager(park, dinos)
    stream_manager.initialize()
    
    simulator = SensorSimulator(park, dinos)
    
    logger.info(">>> CONNECTING SENSORS...")
    sensor_stream = rx.merge(
        simulator.create_temperature_stream(interval_sec=2.0), # Temp cada 2s
        simulator.create_motion_stream(interval_sec=3.0),      # Movimiento cada 3s
        simulator.create_heart_rate_stream(interval_sec=1.0)   # Corazón cada 1s
    )
    
    subscription = sensor_stream.subscribe(
        on_next=lambda data: stream_manager.on_sensor_data(data),
        on_error=lambda e: logger.error(f"Sensor Failure: {e}")
    )
    
    logger.info(">>> SYSTEM ONLINE. LISTENING TO SENSORS.")
    
    yield # Aquí es donde la aplicación se queda corriendo y escuchando peticiones
    
    logger.info(">>> SHUTTING DOWN SYSTEMS...")
    subscription.dispose() # Cortamos el flujo de datos limpiamente

app = FastAPI(
    title="Jurassic Park Reactive Monitor",
    description="System to monitor concurrent sensor data using RxPY",
    version="1.0.0",
    lifespan=lifespan # Vinculamos el ciclo de vida aquí
)

@app.get("/")
async def health_check():
    """Endpoint simple para verificar que el servidor vive."""
    return {
        "system": "Jurassic Park Monitor", 
        "status": "operational", 
        "location": "Isla Nublar"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)