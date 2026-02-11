from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.utils.config import load_config
from src.utils.logging import configure_logging, request_logger_middleware, json_log

config = load_config()

app = FastAPI(title="LAN Monitor Dashboard", version=config.version)

# Configure logging and middleware
configure_logging()
app.middleware("http")(request_logger_middleware)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "version": config.version})


if __name__ == "__main__":
    # Enable running via: python -m src.main
    import uvicorn

    json_log(level="INFO", msg="startup", bind_host=config.bind_host, port=config.port, version=config.version)
    uvicorn.run("src.main:app", host=config.bind_host, port=config.port, reload=False)