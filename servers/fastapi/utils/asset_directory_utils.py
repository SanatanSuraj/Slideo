import os
from utils.get_env import get_app_data_directory_env


def get_images_directory():
    app_data_dir = get_app_data_directory_env() or "./app_data"
    # If relative path, resolve relative to project root (three levels up from fastapi dir)
    if not os.path.isabs(app_data_dir):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
    
    images_directory = os.path.join(app_data_dir, "images")
    os.makedirs(images_directory, exist_ok=True)
    return images_directory


def get_exports_directory():
    app_data_dir = get_app_data_directory_env() or "./app_data"
    # If relative path, resolve relative to project root (three levels up from fastapi dir)
    if not os.path.isabs(app_data_dir):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
    
    export_directory = os.path.join(app_data_dir, "exports")
    os.makedirs(export_directory, exist_ok=True)
    return export_directory

def get_uploads_directory():
    app_data_dir = get_app_data_directory_env() or "./app_data"
    # If relative path, resolve relative to project root (three levels up from fastapi dir)
    if not os.path.isabs(app_data_dir):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        app_data_dir = os.path.join(project_root, app_data_dir.lstrip("./"))
    
    uploads_directory = os.path.join(app_data_dir, "uploads")
    os.makedirs(uploads_directory, exist_ok=True)
    return uploads_directory
