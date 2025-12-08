from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.state import running_system
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ... (tus endpoints de habitats y metrics siguen igual) ...
@router.get("/api/habitats")
async def get_habitats():
    if not running_system["park"]: return []
    return running_system["park"].habitats

@router.get("/api/metrics")
async def get_metrics():
    manager = running_system["manager"]
    if not manager: return {}
    # Ahora esto funcionará porque actualizaste stream_manager.py
    return manager.get_system_metrics()

# ... CORRECCIÓN EN EL ENDPOINT DE LOGS ...
@router.get("/api/logs")
async def get_logs():
    log_path = "logs/jurassic_system.log"
    if not os.path.exists(log_path):
        return {"logs": ["Waiting for system logs..."]}
    
    try:
        # Usamos encoding utf-8 para evitar errores con emojis o tildes
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Devolvemos las últimas 50 líneas limpias
            return {"logs": [line.strip() for line in lines[-50:]]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}

# ... (Endpoints HTML siguen igual) ...
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/habitat/{habitat_id}", response_class=HTMLResponse)
async def read_habitat(request: Request, habitat_id: str):
    habitats = running_system["park"].habitats
    target = next((h for h in habitats if str(h.id) == habitat_id), None)
    if not target: raise HTTPException(status_code=404, detail="Habitat not found")
    return templates.TemplateResponse("habitat_detail.html", {"request": request, "habitat": target})

@router.get("/metrics-view", response_class=HTMLResponse)
async def read_metrics_page(request: Request):
    return templates.TemplateResponse("metrics.html", {"request": request})