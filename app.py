from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import database
from routes.login import router as login_router
from routes.main import router as main_router
from routes.register import router as register_router
import os

app = FastAPI()

# Création des tables
database.Base.metadata.create_all(bind=database.engine)

# Inclusion des routes
app.include_router(login_router)
app.include_router(main_router)
app.include_router(register_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    os.system("uvicorn app:app --reload --port 15000")
    