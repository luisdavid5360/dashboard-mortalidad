# src/app.py — definición única de la aplicación Dash
from dash import Dash
from src.layout import get_layout
from pathlib import Path
import os  # 👈 AÑADIDO — necesario para os.getcwd()

# ==========================================
# Diagnóstico: confirmar rutas en Render
# ==========================================
print("📍 RUTA ACTUAL DE EJECUCIÓN (cwd):", os.getcwd())
print("📍 RUTA DE ESTE ARCHIVO:", Path(__file__).resolve())

# ✅ Ruta explícita a la carpeta assets
BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"

# ==========================================
# Inicializar la app
# ==========================================
app = Dash(
    __name__,
    assets_folder=str(ASSETS_DIR),
    suppress_callback_exceptions=True,
    title="Mortalidad Colombia 2019",
    serve_locally=True  # 👈 Asegura que cargue assets internos (como logo, CSS)
)

server = app.server

# ==========================================
# Configurar layout
# ==========================================
app.layout = get_layout()
app.validation_layout = app.layout
