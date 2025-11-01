# src/layout.py — Layout con sidebar moderno y área de contenido principal
from dash import html, dcc

TABS = [
    ("mapa", "Mapa nacional", "1."),
    ("meses", "Muertes por mes", "2. "),
    ("violencia", "Ciudades violentas", "3. "),
    ("bajas", "Ciudades con menor mortalidad", "4. "),
    ("causas", "Principales causas", "5. "),
    ("sexo", "Muertes por sexo", "6. "),
    ("edad", "Distribución por edad", "7. "),
]

def get_layout():
    return html.Div(
        className="dashboard-container",
        children=[
            # Sidebar lateral
            html.Div(
                className="sidebar",
                children=[
                  html.Div([
                        html.Img(
                            src="/assets/logo-azul-unisalle.svg",
                            className="logo-institucional"
                        ),
                        html.Hr(),
                    ]),

                    html.Div(
                        [
                            html.Div(
                                className="tab-link",
                                id=f"tab-{val}",
                                children=[
                                    html.Span(emoji, className="icon"),
                                    html.Span(label, className="label")
                                ],
                                n_clicks=0
                            )
                            for val, label, emoji in TABS
                        ]
                    ),
                    html.Div(className="footer-sidebar", children=[
                        html.P("Luis David Lenes Padilla © Universidad de La Salle – Maestría en IA 2025 - Aplicaciones 1")
                    ])
                ],
            ),

            # Área principal (contenido dinámico)
            html.Div(
                className="main-content",
                children=[
                    html.Div(
                        [
                            html.H1("Mortalidad en Colombia – 2019", className="main-title"),
                            html.P("Exploración interactiva de datos de mortalidad a nivel nacional",
                                   className="main-subtitle")
                        ],
                        className="main-header"
                    ),
                    html.Div(id="contenido", className="tab-content")
                ],
            )
        ],
    )
