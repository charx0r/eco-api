from contextlib import asynccontextmanager
from typing import AsyncGenerator

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from config import app_configs, settings
from models import EF
from auth.router import router as auth_router

sqlite_file_name = "../databases/efdatabase.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(**app_configs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/ef/")
def create_ef(ef: EF):
    with Session(engine) as session:
        session.add(ef)
        session.commit()
        session.refresh(ef)
        return ef


@app.get("/ef/")
def read_efs(offset: int = 0, limit: int = Query(default=10, le=10)):
    with Session(engine) as session:
        efs = session.exec(select(EF).offset(offset).limit(limit)).all()
        return efs
    
@app.get("/ef/{elemnt_id}")
def read_ef(elemnt_id: int):
    with Session(engine) as session:
        ef = session.exec(select(EF).where(EF.elemnt_id == elemnt_id)).first()
        if not ef:
            raise HTTPException(status_code=404, detail="EF not found")
        return ef
    
app.include_router(auth_router, prefix="/auth", tags=["Auth"])