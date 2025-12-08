import os
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.core.state import running_system
from app.models.infrastructure import Habitat, HabitatDimensions
from app.models.dinosaur import Dinosaur, DinoCategory

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# == Request Models ==
class CreateHabitatRequest(BaseModel):
    name: str
    temp: float
    width: float
    length: float
    height: float

class CreateDinoRequest(BaseModel):
    name: str
    species: str
    category: DinoCategory
    heart_rate: int
    habitat_id: str


# == ENDPOINTS API ==

# Returns the current list of habitats and their dinos
@router.get("/api/habitats")
async def get_habitats():
    if not running_system["park"]:
        return []
    return running_system["park"].habitats

# Returns real-time statistics from the StreamManager
@router.get("/api/metrics")
async def get_metrics():
    manager = running_system["manager"]
    if not manager:
        return {}
    return manager.get_system_metrics()

# Read the last 50 lines of the log file
@router.get("/api/logs")
async def get_logs():
    log_path = "logs/jurassic_system.log"
    
    if not os.path.exists(log_path):
        return {"logs": ["Waiting for system logs..."]}
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return {"logs": [line.strip() for line in lines[-50:]]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}


# Create a new habitat in the park
@router.post("/api/habitats")
async def create_habitat(payload: CreateHabitatRequest):
    if not running_system["park"]:
        raise HTTPException(status_code=503, detail="System not ready")

    new_habitat = Habitat(
        name=payload.name,
        mean_temperature=payload.temp,
        size=HabitatDimensions(
            x=payload.width, 
            y=payload.length, 
            z=payload.height
        )
    )
    
    running_system["park"].add_habitat(new_habitat)
    return {"status": "created", "habitat": new_habitat}

# Remove a habitat by its ID
@router.delete("/api/habitats/{habitat_id}")
async def delete_habitat(habitat_id: str):
    try:
        habitat_uuid = UUID(habitat_id)
        running_system["park"].remove_habitat(habitat_uuid)
        return {"status": "deleted"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID")

# Create a new dinosaur and assigns it to a habitat
@router.post("/api/dinosaurs")
async def create_dinosaur(payload: CreateDinoRequest):
    
    new_dino = Dinosaur(
        name=payload.name,
        species=payload.species,
        category=payload.category,
        heart_rate=payload.heart_rate,
        health_points=100
    )
    
    habitats = running_system["park"].habitats
    target_habitat = next((h for h in habitats if str(h.id) == payload.habitat_id), None)
    
    if not target_habitat:
        raise HTTPException(status_code=404, detail="Habitat not found")
    
    target_habitat.dinosaur_ids.append(new_dino.id)
    
    if running_system["simulator"]:
        running_system["simulator"].add_dinosaur(new_dino)
        
    if running_system["manager"]:
        running_system["manager"].register_dinosaur(new_dino)
        
    return {"status": "created", "dino": new_dino}

# Remove a dinosaur from the entire system
@router.delete("/api/dinosaurs/{dino_id}")
async def delete_dinosaur(dino_id: str):
    
    if running_system["simulator"]:
        running_system["simulator"].remove_dinosaur(dino_id)
    if running_system["manager"]:
        running_system["manager"].unregister_dinosaur(dino_id)
        
    try:
        d_uuid = UUID(dino_id)
        for habitat in running_system["park"].habitats:
            if d_uuid in habitat.dinosaur_ids:
                habitat.dinosaur_ids.remove(d_uuid)
                break
    except ValueError:
        pass
            
    return {"status": "deleted"}

# == ENDPOINTS VIEWS ==

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/habitat/{habitat_id}", response_class=HTMLResponse)
async def read_habitat(request: Request, habitat_id: str):
    if not running_system["park"]:
        raise HTTPException(status_code=503, detail="System initializing")

    habitats = running_system["park"].habitats
    target = next((h for h in habitats if str(h.id) == habitat_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Habitat not found")
        
    return templates.TemplateResponse("habitat_detail.html", {
        "request": request, 
        "habitat": target
    })

@router.get("/metrics-view", response_class=HTMLResponse)
async def read_metrics_page(request: Request):
    return templates.TemplateResponse("metrics.html", {"request": request})