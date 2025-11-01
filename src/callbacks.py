# src/callbacks.py — Lectura de datos, procesamiento y callbacks interactivos

import json
from pathlib import Path
import pandas as pd
import plotly.express as px
from dash import Input, Output, html, dcc, dash_table, callback_context
from src.app import app

# ==========================
# Archivos de datos
# ==========================
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FILE_MAIN = DATA_DIR / "NoFetal2019_CE_15-03-23.xlsx"
FILE_DIVI = DATA_DIR / "Divipola_CE_.xlsx"
FILE_CODIGOS = DATA_DIR / "CodigosDeMuerte_CE_15-03-23.xlsx"
FILE_GEO = DATA_DIR / "col_departamentos.geojson"

# Etiquetas de meses
MESES_LABELS = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

# Orden de grupos de edad
EDAD_CATS_ORD = [
    "Mortalidad neonatal", "Mortalidad infantil", "Primera infancia", "Niñez",
    "Adolescencia", "Juventud", "Adultez temprana", "Adultez intermedia",
    "Vejez", "Longevidad / Centenarios", "Edad desconocida"
]

# ==========================
# Cargar y procesar los datos
# ==========================
def _zfill(s, n):
    return str(s).split(".")[0].zfill(n) if pd.notna(s) else None


def load_data():
    print("🔄 Cargando datos...")
    df = pd.read_excel(FILE_MAIN, engine="openpyxl")
    divi = pd.read_excel(FILE_DIVI, engine="openpyxl")
    cod = pd.read_excel(FILE_CODIGOS, engine="openpyxl")

    df["COD_DEPARTAMENTO"] = df["COD_DEPARTAMENTO"].apply(lambda x: _zfill(x, 2))
    df["COD_MUNICIPIO"] = df["COD_MUNICIPIO"].apply(lambda x: _zfill(x, 5))

    # Sexo
    sexo_map = {1: "Hombre", 2: "Mujer", "1": "Hombre", "2": "Mujer"}
    df["SEXO"] = df["SEXO"].map(sexo_map).fillna(df["SEXO"])

    # ===============================
    # Mes
    # ===============================
    if "MES" in df.columns:
        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").clip(1, 12)
    elif "MES_DEF" in df.columns:
        df["MES"] = pd.to_numeric(df["MES_DEF"], errors="coerce").clip(1, 12)
    elif "FECHA_DEF" in df.columns:
        df["MES"] = pd.to_datetime(df["FECHA_DEF"], errors="coerce").dt.month
    else:
        df["MES"] = pd.NA
    print("📆 Valores únicos de MES:", df["MES"].dropna().unique())

    # Nombres de dptos y municipios
    divi["COD_DEPARTAMENTO"] = divi["COD_DEPARTAMENTO"].apply(lambda x: _zfill(x, 2))
    divi["COD_MUNICIPIO"] = divi["COD_MUNICIPIO"].apply(lambda x: _zfill(x, 5))

    df = df.merge(divi[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates(),
                  on="COD_DEPARTAMENTO", how="left")
    df = df.merge(divi[["COD_MUNICIPIO", "MUNICIPIO"]].drop_duplicates(),
                  on="COD_MUNICIPIO", how="left")

    # Códigos CIE10
    df["COD_MUERTE"] = df["COD_MUERTE"].astype(str).str.strip().str.upper()
    cod["COD_CIE_10"] = cod["COD_CIE_10"].astype(str).str.strip().str.upper()

    df = df.merge(
        cod[["COD_CIE_10", "DESC_CIE_10"]].rename(
            columns={"COD_CIE_10": "COD_MUERTE", "DESC_CIE_10": "CAUSA_MUERTE"}
        ),
        on="COD_MUERTE", how="left"
    )

    # Agrupar grupos de edad
    def agrupar(grupo):
        try:
            g = int(grupo)
        except Exception:
            return "Edad desconocida"
        if 0 <= g <= 4: return "Mortalidad neonatal"
        if 5 <= g <= 6: return "Mortalidad infantil"
        if 7 <= g <= 8: return "Primera infancia"
        if 9 <= g <= 10: return "Niñez"
        if g == 11: return "Adolescencia"
        if 12 <= g <= 13: return "Juventud"
        if 14 <= g <= 16: return "Adultez temprana"
        if 17 <= g <= 19: return "Adultez intermedia"
        if 20 <= g <= 24: return "Vejez"
        if 25 <= g <= 28: return "Longevidad / Centenarios"
        return "Edad desconocida"

    df["GRUPO_EDAD_CAT"] = df["GRUPO_EDAD1"].apply(agrupar)
    df["GRUPO_EDAD_CAT"] = pd.Categorical(df["GRUPO_EDAD_CAT"],
                                          categories=EDAD_CATS_ORD, ordered=True)

    print("✅ Total de filas cargadas:", len(df))
    print("📋 Columnas del DataFrame:", df.columns.tolist())
    return df


DF = load_data()

# ==========================
# Callbacks (sidebar)
# ==========================
TABS = [
    ("mapa", "Mapa nacional"),
    ("meses", "Muertes por mes"),
    ("violencia", "Ciudades violentas"),
    ("bajas", "Ciudades con menor mortalidad"),
    ("causas", "Principales causas"),
    ("sexo", "Muertes por sexo y depto"),
    ("edad", "Distribución por edad"),
]

@app.callback(
    Output("contenido", "children"),
    [Input(f"tab-{val}", "n_clicks") for val, _ in TABS]
)
def render_tab(*args):
    ctx = callback_context
    if not ctx.triggered:
        tab_id = "mapa"
    else:
        tab_id = ctx.triggered[0]["prop_id"].split(".")[0].replace("tab-", "")
    print("📍 Callback ejecutado, pestaña seleccionada:", tab_id)

    # ====== Mapa ======
    if tab_id == "mapa":
        by_dep = DF.groupby("DEPARTAMENTO").size().reset_index(name="Defunciones")
        if FILE_GEO.exists():
            gj = json.loads(FILE_GEO.read_text(encoding="utf-8"))
            fig = px.choropleth(
                by_dep, geojson=gj, featureidkey="properties.NOMBRE_DPT",
                locations="DEPARTAMENTO", color="Defunciones",
                color_continuous_scale="Reds",
                title="Distribución de muertes por departamento (2019)"
            )
            fig.update_geos(fitbounds="locations", visible=False)
        else:
            fig = px.bar(
                by_dep.sort_values("Defunciones", ascending=True),
                x="Defunciones", y="DEPARTAMENTO", orientation="h",
                title="Defunciones por departamento (GeoJSON no encontrado)"
            )
        return dcc.Graph(figure=fig)

    # ====== Muertes por mes ======
    if tab_id == "meses":
        serie = DF.groupby("MES").size().reset_index(name="Defunciones")
        serie["Mes"] = serie["MES"].map(MESES_LABELS)
        fig = px.line(serie, x="Mes", y="Defunciones", markers=True,
                      title="Total de muertes por mes (2019)")
        return dcc.Graph(figure=fig)

    # ====== Ciudades más violentas ======
    if tab_id == "violencia":
        violentos = DF[DF["COD_MUERTE"].str.startswith(("X95", "X96", "X97", "X98", "X99"))]
        if violentos.empty:
            return html.Div(
                html.H4("⚠️ No se encontraron registros con códigos CIE-10 entre X95–X99."),
                style={"textAlign": "center", "color": "#B22222", "padding": "40px"}
            )
        top5 = (violentos.groupby("MUNICIPIO")
                .size().reset_index(name="Casos")
                .sort_values("Casos", ascending=False)
                .head(5))
        fig = px.bar(
            top5, x="MUNICIPIO", y="Casos", color="Casos",
            color_continuous_scale="Reds",
            title="5 ciudades más violentas (CIE-10 X95–X99)"
        )
        fig.update_layout(
            xaxis_title="Municipio", yaxis_title="Número de casos",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        return dcc.Graph(figure=fig)

    # ====== Ciudades con menor mortalidad ======
    if tab_id == "bajas":
        bajas = DF.groupby("MUNICIPIO").size().reset_index(name="Casos").nsmallest(10, "Casos")
        fig = px.pie(bajas, names="MUNICIPIO", values="Casos",
                     title="10 ciudades con menor mortalidad")
        return dcc.Graph(figure=fig)

    # ====== Principales causas de muerte ======
    if tab_id == "causas":
        causas = (DF.groupby(["COD_MUERTE", "CAUSA_MUERTE"])
                    .size().reset_index(name="Casos")
                    .sort_values("Casos", ascending=False).head(10))
        if causas.empty:
            return html.Div("⚠️ No se encontraron causas de muerte disponibles.")
        fig = px.bar(
            causas.sort_values("Casos", ascending=True),
            x="Casos", y="CAUSA_MUERTE",
            orientation="h", color="Casos", color_continuous_scale="Blues",
            title="10 principales causas de muerte en Colombia (2019)"
        )
        table = dash_table.DataTable(
            columns=[
                {"name": "Código CIE-10", "id": "COD_MUERTE"},
                {"name": "Causa", "id": "CAUSA_MUERTE"},
                {"name": "Total de Casos", "id": "Casos"},
            ],
            data=causas.to_dict("records"),
            page_size=10,
            style_table={"overflowX": "auto"},
        )
        return html.Div(
            [dcc.Graph(figure=fig), html.Br(), table],
            style={"width": "95%", "margin": "auto"}
        )

    # ====== Muertes por sexo ======
    if tab_id == "sexo":
        sexo_dep = DF.groupby(["DEPARTAMENTO", "SEXO"]).size().reset_index(name="Casos")
        fig = px.bar(sexo_dep, x="DEPARTAMENTO", y="Casos", color="SEXO",
                     barmode="stack", title="Muertes por sexo y departamento")
        return dcc.Graph(figure=fig)

    # ====== Distribución por edad ======
    if tab_id == "edad":
        hist = DF.groupby("GRUPO_EDAD_CAT").size().reset_index(name="Defunciones")
        fig = px.bar(hist, x="GRUPO_EDAD_CAT", y="Defunciones",
                     title="Distribución de muertes por grupo de edad")
        fig.update_xaxes(categoryorder="array", categoryarray=EDAD_CATS_ORD)
        return dcc.Graph(figure=fig)

    return html.Div("Selecciona una pestaña válida.")
