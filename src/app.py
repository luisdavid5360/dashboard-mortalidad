# src/app.py — definición única de la aplicación Dash
from dash import Dash
from src.layout import get_layout
from pathlib import Path
import os

print("📍 RUTA ACTUAL DE EJECUCIÓN (cwd):", os.getcwd())
print("📍 RUTA DE ESTE ARCHIVO:", Path(__file__).resolve())

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

app = Dash(
    __name__,
    assets_folder=str(ASSETS_DIR),
    suppress_callback_exceptions=True,
    title="Mortalidad Colombia 2019",
    serve_locally=True
)

server = app.server

app.layout = get_layout()
app.validation_layout = app.layout

# 👇 Esto es lo que faltaba
from src import callbacks
