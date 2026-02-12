from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
import os

from src.utils.config import load_config
from src.utils.logging import configure_logging, request_logger_middleware, json_log
from src.models.config_loader import load_systems_config
from src.monitor.scheduler import MonitorScheduler
from src.monitor.store import store, StatusStore
from src.models.entities import Status, FailureCategory

config = load_config()

app = FastAPI(title="LAN Monitor Dashboard", version=config.version)

# Configure logging and middleware
configure_logging()
app.middleware("http")(request_logger_middleware)

# Template engine
templates = Jinja2Templates(directory="src/templates")

# Static assets (CSS, etc.)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/images", StaticFiles(directory="src/images"), name="images")

# Load systems and start scheduler
SYSTEMS_CONFIG_PATH = os.getenv("SYSTEMS_CONFIG_PATH", "systems.json")
try:
    systems = load_systems_config(SYSTEMS_CONFIG_PATH)
except FileNotFoundError:
    json_log(level="WARNING", msg="systems.json not found, using empty list", path=SYSTEMS_CONFIG_PATH)
    systems = []

scheduler = MonitorScheduler(systems, interval=config.refresh_interval_seconds)

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.stop()

@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "version": config.version})

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    statuses = store.get_all_statuses()
    system_map = {s.id: s for s in systems}
    
    display_systems = []
    now = datetime.utcnow()
    
    for sys_id, sys in system_map.items():
        status = store.get_system_status(sys_id)
        is_stale = False
        if status and status.last_checked:
            delta = (now - status.last_checked).total_seconds()
            if delta > config.staleness_window_seconds:
                is_stale = True
        
        display_systems.append({
            "name": sys.name,
            "address": sys.address,
            "status": status or {
                "overall_status": Status.UNKNOWN,
                "check_results": [],
                "last_checked": None,
                "failure_category": FailureCategory.NONE
            },
            "is_stale": is_stale
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "systems": display_systems
    })

@app.get("/api/status")
async def get_status():
    return store.get_all_statuses()

@app.post("/api/refresh")
async def trigger_refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(scheduler.refresh_all)
    return JSONResponse({"status": "refresh triggered"}, status_code=202)


if __name__ == "__main__":
    # Enable running via: python -m src.main
    import uvicorn

    json_log(level="INFO", msg="startup", bind_host=config.bind_host, port=config.port, version=config.version)
    uvicorn.run("src.main:app", host=config.bind_host, port=config.port, reload=False)