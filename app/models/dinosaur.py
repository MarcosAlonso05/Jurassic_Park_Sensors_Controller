from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class DinoCategory(str, Enum):
    TERRESTRIAL = "terrestrial"
    AQUATIC = "aquatic"
    AERIAL = "aerial"

class Dinosaur(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique ID of the dinosaur")
    name: str = Field(..., min_length=2, description="Name")
    species: str = Field(..., description="Species")
    
    category: DinoCategory = Field(..., description="Habitat classification")
    
    health_points: int = Field(100, ge=0, le=100, description="HP: 0 (Dead) to 100 (Perfect)")
    
    heart_rate: int = Field(..., description="Baseline Heart Rate (BPM)")