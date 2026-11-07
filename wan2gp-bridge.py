
import argparse
import secrets
import threading
import uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True, help="Carpeta donde está instalado Wan2GP")
args = parser.parse_args()

WAN_ROOT = Path(args.root).resolve()

if not (WAN_ROOT / "shared" / "api.py").is_file():
    raise SystemExit("No encuentro shared/api.py en la carpeta indicada.")

import sys
sys.path.insert(0, str(WAN_ROOT))

from shared.api import init

print("Iniciando conexión con Wan2GP...")
session = init(root=WAN_ROOT)

TOKEN = secrets.token_urlsafe(32)
jobs = {}

app = FastAPI(title="Gangry Fusion AI - Wan2GP Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://raymergarcias56-del.github.io"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def authorize(authorization):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Token incorrecto")


@app.get("/health")
def health():
    return {"connected": True, "engine": "Wan2GP"}


@app.get("/models")
def models(authorization: str = Header(default="")):
    authorize(authorization)
    return session.list_model_metadata(
        main_output="video",
        limit=100,
        include_availability=True
    )


@app.post("/generate")
def generate(data: dict, authorization: str = Header(default="")):
    authorize(authorization)

    model_type = str(data.get("model_type", "")).strip()
    prompt = str(data.get("prompt", "")).strip()

    if not model_type or not prompt:
        raise HTTPException(400, "Falta el modelo o el prompt.")

    if len(prompt) > 12000:
        raise HTTPException(400, "El prompt es demasiado largo.")

    try:
        settings = session.get_default_settings(model_type)
    except Exception as error:
        raise HTTPException(400, f"Modelo no válido: {error}")

    settings["prompt"] = prompt

    allowed = (
        "resolution",
        "duration_seconds",
        "video_length",
        "force_fps",
        "num_inference_steps",
    )

    for key in allowed:
        if key in data:
            settings[key] = data[key]

    job_id = str(uuid.uuid4())

    try:
        task = session.submit_task(settings)
    except Exception as error:
        raise HTTPException(500, f"No se pudo iniciar: {error}")

    jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Generación iniciada",
        "files": [],
        "error": None,
    }

    def monitor():
        try:
            for event in task.events.iter(timeout=0.2):
                if event.kind == "progress":
                    progress = event.data
                    jobs[job_id]["progress"] = getattr(
                        progress, "progress", 0
                    )
                    jobs[job_id]["message"] = getattr(
                        progress, "phase", "Generando vídeo"
                    )

            result = task.result()

            if result.success:
                jobs[job_id]["status"] = "completed"
                jobs[job_id]["files"] = [
                    str(path) for path in result.generated_files
                ]
                jobs[job_id]["progress"] = 100
                jobs[job_id]["message"] = "Vídeo terminado"
            else:
                jobs[job_id]["status"] = "failed"
                jobs[job_id]["error"] = "; ".join(
                    error.message for error in result.errors
                )

        except Exception as error:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = str(error)

    threading.Thread(target=monitor, daemon=True).start()

    return {"job_id": job_id, "status": "processing"}


@app.get("/jobs/{job_id}")
def job_status(job_id: str, authorization: str = Header(default="")):
    authorize(authorization)

    if job_id not in jobs:
        raise HTTPException(404, "Trabajo no encontrado.")

    job = jobs[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "error": job["error"],
        "files": len(job["files"]),
    }


@app.get("/jobs/{job_id}/file/{index}")
def download(job_id: str, index: int, authorization: str = Header(default="")):
    authorize(authorization)

    if job_id not in jobs:
        raise HTTPException(404, "Trabajo no encontrado.")

    files = jobs[job_id]["files"]

    if index < 0 or index >= len(files):
        raise HTTPException(404, "Vídeo no encontrado.")

    path = Path(files[index]).resolve()

    if not path.is_file() or path.suffix.lower() not in (
        ".mp4", ".webm", ".mov"
    ):
        raise HTTPException(404, "Archivo no disponible.")

    return FileResponse(path, filename=path.name)


if __name__ == "__main__":
    print("\nGANGRY FUSION AI - WAN2GP")
    print("Dirección: http://127.0.0.1:7866")
    print("Token de conexión (no lo compartas):")
    print(TOKEN)
    print("\nMantén esta ventana abierta mientras utilizas el conector.\n")

    uvicorn.run(app, host="127.0.0.1", port=7866)

