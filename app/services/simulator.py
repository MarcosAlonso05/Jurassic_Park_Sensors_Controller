import random
from uuid import uuid4
import reactivex as rx
from reactivex import operators as ops

from app.models.infrastructure import Park
from app.models.sensors import MotionSensor, TemperatureSensor, HeartRateSensor

class SensorSimulator:
    def __init__(self, park: Park, dinosaurs: list):
        self.park = park
        self.dinosaurs = dinosaurs

    def create_temperature_stream(self, interval_sec: float = 2.0):
        return rx.interval(interval_sec).pipe(
            ops.map(lambda _: self._generate_random_temp())
        )

    def create_motion_stream(self, interval_sec: float = 3.0):
        return rx.interval(interval_sec).pipe(
            ops.map(lambda _: self._generate_random_motion())
        )

    def create_heart_rate_stream(self, interval_sec: float = 1.0):
        return rx.interval(interval_sec).pipe(
            ops.map(lambda _: self._generate_random_bpm())
        )


    def _generate_random_temp(self) -> TemperatureSensor:
        habitat = random.choice(self.park.habitats)
        
        variation = random.uniform(-2, 2)
        if random.random() < 0.05: 
            variation = 15.0
            
        return TemperatureSensor(
            id=f"temp-{habitat.name[:3].replace(' ', '')}",
            habitat_id=habitat.id,
            sensor_type="temperature",
            value=round(habitat.mean_temperature + variation, 2),
            unit="celsius"
        )

    def _generate_random_motion(self) -> MotionSensor:
        habitat = random.choice(self.park.habitats)
        is_detected = random.choice([True, False])
        
        z = random.uniform(0, habitat.size.z + 5) 
        coords = f"{random.randint(0, 100)},{random.randint(0, 100)},{int(z)}"
        
        return MotionSensor(
            id=f"motion-{habitat.name[:3].replace(' ', '')}",
            habitat_id=habitat.id,
            sensor_type="motion",
            is_detected=is_detected,
            sensitivity=random.randint(1, 10),
            coordinates=coords if is_detected else None
        )

    def _generate_random_bpm(self) -> HeartRateSensor:
        dino = random.choice(self.dinosaurs)
        
        bpm = int(random.normalvariate(dino.heart_rate, 5))
        stress = "Low"
        
        if random.random() < 0.02:
            bpm = int(dino.heart_rate * 1.8)
            stress = "High"

        return HeartRateSensor(
            id=f"bio-{dino.name.replace(' ', '')}",
            habitat_id=uuid4(), 
            sensor_type="heart_rate",
            dinosaur_id=str(dino.id),
            bpm=bpm,
            stress_level=stress
        )
    
    def add_dinosaur(self, dino):
        self.dinosaurs.append(dino)

    def remove_dinosaur(self, dino_id):
        self.dinosaurs = [d for d in self.dinosaurs if str(d.id) != str(dino_id)]