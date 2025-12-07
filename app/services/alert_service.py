from abc import ABC, abstractmethod
from typing import Optional
from app.models.sensors import MotionSensor, TemperatureSensor, HeartRateSensor
from app.models.alert import Alert, AlertSeverity

class AlertStrategy(ABC):
    @abstractmethod
    def check_for_alert(self, reading) -> Optional[Alert]:
        pass