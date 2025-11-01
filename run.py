# run.py — punto de entrada único
from src.app import app

# Cargar callbacks una vez esté listo el layout
print("🔄 Cargando callbacks...")
import src.callbacks

if __name__ == "__main__":
    print("✅ Ejecutando aplicación Dash unificada")
    app.run_server(host="127.0.0.1", port=8050, debug=True)
