from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.middleware.cors import CORSMiddleware

from freelance_website.config import api_settings
from freelance_website.routes import api, docs

origins = ["http://localhost", "http://localhost:3000"]

app: FastAPI = FastAPI(**api_settings.model_dump(exclude={"prefix": True}))

app.include_router(api.api_router, prefix=api_settings.prefix)
app.include_router(docs.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()
