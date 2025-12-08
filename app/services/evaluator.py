from typing import Optional, List
from app.models.sensors import SensorEvent, MotionSensor, TemperatureSensor, HeartRateSensor
from app.models.infrastructure import Habitat
from app.models.dinosaur import Dinosaur
from app.models.alert import Alert, AlertSeverity

class RuleEvaluator:

    @staticmethod
    def evaluate_temperature(reading: TemperatureSensor, habitat: Habitat) -> Optional[Alert]:
        val_c = reading.value
        if reading.unit == "fahrenheit":
            val_c = (reading.value - 32) * 5/9
        
        tolerance = 5.0
        target = habitat.mean_temperature
        
        if val_c > (target + tolerance):
            return Alert(
                sensor_id=reading.id,
                severity=AlertSeverity.MEDIUM,
                message=f"Overheating in {habitat.name}. Current: {val_c:.1f}C (Target: {target}C)",
                triggered_value=val_c
            )
        
        if val_c < (target - tolerance):
            return Alert(
                sensor_id=reading.id,
                severity=AlertSeverity.MEDIUM,
                message=f"Freezing in {habitat.name}. Current: {val_c:.1f}C (Target: {target}C)",
                triggered_value=val_c
            )
            
        return None

    @staticmethod
    def evaluate_motion(reading: MotionSensor, habitat: Habitat) -> Optional[Alert]:
        if not reading.is_detected:
            return None

        if reading.sensitivity >= 9:
            return Alert(
                sensor_id=reading.id,
                severity=AlertSeverity.HIGH,
                message=f"Violent motion detected in {habitat.name}!",
                triggered_value=reading.sensitivity
            )

        if reading.coordinates:
            try:
                coords = [float(c) for c in reading.coordinates.split(",")]
                if len(coords) == 3:
                    z_height = coords[2]
                    
                    if z_height > habitat.size.z:
                        return Alert(
                            sensor_id=reading.id,
                            severity=AlertSeverity.CRITICAL,
                            message=f"BREACH DETECTED: Object at height {z_height}m (Max: {habitat.size.z}m) in {habitat.name}",
                            triggered_value=reading.coordinates
                        )
            except ValueError:
                pass

        return None

    @staticmethod
    def evaluate_heart_rate(reading: HeartRateSensor, dino: Dinosaur) -> Optional[Alert]:
        baseline = dino.heart_rate
        current = reading.bpm

        if current > (baseline * 1.5):
            severity = AlertSeverity.HIGH
            
            if reading.stress_level == "High":
                severity = AlertSeverity.CRITICAL

            return Alert(
                sensor_id=reading.id,
                severity=severity,
                message=f"Dinosaur {dino.name} ({dino.species}) is stressed! BPM: {current} (Base: {baseline})",
                triggered_value=current
            )
            
        if current == 0:
            return Alert(
                sensor_id=reading.id,
                severity=AlertSeverity.CRITICAL,
                message=f"VITAL SIGNS LOST: {dino.name}",
                triggered_value=0
            )

        return None