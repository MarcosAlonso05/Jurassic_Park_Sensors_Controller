from datetime import datetime
from typing import Literal, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class SensorBase(BaseModel):
    
    id: str = Field(..., description="ID of the device")
    habitat_id: UUID = Field(..., description="ID of the habitat")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    battery_level: float = Field(default=100.0, ge=0, le=100)


# == Sensors ==

class MotionSensor(SensorBase):
    
    sensor_type: Literal["motion"] 
    
    sensitivity: int = Field(default=5, ge=1, le=10)
    coordinates: Optional[str] = Field(None, description="Grid coordinates e.g., 'A1-North'")
    
    is_detected: bool = Field(..., description="True if motion is detected")

class TemperatureSensor(SensorBase):
    
    sensor_type: Literal["temperature"]
    
    unit: Literal["celsius", "fahrenheit"] = Field(default="celsius")
    humidity: Optional[float] = Field(None, description="Optional humidity reading")
    
    value: float = Field(..., description="Temperature value")

class HeartRateSensor(SensorBase):
    
    sensor_type: Literal["heart_rate"]
    
    dinosaur_id: str = Field(..., description="ID of the animal being monitored")
    
    bpm: int = Field(..., gt=0, description="Beats per minute")
    stress_level: Optional[str] = Field(None, description="Low, Medium, High")

# --- Union Type ---
SensorEvent = Union[MotionSensor, TemperatureSensor, HeartRateSensor]