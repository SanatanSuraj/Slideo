import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.lifespan import app_lifespan
from api.middlewares import UserConfigEnvUpdateMiddleware
from api.v1.ppt.router import API_V1_PPT_ROUTER
from api.v1.webhook.router import API_V1_WEBHOOK_ROUTER
from api.v1.mock.router import API_V1_MOCK_ROUTER
from api.v1.auth.router import router as auth_router
from api.v1.presentations.router import router as presentations_router
from api.v1.slides.router import router as slides_router
from api.v1.db_status import router as db_status_router
from api.v1.ppt.endpoints.pptx_storage import PPTX_STORAGE_ROUTER
from api.v1.presentation_final_edits.router import PRESENTATION_FINAL_EDIT_ROUTER
from api.v1.final_presentations.router import FINAL_PRESENTATION_ROUTER
from utils.asset_directory_utils import get_images_directory
from utils.get_env import get_app_data_directory_env

# Load environment variables from .env file
load_dotenv()


app = FastAPI(lifespan=app_lifespan)


# Routers
app.include_router(API_V1_PPT_ROUTER)
app.include_router(API_V1_WEBHOOK_ROUTER)
app.include_router(API_V1_MOCK_ROUTER)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(presentations_router, prefix="/api/v1")
app.include_router(slides_router, prefix="/api/v1")
app.include_router(db_status_router, prefix="/api/v1")
app.include_router(PPTX_STORAGE_ROUTER, prefix="/api/v1/ppt")
app.include_router(PRESENTATION_FINAL_EDIT_ROUTER, prefix="/api/v1/presentation_final_edits")
app.include_router(FINAL_PRESENTATION_ROUTER, prefix="/api/v1/final_presentations")

# Middlewares
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(UserConfigEnvUpdateMiddleware)

# Mount static files for app_data directory
app_data_dir = get_app_data_directory_env() or "./app_data"
# If relative path, resolve relative to project root (three levels up from fastapi dir)
if not os.path.isabs(app_data_dir):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))

# Ensure the directory exists
os.makedirs(app_data_dir, exist_ok=True)

# Mount the app_data directory to serve static files
app.mount("/app_data", StaticFiles(directory=app_data_dir), name="app_data")

# Mount the static directory to serve static files (icons, placeholder images, etc.)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
