# src/app.py — definición única de la aplicación Dash
from dash import Dash
from src.layout import get_layout
from pathlib import Path

# ✅ Ruta explícita a la carpeta assets
BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

app = Dash(
    __name__,
    assets_folder=str(ASSETS_DIR),  # 👈 Dash usará esta carpeta sí o sí
    suppress_callback_exceptions=True,
    title="Mortalidad Colombia 2019"
)
server = app.server

# Configurar layout
app.layout = get_layout()
app.validation_layout = app.layout
app = Dash(__name__, suppress_callback_exceptions=True, serve_locally=True)
