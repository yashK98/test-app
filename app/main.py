from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import cluster, repositories

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Drift Detector — Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # tighten before anything non-local
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repositories.router)
app.include_router(cluster.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
