from uuid import UUID, uuid4
from typing import List, Literal
from pydantic import BaseModel, Field

# == HABITATS MODEL ==

class HabitatDimensions(BaseModel):
    
    x: float = Field(..., description="Width (meters)")
    y: float = Field(..., description="Length (meters)")
    z: float = Field(..., description="Height (meters)")

class Habitat(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique Habitat ID")
    name: str = Field(..., description="Habitat name")    
    size: HabitatDimensions = Field(..., description="3D dimensions of the habitat")
    
    mean_temperature: float = Field(..., description="Target average temperature for this habitat")
    
    dinosaur_ids: List[UUID] = Field(default_factory=list, description="List of Dinosaurs currently in this habitat")

# == PARCK MODEL ==

class Park(BaseModel):
    name: str = Field(default="Jurassic Park")
    
    habitats: List[Habitat] = Field(default_factory=list, description="All habitats in the park")

    def add_habitat(self, habitat: Habitat):
        self.habitats.append(habitat)
    
    def remove_habitat(self, habitat_id: UUID):
        self.habitats = [h for h in self.habitats if h.id != habitat_id]