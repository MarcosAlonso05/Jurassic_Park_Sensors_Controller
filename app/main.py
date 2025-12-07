import sys
import os
from uuid import uuid4

# --- FIX DE IMPORTACIONES ---
# Esto permite ejecutar el archivo directamente con "python app/main.py"
# sin que te de el error "ModuleNotFoundError".
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.infrastructure import Park, Habitat, HabitatDimensions
from app.models.dinosaur import Dinosaur, DinoCategory
from app.models.sensors import TemperatureSensor, MotionSensor, HeartRateSensor
from app.services.evaluator import RuleEvaluator

def print_separator(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def initialize_park() -> Park:
    """
    Creates the default infrastructure: Dinos, Habitats and the Park itself.
    """
    print_separator("STEP 1: INITIALIZING JURASSIC PARK INFRASTRUCTURE")

    # 1. Create Dinosaurs
    rex = Dinosaur(
        name="Rexy",
        species="Tyrannosaurus Rex",
        category=DinoCategory.TERRESTRIAL,
        health_points=100,
        heart_rate=60
    )
    
    blue = Dinosaur(
        name="Blue",
        species="Velociraptor",
        category=DinoCategory.TERRESTRIAL,
        health_points=95,
        heart_rate=110
    )

    mosa = Dinosaur(
        name="The Queen",
        species="Mosasaurus",
        category=DinoCategory.AQUATIC,
        health_points=100,
        heart_rate=35
    )

    print(f"[OK] Dinosaurs cloned: {rex.name}, {blue.name}, {mosa.name}")

    # 2. Create Habitats
    # T-Rex Paddock (Large, 25m high fence)
    paddock_rex = Habitat(
        name="T-Rex Paddock",
        size=HabitatDimensions(x=800, y=800, z=25), 
        mean_temperature=28.0,
        dinosaur_ids=[rex.id]
    )

    # Raptor Pen (Small, 15m high fence)
    raptor_pen = Habitat(
        name="Raptor Containment Unit",
        size=HabitatDimensions(x=100, y=100, z=15),
        mean_temperature=26.0,
        dinosaur_ids=[blue.id]
    )

    # Lagoon (Deep water, 80m depth)
    lagoon = Habitat(
        name="Jurassic World Lagoon",
        size=HabitatDimensions(x=1500, y=1000, z=80),
        mean_temperature=20.0,
        dinosaur_ids=[mosa.id]
    )

    print(f"[OK] Habitats constructed: {paddock_rex.name}, {raptor_pen.name}, {lagoon.name}")

    # 3. Create Park
    park = Park(name="Jurassic Park - Isla Nublar")
    park.add_habitat(paddock_rex)
    park.add_habitat(raptor_pen)
    park.add_habitat(lagoon)

    return park, rex, blue, mosa # Returning objects for simulation testing

def run_simulation():
    """
    Simulates sensor readings coming in and checks for alerts.
    """
    # Load Infrastructure
    park, rex, blue, mosa = initialize_park()
    
    # Let's pick the T-Rex Paddock for testing
    paddock = park.habitats[0] 

    print_separator(f"STEP 2: STARTING SENSOR SIMULATION ON '{paddock.name}'")
    print(f"Context: Max Height (Z) = {paddock.size.z}m | Target Temp = {paddock.mean_temperature}C")

    # --- SCENARIO 1: Temperature Normal ---
    print("\n>>> Scenario 1: Normal Morning")
    sensor_temp = TemperatureSensor(
        id="temp-001", habitat_id=paddock.id, sensor_type="temperature",
        value=27.5, unit="celsius" # Close to 28.0
    )
    alert = RuleEvaluator.evaluate_temperature(sensor_temp, paddock)
    if alert:
        print(f"[ALARM] {alert.severity}: {alert.message}")
    else:
        print(f"[INFO] Status Green. Temp: {sensor_temp.value}C")

    # --- SCENARIO 2: Heatwave (Warning) ---
    print("\n>>> Scenario 2: Ventilation Failure (Heatwave)")
    sensor_temp_hot = TemperatureSensor(
        id="temp-001", habitat_id=paddock.id, sensor_type="temperature",
        value=38.0, unit="celsius" # Way above 28.0 (+10)
    )
    alert = RuleEvaluator.evaluate_temperature(sensor_temp_hot, paddock)
    if alert:
        print(f" [ALARM!] SEVERITY: {alert.severity.upper()}")
        print(f"          MSG: {alert.message}")

    # --- SCENARIO 3: Motion Breach (Critical) ---
    print("\n>>> Scenario 3: T-Rex Climbing Fence")
    # Coordinates: x=50, y=50, z=26 (Fence is 25m high!)
    sensor_motion = MotionSensor(
        id="motion-055", habitat_id=paddock.id, sensor_type="motion",
        is_detected=True, sensitivity=10, coordinates="50,50,26" 
    )
    alert = RuleEvaluator.evaluate_motion(sensor_motion, paddock)
    if alert:
        print(f" [ALARM!] SEVERITY: {alert.severity.upper()}")
        print(f"          MSG: {alert.message}")

    # --- SCENARIO 4: Heart Rate Stress (Raptor) ---
    print("\n>>> Scenario 4: Blue is Panicking")
    # Blue's baseline is 110. Reading is 180 (Stress).
    sensor_heart = HeartRateSensor(
        id="bio-blue", habitat_id=paddock.id, sensor_type="heart_rate",
        dinosaur_id=str(blue.id), bpm=180, stress_level="High"
    )
    # Note: We need to pass the Dino object, not the Habitat
    alert = RuleEvaluator.evaluate_heart_rate(sensor_heart, blue) 
    if alert:
        print(f" [ALARM!] SEVERITY: {alert.severity.upper()}")
        print(f"          MSG: {alert.message}")

if __name__ == "__main__":
    run_simulation()