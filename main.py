from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import create_tables
from routes.redirects import router as redirects_router
from routes.urls import router as urls_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield
    

app = FastAPI(title = "URL Shortner Service", 
    summary= "Service to convert your long urls into short unique urls.",
    docs_url= "/docs", 
    openapi_url= "/openapi",
    lifespan=lifespan)

app.include_router(router=urls_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }

app.include_router(router=redirects_router)

