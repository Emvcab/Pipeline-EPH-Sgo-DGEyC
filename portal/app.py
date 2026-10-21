"""Panel visual de indicadores EPH para el aglomerado 18."""

from __future__ import annotations

import hmac
import json
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="EPH · Santiago del Estero - La Banda",
    page_icon="📊",
    layout="wide",
)

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import monitor_actualizaciones as monitor
import portal_admin
import pipeline as core
from validacion_metodologica import redondear_un_decimal
from pipeline import normalizar_estado, normalizar_periodo
from visualizacion import filtrar_rango_periodos, rango_eje, variacion
from interpretacion_brechas import lectura_deciles, lectura_dimension
from reporte_pdf import generar_reporte_pdf


DIR_RESULTADOS = RAIZ / "results"
DIR_SNAPSHOT = RAIZ / "data_snapshot"
DIR_DOCS = RAIZ / "docs"
ESTADOS_VALIDOS = {"VALIDADO", "PUBLICADO"}
PORTAL_VERSION = "3.5.0-dev"


# Colores consistentes para las categorías de la sección "Brechas y perfiles".
# Se mantienen iguales aunque cambie el indicador seleccionado.
COLORES_CATEGORIAS = {
    "Varón": "#2563EB",
    "Mujer": "#E11D48",
    "14 a 29 años": "#2563EB",
    "30 a 64 años": "#F59E0B",
    "65 años y más": "#16A34A",
    "Primario incompleto": "#2563EB",
    "Primario completo": "#0891B2",
    "Secundario incompleto": "#F59E0B",
    "Secundario completo": "#EA580C",
    "Superior/universitario incompleto": "#7C3AED",
    "Superior/universitario completo": "#16A34A",
    "Sin instrucción": "#64748B",
}

PALETA_CATEGORIAS = [
    "#2563EB", "#E11D48", "#16A34A", "#F59E0B",
    "#7C3AED", "#0891B2", "#EA580C", "#64748B",
]

# Escala secuencial para deciles: de menor a mayor ingreso.
COLORES_DECILES = [
    "#DBEAFE", "#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6",
    "#2563EB", "#1D4ED8", "#1E40AF", "#1E3A8A", "#172554",
]


def colores_para_categorias(categorias: list[str]) -> list[str]:
    """Asigna colores estables a categorías conocidas y una paleta al resto."""
    colores: list[str] = []
    for i, categoria in enumerate(categorias):
        colores.append(COLORES_CATEGORIAS.get(str(categoria), PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)]))
    return colores


def leer_json(ruta: Path) -> dict | None:
    """Lee JSON sin interrumpir el portal si falta o está dañado."""
    try:
        return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None
    except (OSError, json.JSONDecodeError):
        return None


def leer_csv(ruta: Path) -> pd.DataFrame | None:
    """Lee CSV con un resultado comprensible ante archivos ausentes o inválidos."""
    try:
        return pd.read_csv(ruta) if ruta.exists() else None
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return None
def resolver_archivo_publicado(nombre: str) -> Path:
    """
    Busca primero una salida en la fuente activa.
    Si no existe, utiliza el snapshot publicado como respaldo.
    """
    ruta_activa = DIR_ACTIVO / nombre

    if ruta_activa.exists():
        return ruta_activa

    ruta_snapshot = DIR_SNAPSHOT / nombre

    if ruta_snapshot.exists():
        return ruta_snapshot

    return ruta_activa

def directorio_publicable(directorio: Path) -> bool:
    """Acepta un directorio sólo si su último período está validado."""
    historico = leer_csv(directorio / "historico_SDE.csv")
    estados = leer_csv(directorio / "estado_periodos.csv")
    if historico is None or historico.empty or estados is None or estados.empty:
        return False
    periodos_historico = historico["periodo"].map(normalizar_periodo)
    periodos_estado = estados["periodo"].map(normalizar_periodo)
    estados_normalizados = estados["estado"].map(normalizar_estado)
    if periodos_historico.isna().any() or periodos_estado.isna().any():
        return False
    ultimo_indice = historico.sort_values(["anio", "trimestre"]).index[-1]
    ultimo = periodos_historico.loc[ultimo_indice]
    fila = estados[periodos_estado == ultimo]
    if fila.empty:
        return False
    return estados_normalizados.loc[fila.index[-1]] in ESTADOS_VALIDOS


def seleccionar_fuente() -> tuple[Path | None, bool, str]:
    """Prioriza resultados locales validados y conserva el snapshot como contingencia."""
    if directorio_publicable(DIR_RESULTADOS):
        return DIR_RESULTADOS, False, "Resultados locales validados"
    if directorio_publicable(DIR_SNAPSHOT):
        return DIR_SNAPSHOT, True, "Snapshot agregado validado"
    return None, False, "Sin datos validados"


def formato_numero(valor: object, decimales: int = 0, prefijo: str = "") -> str:
    """Formatea métricas y evita mostrar errores cuando el dato no existe."""
    if valor is None or pd.isna(valor):
        return "No disponible"
    return f"{prefijo}{float(valor):,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formato_tasa(valor: object) -> str:
    return "No disponible" if valor is None or pd.isna(valor) else f"{float(valor):.2f}%"


def delta_pp(actual: object, anterior: object, periodo_anterior: str | None) -> str | None:
    """Formatea una variación en puntos porcentuales para ``st.metric``."""
    cambio = variacion(actual, anterior)
    if cambio is None or not periodo_anterior:
        return None
    return f"{cambio:+.2f} p.p. vs {periodo_anterior}"
def lectura_serie_temporal(
    datos: pd.DataFrame,
    columna: str,
    etiqueta: str,
    *,
    porcentaje: bool = False,
    moneda: bool = False,
) -> str | None:
    """
    Resume descriptivamente una serie entre el primer y último
    período disponible, e informa sus valores máximo y mínimo.
    """
    if columna not in datos.columns or "periodo" not in datos.columns:
        return None

    serie = datos[["periodo", columna]].copy()

    serie[columna] = pd.to_numeric(
        serie[columna],
        errors="coerce",
    )

    serie = serie.dropna(subset=[columna])

    if serie.empty:
        return None

    primero = serie.iloc[0]
    ultimo = serie.iloc[-1]

    valor_inicial = float(primero[columna])
    valor_final = float(ultimo[columna])

    periodo_inicial = str(primero["periodo"])
    periodo_final = str(ultimo["periodo"])

    fila_max = serie.loc[serie[columna].idxmax()]
    fila_min = serie.loc[serie[columna].idxmin()]

    valor_max = float(fila_max[columna])
    valor_min = float(fila_min[columna])

    periodo_max = str(fila_max["periodo"])
    periodo_min = str(fila_min["periodo"])

    diferencia = valor_final - valor_inicial

    if porcentaje:
        return (
            f"{etiqueta}: pasó de {valor_inicial:.2f}% en "
            f"{periodo_inicial} a {valor_final:.2f}% en {periodo_final} "
            f"({diferencia:+.2f} p.p.). "
            f"En el rango seleccionado, el máximo observado fue "
            f"{valor_max:.2f}% en {periodo_max} y el mínimo "
            f"{valor_min:.2f}% en {periodo_min}."
        )

    if moneda:
        variacion_porcentual = (
            ((valor_final / valor_inicial) - 1) * 100
            if valor_inicial != 0
            else None
        )

        texto_variacion = (
            f"{variacion_porcentual:+.1f}% nominal"
            if variacion_porcentual is not None
            else "variación porcentual no disponible"
        )

        return (
            f"{etiqueta}: pasó de ${valor_inicial:,.0f} en "
            f"{periodo_inicial} a ${valor_final:,.0f} en {periodo_final} "
            f"({texto_variacion}). "
            f"El máximo observado fue ${valor_max:,.0f} en {periodo_max} "
            f"y el mínimo ${valor_min:,.0f} en {periodo_min}."
        )

    return (
        f"{etiqueta}: pasó de {valor_inicial:.2f} en {periodo_inicial} "
        f"a {valor_final:.2f} en {periodo_final}. "
        f"Máximo observado: {valor_max:.2f} en {periodo_max}; "
        f"mínimo: {valor_min:.2f} en {periodo_min}."
    )


def grafico_series_interactivo(
    datos: pd.DataFrame,
    columnas: list[str],
    etiquetas: dict[str, str],
    titulo: str,
    y_titulo: str,
    *,
    porcentaje: bool = False,
    moneda: bool = False,
) -> None:
    """Muestra series Plotly con hover, zoom y eje Y ajustado a los datos visibles."""
    disponibles = [c for c in columnas if c in datos.columns]
    if not disponibles or datos.empty:
        st.info("No hay datos suficientes para mostrar este gráfico.")
        return

    fig = go.Figure()
    valores_eje: list[float] = []
    for columna in disponibles:
        serie = pd.to_numeric(datos[columna], errors="coerce")
        valores_eje.extend(serie.dropna().astype(float).tolist())
        if moneda:
            hover = "%{x}<br>%{y:$,.0f}<extra>%{fullData.name}</extra>"
        elif porcentaje:
            hover = "%{x}<br>%{y:.2f}%<extra>%{fullData.name}</extra>"
        else:
            hover = "%{x}<br>%{y:,.2f}<extra>%{fullData.name}</extra>"
        fig.add_trace(
            go.Scatter(
                x=datos["periodo"].astype(str),
                y=serie,
                mode="lines+markers",
                name=etiquetas.get(columna, columna),
                hovertemplate=hover,
            )
        )

    rango = rango_eje(valores_eje)
    if rango is not None and (porcentaje or moneda):
        inferior, superior = rango
        if porcentaje and inferior < 0:
            inferior = 0.0
        rango = (inferior, superior)

    fig.update_layout(
        title=titulo,
        xaxis_title="Período",
        yaxis_title=y_titulo,
        hovermode="x unified",
        legend_title_text="",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    fig.update_yaxes(range=list(rango) if rango is not None else None)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True},
    )


def boton_descarga(ruta: Path, etiqueta: str, clave: str) -> None:
    """Ofrece un archivo existente o explica claramente su ausencia."""
    if ruta.exists() and ruta.is_file():
        st.download_button(
            etiqueta,
            data=ruta.read_bytes(),
            file_name=ruta.name,
            key=clave,
        )
    else:
        st.caption(f"{ruta.name}: no disponible para esta fuente.")


def _config_texto(secret_key: str, env_key: str) -> str | None:
    """Lee configuración administrativa desde secrets o variables de entorno."""
    valor_entorno = os.getenv(env_key)
    if valor_entorno:
        return valor_entorno
    try:
        valor = st.secrets.get(secret_key)
    except (FileNotFoundError, KeyError):
        valor = None
    return str(valor) if valor not in (None, "") else None


def _config_bool(secret_key: str, env_key: str, default: bool = False) -> bool:
    valor = _config_texto(secret_key, env_key)
    if valor is None:
        return default
    return valor.strip().lower() in {"1", "true", "si", "sí", "yes", "on"}


def administrador_autenticado() -> bool:
    """Autenticación simple para el MVP; no sustituye un SSO institucional."""
    clave_configurada = _config_texto("admin_password", "EPH_ADMIN_PASSWORD")
    if not clave_configurada:
        st.warning(
            "El área administrativa está en modo lectura porque no se configuró "
            "`admin_password`/`EPH_ADMIN_PASSWORD`."
        )
        return False
    if st.session_state.get("admin_autenticado", False):
        c1, c2 = st.columns([4, 1])
        c1.success("Sesión administrativa habilitada.")
        if c2.button("Cerrar sesión", key="admin_logout"):
            st.session_state["admin_autenticado"] = False
            st.rerun()
        return True

    clave_ingresada = st.text_input(
        "Clave de administración", type="password", key="admin_password_input"
    )
    if st.button("Ingresar al área administrativa", key="admin_login"):
        if hmac.compare_digest(clave_ingresada, clave_configurada):
            st.session_state["admin_autenticado"] = True
            st.rerun()
        st.error("Clave incorrecta.")
    return False


def definir_periodo_admin(periodo: str) -> None:
    """Carga un período sugerido en los controles sin publicar nada."""
    normalizado = normalizar_periodo(periodo)
    if normalizado is None:
        return
    st.session_state["admin_anio"] = int(normalizado[:4])
    st.session_state["admin_trimestre"] = int(normalizado[-1])


def mostrar_reporte_prevalidacion(reporte: dict) -> None:
    """Renderiza un reporte del monitor en lenguaje operativo."""
    st.subheader(f"Prevalidación {reporte.get('periodo', '')}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Estado", str(reporte.get("estado_prevalidacion", "Sin estado")))
    c2.metric(
        "Período anterior",
        str(reporte.get("comparacion_historica", {}).get("periodo_anterior") or "No disponible"),
    )
    alertas = reporte.get("comparacion_historica", {}).get("alertas", [])
    c3.metric("Alertas orientativas", len(alertas))

    validacion = reporte.get("validacion_critica", {})
    controles = validacion.get("controles", [])
    if controles:
        st.markdown("**Controles críticos**")
        st.dataframe(pd.DataFrame(controles), width="stretch", hide_index=True)

    variaciones = reporte.get("comparacion_historica", {}).get("variaciones", {})
    if variaciones:
        filas = []
        for variable, datos in variaciones.items():
            fila = {"variable": variable, **datos}
            filas.append(fila)
        st.markdown("**Comparación con el histórico**")
        st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)

    if alertas:
        st.warning(
            "Se detectaron variaciones que merecen revisión. Son alertas operativas; "
            "no constituyen pruebas de significancia estadística."
        )
        st.dataframe(pd.DataFrame(alertas), width="stretch", hide_index=True)
    else:
        st.success("No se detectaron alertas por encima de los umbrales operativos.")


DIR_ACTIVO, USANDO_SNAPSHOT, DESCRIPCION_FUENTE = seleccionar_fuente()

st.title("Mercado laboral en Santiago del Estero - La Banda")
st.caption(f"Portal {PORTAL_VERSION} · motor ETL {core.PIPELINE_VERSION}")
st.markdown("**Fuente:** Encuesta Permanente de Hogares — INDEC.")
st.markdown("**Alcance territorial:** Aglomerado 18 — Santiago del Estero - La Banda.")
st.caption(
    "Los datos públicos son producidos por el INDEC. Las tasas laborales y expansiones "
    "generales usan PONDERA; el ingreso ponderado de la ocupación principal P21 usa "
    "PONDIIO. Los resultados del pipeline no constituyen una nueva estadística oficial provincial."
)

if DIR_ACTIVO is None:
    st.error(
        "No hay un histórico acompañado por estados de validación. Se conserva cualquier "
        "archivo existente, pero no se lo muestra hasta que supere los controles críticos."
    )
    st.stop()

if USANDO_SNAPSHOT:
    st.info(
        "El portal está usando una versión agregada y validada de los datos. "
        "No necesita los archivos ZIP ni los microdatos individuales para funcionar."
    )
else:
    st.success("El portal está usando resultados locales validados.")

historico = leer_csv(DIR_ACTIVO / "historico_SDE.csv")
estados = leer_csv(DIR_ACTIVO / "estado_periodos.csv")
meta_historico = leer_json(DIR_ACTIVO / "historico_SDE.meta.json") or {}

if historico is None or historico.empty or estados is None:
    st.error("Los archivos validados no pudieron leerse. Se requiere revisar el snapshot.")
    st.stop()

historico["periodo"] = historico["periodo"].map(normalizar_periodo)
estados["periodo"] = estados["periodo"].map(normalizar_periodo)
estados["estado"] = estados["estado"].map(normalizar_estado)
if historico["periodo"].isna().any() or estados["periodo"].isna().any():
    st.error("Hay períodos fuera del formato canónico YYYYTx en los archivos del portal.")
    st.stop()

periodos_validos = set(
    estados.loc[estados["estado"].isin(ESTADOS_VALIDOS), "periodo"]
)
df = historico[historico["periodo"].isin(periodos_validos)].copy()
df = df.sort_values(["anio", "trimestre"]).reset_index(drop=True)
if df.empty:
    st.error("No hay períodos con estado VALIDADO o PUBLICADO.")
    st.stop()

periodos_disponibles = df["periodo"].astype(str).tolist()
ultimo = df.iloc[-1]
periodo_ultimo = str(ultimo["periodo"])
estado_ultimo = estados.loc[estados["periodo"].astype(str) == periodo_ultimo].iloc[-1]

(
    tab_resumen,
    tab_evolucion,
    tab_presion,
    tab_brechas,
    tab_ingresos,
    tab_calendario,
    tab_calidad,
    tab_documentacion,
    tab_admin,
) = st.tabs([
    "Resumen ejecutivo",
    "Evolución laboral",
    "Presión laboral",
    "Brechas y perfiles",
    "Ingresos",
    "Calendario",
    "Calidad y auditoría",
    "Documentación y descargas",
    "Administración",
])


with tab_resumen:
    st.header("Resumen ejecutivo")
    st.caption(
        "Una síntesis del mercado de trabajo del aglomerado "
        "Santiago del Estero–La Banda a partir de los microdatos de la EPH."
    )

    with st.expander("¿Cómo leer estos indicadores?", expanded=False):
        st.markdown(
            """
            **Actividad:** porcentaje de la población de 14 años y más que
            trabaja o busca trabajo.

            **Empleo:** porcentaje de la población de 14 años y más que está
            ocupada.

            **Desocupación:** porcentaje de la población económicamente activa
            que no tiene trabajo, está disponible y lo busca activamente.

            **Inactividad:** personas que no están ocupadas ni buscan
            activamente trabajo.

            **¿Qué significa estar ocupado?** En la EPH una persona puede ser
            considerada ocupada si trabajó al menos una hora durante la semana
            de referencia, o si tenía trabajo pero estuvo temporalmente ausente.

            **Población expandida:** es la estimación de cuántas personas de la
            población representa la muestra relevada.

            Los resultados provienen de una encuesta por muestreo. Por eso deben
            interpretarse como estimaciones y no como un conteo completo de la
            población.
            """
        )
    with st.expander("¿Cómo leer este portal?", expanded=False):
        st.markdown(
            """
            Este portal transforma los microdatos de la Encuesta Permanente de Hogares
            (EPH) en indicadores del mercado de trabajo para el aglomerado
            **Santiago del Estero–La Banda**.

            **Actividad:** qué proporción de la población de 14 años y más trabaja
            o busca trabajo.

            **Empleo:** qué proporción de la población de 14 años y más está ocupada.

            **Desocupación:** qué proporción de la población económicamente activa
            no tiene trabajo y lo busca activamente.

            **Ocupado:** en la EPH, una persona puede ser considerada ocupada si
            trabajó al menos una hora durante la semana de referencia o si tenía
            trabajo pero estuvo temporalmente ausente.

            **Población expandida:** estimación de cuántas personas de la población
            representa la muestra relevada.

            Los resultados deben interpretarse como estimaciones provenientes de
            una encuesta por muestreo y no como un conteo completo de la población.
            """
        )
    a, b, c = st.columns(3)
    a.metric("Último período validado", periodo_ultimo)
    b.metric("Estado de validación", str(estado_ultimo["estado"]))
    b.caption(str(estado_ultimo.get("mensaje", "Sin mensaje adicional")))
    c.metric(
        "Fecha de actualización",
        str(meta_historico.get("ultima_ejecucion_exitosa")
            or meta_historico.get("fecha_hora_generacion") or "No disponible"),
    )

    st.subheader("Indicadores principales")
    s1, s2 = st.columns(2)
    with s1:
        periodo_referencia = st.selectbox(
            "Período de referencia",
            periodos_disponibles,
            index=len(periodos_disponibles) - 1,
            key="resumen_periodo_referencia",
            help="Permite consultar cualquier trimestre validado sin alterar el histórico.",
        )
    indice_ref = periodos_disponibles.index(periodo_referencia)
    indice_comparacion_default = max(0, indice_ref - 1)
    with s2:
        periodo_comparacion = st.selectbox(
            "Comparar con",
            periodos_disponibles,
            index=indice_comparacion_default,
            key=f"resumen_periodo_comparacion_{periodo_referencia}",
            help="Las diferencias se muestran en puntos porcentuales respecto del período elegido.",
        )
    referencia = df.iloc[indice_ref]
    comparacion = df[df["periodo"].astype(str) == periodo_comparacion].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Tasa de actividad",
        formato_tasa(referencia.get("tasa_actividad_oficial")),
        delta=delta_pp(
            referencia.get("tasa_actividad_oficial"),
            comparacion.get("tasa_actividad_oficial"),
            periodo_comparacion,
        ),
    )
    c2.metric(
        "Tasa de empleo",
        formato_tasa(referencia.get("tasa_empleo_oficial")),
        delta=delta_pp(
            referencia.get("tasa_empleo_oficial"),
            comparacion.get("tasa_empleo_oficial"),
            periodo_comparacion,
        ),
    )
    c3.metric(
        "Tasa de desocupación",
        formato_tasa(referencia.get("tasa_desocupacion")),
        delta=delta_pp(
            referencia.get("tasa_desocupacion"),
            comparacion.get("tasa_desocupacion"),
            periodo_comparacion,
        ),
        delta_color="inverse",
    )
    c4.metric(
        "Proporción inactiva",
        formato_tasa(referencia.get("proporcion_inactiva_total")),
        delta=delta_pp(
            referencia.get("proporcion_inactiva_total"),
            comparacion.get("proporcion_inactiva_total"),
            periodo_comparacion,
        ),
        delta_color="inverse",
    )
    st.caption(
        "Las variaciones se expresan en puntos porcentuales respecto del período elegido para comparación. "
        "Son comparaciones descriptivas, no pruebas de significancia estadística."
    )

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Personas en muestra", formato_numero(referencia.get("n_personas_muestra")))
    c6.metric("Hogares en muestra", formato_numero(referencia.get("n_hogares_muestra")))
    c7.metric(
        "Población total expandida",
        formato_numero(referencia.get("poblacion_expandida_total")),
    )
    c8.metric("Tasa de informalidad", formato_tasa(referencia.get("tasa_informalidad")))
    if pd.isna(referencia.get("tasa_informalidad")):
        st.warning("La informalidad no está disponible porque la variable EMPLEO no existe en ese período.")
    st.info(
        "Advertencia territorial: los microdatos públicos identifican el aglomerado conjunto y "
        "no permiten separar Santiago Capital de La Banda."
    )

    st.subheader("Reporte estático")
    st.caption(
        "Genera un PDF ejecutivo del período de referencia usando únicamente las salidas "
        "agregadas validadas. El reporte no recalcula el ETL."
    )
    ruta_segmentado_reporte = resolver_archivo_publicado(
    f"analisis_segmentado_SDE_{periodo_referencia}.csv"
)
    
    segmentado_reporte = leer_csv(ruta_segmentado_reporte)
    try:
        pdf_reporte = generar_reporte_pdf(
            df,
            periodo_referencia,
            periodo_comparacion=periodo_comparacion,
            segmentado=segmentado_reporte,
            fuente_descripcion=DESCRIPCION_FUENTE,
        )
        st.download_button(
            "Descargar reporte estático PDF",
            data=pdf_reporte,
            file_name=f"Reporte_EPH_SDE_{periodo_referencia}.pdf",
            mime="application/pdf",
            key=f"descargar_reporte_pdf_{periodo_referencia}_{periodo_comparacion}",
            type="primary",
        )
        if segmentado_reporte is None or segmentado_reporte.empty:
            st.caption(
                "El PDF se genera con los indicadores generales. No se encontró una salida "
                "segmentada agregada para este período."
            )
    except Exception as error:
        st.warning(f"No se pudo generar el reporte PDF: {error}")


with tab_evolucion:
    st.header("Evolución laboral")
    st.caption(
        "Gráficos interactivos: puede pasar el cursor, hacer zoom y seleccionar el rango temporal. "
        "El eje vertical se ajusta a los datos visibles y no se fuerza a comenzar en cero cuando eso "
        "ocultaría variaciones relevantes."
    )

    r1, r2 = st.columns(2)
    with r1:
        desde_evol = st.selectbox(
            "Desde", periodos_disponibles, index=0, key="evol_desde"
        )
    with r2:
        hasta_evol = st.selectbox(
            "Hasta",
            periodos_disponibles,
            index=len(periodos_disponibles) - 1,
            key="evol_hasta",
        )
    df_evol = filtrar_rango_periodos(df, desde_evol, hasta_evol)
    if periodos_disponibles.index(desde_evol) > periodos_disponibles.index(hasta_evol):
        st.info("El rango estaba invertido; se ordenó automáticamente para la visualización.")

    grafico_series_interactivo(
        df_evol,
        ["tasa_actividad_oficial", "tasa_empleo_oficial"],
        {
            "tasa_actividad_oficial": "Actividad",
            "tasa_empleo_oficial": "Empleo",
        },
        "Actividad y empleo",
        "Porcentaje",
        porcentaje=True,
    )

    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico_series_interactivo(
            df_evol,
            ["tasa_desocupacion"],
            {"tasa_desocupacion": "Desocupación"},
            "Desocupación",
            "Porcentaje",
            porcentaje=True,
        )
    with derecha:
        grafico_series_interactivo(
            df_evol,
            ["proporcion_inactiva_total"],
            {"proporcion_inactiva_total": "Inactividad total"},
            "Proporción inactiva total",
            "Porcentaje",
            porcentaje=True,
        )

    st.subheader("Informalidad")
    if "tasa_informalidad" in df_evol.columns:
        informalidad = df_evol[["periodo", "tasa_informalidad"]].dropna()
    else:
        informalidad = pd.DataFrame()
    if len(informalidad) >= 2:
        grafico_series_interactivo(
            informalidad,
            ["tasa_informalidad"],
            {"tasa_informalidad": "Informalidad"},
            "Evolución de la informalidad",
            "Porcentaje",
            porcentaje=True,
        )
    else:
        st.info("No hay suficientes períodos con EMPLEO disponible para mostrar una evolución.")
    st.caption(
        "En 2023T1, 2023T2 y 2023T3, la variable necesaria para estimar informalidad "
        "no está disponible. Por ese motivo, el indicador se presenta como no disponible "
        "y no se realiza imputación ni se reemplazan faltantes por cero."
    )
    mensajes_evolucion = []

    indicadores_evolucion = [
        (
            "tasa_actividad_oficial",
            "Actividad",
        ),
        (
            "tasa_empleo_oficial",
            "Empleo",
        ),
        (
            "tasa_desocupacion",
            "Desocupación",
        ),
        (
            "proporcion_inactiva_total",
            "Inactividad",
        ),
        (
            "tasa_informalidad",
            "Informalidad",
        ),
    ]

    for columna, etiqueta in indicadores_evolucion:
        mensaje = lectura_serie_temporal(
            df_evol,
            columna,
            etiqueta,
            porcentaje=True,
        )

        if mensaje:
            mensajes_evolucion.append(mensaje)

    if mensajes_evolucion:
        with st.expander(
            "Lectura descriptiva del período seleccionado",
            expanded=True,
        ):
            st.markdown(
                "\n\n".join(
                    f"- {mensaje}"
                    for mensaje in mensajes_evolucion
                )
            )

            st.caption(
                "La lectura resume las variaciones observadas en el rango "
                "seleccionado. No implica causalidad ni, por sí sola, "
                "significancia estadística."
            )

with tab_presion:
    st.header("Presión sobre el mercado de trabajo")

    st.caption(
        "Estos indicadores permiten observar situaciones de presión laboral que no se reflejan "
        "únicamente en la tasa de desocupación. Todas las tasas de esta sección se calculan "
        "sobre la Población Económicamente Activa (PEA) y utilizan PONDERA."
    )

    columnas_presion = [
        "tasa_ocupados_demandantes",
        "tasa_subocupacion",
        "tasa_subocupacion_demandante",
        "tasa_subocupacion_no_demandante",
    ]

    faltantes_presion = [
        columna
        for columna in columnas_presion
        if columna not in df.columns
    ]

    if faltantes_presion:
        st.warning(
            "Los indicadores de presión laboral todavía no están disponibles "
            "en el histórico activo."
        )

    else:
        p1, p2 = st.columns(2)

        with p1:
            periodo_presion = st.selectbox(
                "Período de referencia",
                periodos_disponibles,
                index=len(periodos_disponibles) - 1,
                key="presion_periodo_referencia",
            )

        indice_presion = periodos_disponibles.index(
            periodo_presion
        )

        fila_presion = df.iloc[indice_presion]

        fila_anterior_presion = (
            df.iloc[indice_presion - 1]
            if indice_presion > 0
            else None
        )

        periodo_anterior_presion = (
            str(fila_anterior_presion["periodo"])
            if fila_anterior_presion is not None
            else None
        )

        with p2:
            st.metric(
                "PEA expandida",
                formato_numero(
                    fila_presion.get(
                        "pea_expandida"
                    )
                ),
            )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Ocupados demandantes",
            formato_tasa(
                fila_presion.get(
                    "tasa_ocupados_demandantes"
                )
            ),
            delta=delta_pp(
                fila_presion.get(
                    "tasa_ocupados_demandantes"
                ),
                (
                    None
                    if fila_anterior_presion is None
                    else fila_anterior_presion.get(
                        "tasa_ocupados_demandantes"
                    )
                ),
                periodo_anterior_presion,
            ),
            delta_color="inverse",
        )

        c2.metric(
            "Subocupación horaria",
            formato_tasa(
                fila_presion.get(
                    "tasa_subocupacion"
                )
            ),
            delta=delta_pp(
                fila_presion.get(
                    "tasa_subocupacion"
                ),
                (
                    None
                    if fila_anterior_presion is None
                    else fila_anterior_presion.get(
                        "tasa_subocupacion"
                    )
                ),
                periodo_anterior_presion,
            ),
            delta_color="inverse",
        )

        c3.metric(
            "Subocupación demandante",
            formato_tasa(
                fila_presion.get(
                    "tasa_subocupacion_demandante"
                )
            ),
            delta=delta_pp(
                fila_presion.get(
                    "tasa_subocupacion_demandante"
                ),
                (
                    None
                    if fila_anterior_presion is None
                    else fila_anterior_presion.get(
                        "tasa_subocupacion_demandante"
                    )
                ),
                periodo_anterior_presion,
            ),
            delta_color="inverse",
        )

        c4.metric(
            "Subocupación no demandante",
            formato_tasa(
                fila_presion.get(
                    "tasa_subocupacion_no_demandante"
                )
            ),
            delta=delta_pp(
                fila_presion.get(
                    "tasa_subocupacion_no_demandante"
                ),
                (
                    None
                    if fila_anterior_presion is None
                    else fila_anterior_presion.get(
                        "tasa_subocupacion_no_demandante"
                    )
                ),
                periodo_anterior_presion,
            ),
            delta_color="inverse",
        )

        st.caption(
            "Las variaciones corresponden a puntos porcentuales respecto "
            "del trimestre inmediatamente anterior disponible. "
            "Son comparaciones descriptivas."
        )

        st.subheader("¿Qué significa cada indicador?")

        st.markdown(
            """
**Ocupados demandantes:** personas ocupadas que buscan activamente otra ocupación.

**Subocupación horaria:** personas ocupadas que trabajan menos de 35 horas semanales
por causas involuntarias y desean trabajar más horas.

**Subocupación demandante:** personas subocupadas que además buscan activamente
otra ocupación.

**Subocupación no demandante:** personas subocupadas que desean trabajar más horas,
pero no están buscando activamente otra ocupación.
"""
        )

        st.info(
            "Una tasa de desocupación baja no implica necesariamente ausencia de "
            "problemas laborales. En la EPH, una persona puede ser considerada ocupada "
            "si trabajó al menos una hora durante la semana de referencia. "
            "Por eso, los indicadores de presión laboral ayudan a complementar la lectura "
            "de la desocupación."
        )
        st.subheader("Jornada e intensidad laboral")

        columnas_horas_portal = [
            "promedio_horas_semanales_ponderado",
            "mediana_horas_semanales_ponderada",
            "sobreocupados_expandidos",
            "tasa_sobreocupacion_horaria",
        ]

        if all(
            columna in df.columns
            for columna in columnas_horas_portal
        ):
            h1, h2, h3, h4 = st.columns(4)

            h1.metric(
                "Promedio semanal",
                (
                    f"{float(fila_presion.get('promedio_horas_semanales_ponderado')):.2f} h"
                    if pd.notna(
                        fila_presion.get(
                            "promedio_horas_semanales_ponderado"
                        )
                    )
                    else "No disponible"
                ),
            )

            h2.metric(
                "Mediana semanal",
                (
                    f"{float(fila_presion.get('mediana_horas_semanales_ponderada')):.1f} h"
                    if pd.notna(
                        fila_presion.get(
                            "mediana_horas_semanales_ponderada"
                        )
                    )
                    else "No disponible"
                ),
            )

            h3.metric(
                "Sobreocupación horaria",
                formato_tasa(
                    fila_presion.get(
                        "tasa_sobreocupacion_horaria"
                    )
                ),
                delta=delta_pp(
                    fila_presion.get(
                        "tasa_sobreocupacion_horaria"
                    ),
                    (
                        None
                        if fila_anterior_presion is None
                        else fila_anterior_presion.get(
                            "tasa_sobreocupacion_horaria"
                        )
                    ),
                    periodo_anterior_presion,
                ),
                delta_color="inverse",
            )

            h4.metric(
                "Sobreocupados expandidos",
                formato_numero(
                    fila_presion.get(
                        "sobreocupados_expandidos"
                    )
                ),
            )

            st.caption(
                "Las horas semanales se obtienen como PP3E_TOT + PP3F_TOT. "
                "El promedio y la mediana se calculan entre ocupados que "
                "trabajaron al menos una hora durante la semana de referencia."
            )

            st.info(
                "La sobreocupación identifica a personas ocupadas que trabajan "
                "más de 45 horas semanales. La tasa se calcula sobre la PEA. "
                "En este proyecto la clasificación utiliza INTENSI=3."
            )

        else:
            st.info(
                "Los indicadores de horas trabajadas e intensidad todavía "
                "no están disponibles en el histórico activo."
            )
        st.subheader("Evolución histórica")

        r1, r2 = st.columns(2)

        with r1:
            desde_presion = st.selectbox(
                "Desde",
                periodos_disponibles,
                index=0,
                key="presion_desde",
            )

        with r2:
            hasta_presion = st.selectbox(
                "Hasta",
                periodos_disponibles,
                index=len(periodos_disponibles) - 1,
                key="presion_hasta",
            )

        df_presion = filtrar_rango_periodos(
            df,
            desde_presion,
            hasta_presion,
        )

        if (
            periodos_disponibles.index(desde_presion)
            > periodos_disponibles.index(hasta_presion)
        ):
            st.info(
                "El rango estaba invertido; se ordenó automáticamente "
                "para la visualización."
            )

        grafico_series_interactivo(
            df_presion,
            [
                "tasa_ocupados_demandantes",
                "tasa_subocupacion",
            ],
            {
                "tasa_ocupados_demandantes":
                    "Ocupados demandantes",
                "tasa_subocupacion":
                    "Subocupación horaria",
            },
            "Ocupados demandantes y subocupación horaria",
            "Porcentaje de la PEA",
            porcentaje=True,
        )

        grafico_series_interactivo(
            df_presion,
            [
                "tasa_subocupacion_demandante",
                "tasa_subocupacion_no_demandante",
            ],
            {
                "tasa_subocupacion_demandante":
                    "Subocupación demandante",
                "tasa_subocupacion_no_demandante":
                    "Subocupación no demandante",
            },
            "Composición de la subocupación",
            "Porcentaje de la PEA",
            porcentaje=True,
        )
        mensajes_presion = []

        indicadores_presion_lectura = [
            (
                "tasa_ocupados_demandantes",
                "Ocupados demandantes",
            ),
            (
                "tasa_subocupacion",
                "Subocupación horaria",
            ),
            (
                "tasa_subocupacion_demandante",
                "Subocupación demandante",
            ),
            (
                "tasa_subocupacion_no_demandante",
                "Subocupación no demandante",
            ),
        ]

        for columna, etiqueta in indicadores_presion_lectura:
            mensaje = lectura_serie_temporal(
                df_presion,
                columna,
                etiqueta,
                porcentaje=True,
            )

            if mensaje:
                mensajes_presion.append(mensaje)

        if mensajes_presion:
            with st.expander(
                "Lectura descriptiva de la presión laboral",
                expanded=True,
            ):
                st.markdown(
                    "\n\n".join(
                        f"- {mensaje}"
                        for mensaje in mensajes_presion
                    )
                )

                st.info(
                    "Una tasa de desocupación baja no resume por sí sola "
                    "toda la presión sobre el mercado laboral. También existen "
                    "personas que ya están ocupadas pero buscan otro empleo o "
                    "desean trabajar más horas."
                )

                st.caption(
                    "Las variaciones son descriptivas y se refieren al rango "
                    "temporal seleccionado. No implican causalidad ni, por sí "
                    "solas, significancia estadística."
                )
        st.subheader("Evolución de horas e intensidad")

        columnas_historicas_horas = [
            "promedio_horas_semanales_ponderado",
            "mediana_horas_semanales_ponderada",
            "tasa_sobreocupacion_horaria",
        ]

        if all(
            columna in df_presion.columns
            for columna in columnas_historicas_horas
        ):
            gh1, gh2 = st.columns(2)

            with gh1:
                grafico_series_interactivo(
                    df_presion,
                    [
                        "promedio_horas_semanales_ponderado",
                        "mediana_horas_semanales_ponderada",
                    ],
                    {
                        "promedio_horas_semanales_ponderado":
                            "Promedio ponderado",
                        "mediana_horas_semanales_ponderada":
                            "Mediana ponderada",
                    },
                    "Horas trabajadas por semana",
                    "Horas semanales",
                )

            with gh2:
                grafico_series_interactivo(
                    df_presion,
                    [
                        "tasa_sobreocupacion_horaria",
                    ],
                    {
                        "tasa_sobreocupacion_horaria":
                            "Sobreocupación horaria",
                    },
                    "Evolución de la sobreocupación",
                    "Porcentaje de la PEA",
                    porcentaje=True,
                )

            st.caption(
                "El promedio y la mediana consideran a los ocupados que "
                "trabajaron al menos una hora en la semana de referencia. "
                "La tasa de sobreocupación corresponde a personas clasificadas "
                "con INTENSI=3 y se calcula sobre la PEA."
            )

            st.warning(
                "La construcción de sobreocupación fue validada internamente "
                "contra las horas trabajadas en los 13 períodos. "
                "El cuadro geográfico utilizado para la validación externa "
                "de presión laboral no publica esta tasa por aglomerado, "
                "por lo que no se presenta como una concordancia numérica "
                "externa contra INDEC."
            )
            mensajes_horas = []

            for columna, etiqueta in [
                (
                    "promedio_horas_semanales_ponderado",
                    "Promedio semanal de horas trabajadas",
                ),
                (
                    "mediana_horas_semanales_ponderada",
                    "Mediana semanal de horas trabajadas",
                ),
            ]:
                mensaje = lectura_serie_temporal(
                    df_presion,
                    columna,
                    etiqueta,
                )

                if mensaje:
                    mensajes_horas.append(mensaje)

            mensaje_sobreocupacion = lectura_serie_temporal(
                df_presion,
                "tasa_sobreocupacion_horaria",
                "Sobreocupación horaria",
                porcentaje=True,
            )

            if mensaje_sobreocupacion:
                mensajes_horas.append(
                    mensaje_sobreocupacion
                )

            if mensajes_horas:
                with st.expander(
                    "Lectura descriptiva de horas e intensidad",
                    expanded=True,
                ):
                    st.markdown(
                        "\n\n".join(
                            f"- {mensaje}"
                            for mensaje in mensajes_horas
                        )
                    )

                    st.info(
                        "Las horas promedio y medianas describen la duración "
                        "semanal del trabajo entre las personas ocupadas que "
                        "trabajaron al menos una hora. La sobreocupación permite "
                        "observar, en cambio, la proporción de la PEA asociada "
                        "a jornadas superiores a 45 horas semanales."
                    )

                    st.caption(
                        "La lectura resume cambios observados en el rango "
                        "seleccionado. Es descriptiva y no implica causalidad "
                        "ni significancia estadística."
                    )

        else:
            st.info(
                "No hay suficientes datos históricos de horas e intensidad "
                "para mostrar esta evolución."
            )
        st.caption(
            "Fuente: elaboración propia a partir de microdatos públicos "
            "de la EPH-INDEC. Los cuatro indicadores fueron contrastados "
            "con las publicaciones del INDEC para los períodos incluidos "
            "en el histórico."
        )
with tab_brechas:
    st.header("Brechas y perfiles")
    st.caption(
    "Esta sección permite analizar diferencias por sexo, edad, nivel educativo, "
    "el cruce entre edad y educación, y deciles de ingreso. "
    "Los resultados son descriptivos: cuanto más pequeño es un grupo, "
    "mayor cautela requiere su interpretación."
)
    periodo_brechas = st.selectbox(
        "Período para análisis segmentado",
        periodos_disponibles,
        index=len(periodos_disponibles) - 1,
        key="brechas_periodo",
    )
    ruta_brechas = resolver_archivo_publicado(
    f"analisis_segmentado_SDE_{periodo_brechas}.csv"
)
    brechas = leer_csv(ruta_brechas)
    if brechas is None or brechas.empty:
        st.info(
           "No se encontró una salida segmentada disponible para este período "
           "ni en los resultados locales ni en el snapshot publicado."
        )
    else:
        dimensiones = brechas["dimension"].dropna().astype(str).unique().tolist()
        dimension = st.selectbox(
            "Dimensión de análisis",
            dimensiones,
            key=f"brechas_dimension_{periodo_brechas}",
        )
        vista = brechas[brechas["dimension"].astype(str) == dimension].copy()
        if dimension == "Edad × Nivel educativo":
            vista["n_muestra"] = pd.to_numeric(
                vista["n_muestra"],
                errors="coerce",
            )

            def clasificar_base_muestral(n):
                if pd.isna(n):
                    return "No disponible"
                if n < 10:
                    return "Muy reducida"
                if n < 30:
                    return "Reducida"
                return "Más amplia"

            vista["base_muestral"] = vista["n_muestra"].apply(
                clasificar_base_muestral
            )

            n_amplia = int((vista["n_muestra"] >= 30).sum())
            n_reducida = int(
                (
                    (vista["n_muestra"] >= 10)
                    & (vista["n_muestra"] < 30)
                ).sum()
            )
            n_muy_reducida = int((vista["n_muestra"] < 10).sum())

            st.info(
                "Este cruce divide la muestra en grupos más específicos. "
                "Por eso algunas combinaciones pueden contener pocos casos. "
                "La población expandida indica a cuántas personas representa la muestra, "
                "pero no reemplaza el número de personas efectivamente observadas."
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Base más amplia",
                n_amplia,
                help="Combinaciones con 30 casos muestrales o más.",
            )

            c2.metric(
                "Base reducida",
                n_reducida,
                help="Combinaciones entre 10 y 29 casos muestrales.",
            )

            c3.metric(
                "Base muy reducida",
                n_muy_reducida,
                help="Combinaciones con menos de 10 casos muestrales.",
            )

            if n_muy_reducida > 0:
                st.warning(
                    "Las categorías con menos de 10 casos se conservan en la tabla "
                    "para mantener la trazabilidad del análisis, pero sus tasas no deben "
                    "interpretarse como estimaciones precisas ni utilizarse para conclusiones fuertes."
                )

            st.caption(
                "Los cortes de 10 y 30 casos son una ayuda de lectura utilizada por este portal. "
                "No constituyen una regla oficial de precisión estadística del INDEC."
            )

        if dimension == "Decil de ingreso":
            vista["_orden_decil"] = pd.to_numeric(
                vista["categoria"].astype(str).str.extract(r"(\d+)")[0],
                errors="coerce",
            )
            vista = (
                vista.sort_values("_orden_decil")
                .drop(columns="_orden_decil")
                .reset_index(drop=True)
            )
            columnas_tabla = [
                "categoria", "n_muestra", "poblacion_expandida",
                "ingreso_promedio_ponderado_ocupados",
            ]
            tabla = vista[columnas_tabla].copy().rename(columns={
                "categoria": "Decil",
                "n_muestra": "Muestra",
                "poblacion_expandida": "Población expandida",
                "ingreso_promedio_ponderado_ocupados": "Ingreso medio ocupación principal",
            })
        else:
            columnas_tabla = [
                "categoria",
                "n_muestra",
                "poblacion_expandida",
                "tasa_actividad",
                "tasa_empleo",
                "tasa_desocupacion",
                "tasa_informalidad",
                "ingreso_promedio_ponderado_ocupados",
            ]

            if dimension == "Edad × Nivel educativo":
                columnas_tabla.append("base_muestral")

            columnas_tabla = [
                c for c in columnas_tabla
                if c in vista.columns
            ]

            tabla = vista[columnas_tabla].copy()

            tabla = tabla.rename(
                columns={
                    "categoria": "Grupo",
                    "n_muestra": "Casos en muestra",
                    "poblacion_expandida": "Población expandida",
                    "tasa_actividad": "Actividad (%)",
                    "tasa_empleo": "Empleo (%)",
                    "tasa_desocupacion": "Desocupación (%)",
                    "tasa_informalidad": "Informalidad (%)",
                    "ingreso_promedio_ponderado_ocupados":
                        "Ingreso medio ocupación principal",
                    "base_muestral": "Base muestral",
                }
            )

        tabla_visual = tabla.copy()

        tabla_visual = tabla_visual.replace(
            {
                None: "—",
                "None": "—",
            }
        )

        tabla_visual = tabla_visual.fillna("—")

        st.dataframe(
            tabla_visual,
            width="stretch",
            hide_index=True,
        )

        if dimension == "Edad × Nivel educativo":
            metrica = st.selectbox(
                "Indicador para comparar",
                [
                    "tasa_actividad",
                    "tasa_empleo",
                    "tasa_desocupacion",
                    "tasa_informalidad",
                ],
                format_func=lambda x: {
                    "tasa_actividad": "Tasa de actividad",
                    "tasa_empleo": "Tasa de empleo",
                    "tasa_desocupacion": "Tasa de desocupación",
                    "tasa_informalidad": "Tasa de informalidad",
                }[x],
                key=f"brechas_metrica_{periodo_brechas}_{dimension}",
            )

            etiquetas_metricas = {
                "tasa_actividad": "Tasa de actividad",
                "tasa_empleo": "Tasa de empleo",
                "tasa_desocupacion": "Tasa de desocupación",
                "tasa_informalidad": "Tasa de informalidad",
            }

            cruce = vista[
                ["categoria", "n_muestra", metrica]
            ].copy()

            cruce[metrica] = pd.to_numeric(
                cruce[metrica],
                errors="coerce",
            )

            cruce[["grupo_edad", "nivel_educativo"]] = (
                cruce["categoria"]
                .astype(str)
                .str.split(" · ", n=1, expand=True)
            )

            orden_edades = [
                "14 a 29 años",
                "30 a 64 años",
                "65 años y más",
            ]

            orden_educacion = [
                "Primario incompleto",
                "Primario completo",
                "Secundario incompleto",
                "Secundario completo",
                "Superior/universitario incompleto",
                "Superior/universitario completo",
                "Sin instrucción",
            ]

            matriz_valores = (
                cruce.pivot(
                    index="grupo_edad",
                    columns="nivel_educativo",
                    values=metrica,
                )
                .reindex(
                    index=orden_edades,
                    columns=orden_educacion,
                )
            )

            matriz_muestra = (
                cruce.pivot(
                    index="grupo_edad",
                    columns="nivel_educativo",
                    values="n_muestra",
                )
                .reindex(
                    index=orden_edades,
                    columns=orden_educacion,
                )
            )

            textos = []

            for edad in orden_edades:
                fila_textos = []

                for nivel in orden_educacion:
                    valor = matriz_valores.loc[edad, nivel]
                    n = matriz_muestra.loc[edad, nivel]

                    if pd.isna(valor):
                        texto = "—"
                    else:
                        texto = f"{valor:.1f}%"

                        if not pd.isna(n):
                            texto += f"<br>n={int(n)}"

                            if n < 10:
                                texto += " ⚠"

                    fila_textos.append(texto)

                textos.append(fila_textos)

            fig = go.Figure(
                data=go.Heatmap(
                    z=matriz_valores.values,
                    x=orden_educacion,
                    y=orden_edades,
                    text=textos,
                    texttemplate="%{text}",
                    customdata=matriz_muestra.values,
                    zmin=0,
                    zmax=100,
                    colorscale="Blues",
                    colorbar=dict(
                        title="%"
                    ),
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "%{x}<br>"
                        "Valor: %{z:.2f}%<br>"
                        "Casos en muestra: %{customdata}"
                        "<extra></extra>"
                    ),
                )
            )

            fig.update_layout(
                title=(
                    f"{etiquetas_metricas[metrica]} "
                    f"por edad y nivel educativo · {periodo_brechas}"
                ),
                xaxis_title="Nivel educativo",
                yaxis_title="Grupo de edad",
                margin=dict(
                    l=20,
                    r=20,
                    t=70,
                    b=20,
                ),
            )

            fig.update_yaxes(
                autorange="reversed"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displaylogo": False},
            )

            st.caption(
                "Cada celda muestra el valor del indicador y el número de casos "
                "observados en la muestra. El símbolo ⚠ identifica combinaciones "
                "con menos de 10 casos. Las celdas sin valor indican que el "
                "indicador no pudo calcularse para esa combinación."
            )
        elif dimension != "Decil de ingreso":
            metrica = st.selectbox(
                "Indicador para comparar",
                [
                    "tasa_actividad",
                    "tasa_empleo",
                    "tasa_desocupacion",
                    "tasa_informalidad",
                ],
                format_func=lambda x: {
                    "tasa_actividad": "Tasa de actividad",
                    "tasa_empleo": "Tasa de empleo",
                    "tasa_desocupacion": "Tasa de desocupación",
                    "tasa_informalidad": "Tasa de informalidad",
                }[x],
                key=f"brechas_metrica_{periodo_brechas}_{dimension}",
            )

            graf = vista[
                ["categoria", metrica]
            ].copy()

            graf[metrica] = pd.to_numeric(
                graf[metrica],
                errors="coerce",
            )

            graf = graf.dropna()

            if not graf.empty:
                categorias_graf = (
                    graf["categoria"]
                    .astype(str)
                    .tolist()
                )

                valores = (
                    graf[metrica]
                    .astype(float)
                    .tolist()
                )

                colores = colores_para_categorias(
                    categorias_graf
                )

                fig = go.Figure(
                    go.Scatter(
                        x=categorias_graf,
                        y=valores,
                        mode="markers+text",
                        marker=dict(
                            size=20,
                            color=colores,
                            line=dict(
                                width=1,
                                color="white",
                            ),
                        ),
                        text=[
                            f"{valor:.2f}%"
                            for valor in valores
                        ],
                        textposition="top center",
                        hovertemplate=(
                            "%{x}<br>"
                            "%{y:.2f}%"
                            "<extra></extra>"
                        ),
                        showlegend=False,
                    )
                )

                rango = rango_eje(valores)

                fig.update_layout(
                    title=f"{dimension} · {periodo_brechas}",
                    xaxis_title="",
                    yaxis_title="Porcentaje",
                    margin=dict(
                        l=20,
                        r=20,
                        t=55,
                        b=20,
                    ),
                )

                if rango is not None:
                    fig.update_yaxes(
                        range=[
                            max(0, rango[0]),
                            rango[1],
                        ]
                    )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displaylogo": False},
                )
                st.subheader("Lectura descriptiva del período")

        mensajes_lectura = []

        if dimension == "Decil de ingreso":
            mensajes_lectura = lectura_deciles(vista)

        elif dimension == "Edad × Nivel educativo":
            muestra_lectura = pd.to_numeric(
                vista["n_muestra"],
                errors="coerce",
            )

            vista_lectura = vista[
                muestra_lectura >= 10
            ].copy()

            if not vista_lectura.empty:
                mensajes_lectura = lectura_dimension(
                    vista_lectura,
                    dimension,
                    metrica,
                )

            mensajes_lectura.append(
                "Las combinaciones con menos de 10 casos "
                "se muestran en la tabla y en la matriz, "
                "pero no se utilizan para identificar máximos "
                "o mínimos en esta lectura automática."
            )

        else:
            mensajes_lectura = lectura_dimension(
                vista,
                dimension,
                metrica,
            )

        if mensajes_lectura:
            st.info(
                "\n\n".join(
                    f"• {mensaje}"
                    for mensaje in mensajes_lectura
                )
            )

        st.caption(
            "Sexo: tasas específicas para población de 14 años y más. Los deciles utilizan "
            "ADECOCUR, la escala decílica del ingreso de la ocupación principal construida por "
            "INDEC para el aglomerado. Si esa variable no existe, no se fabrican deciles locales."
        )

with tab_ingresos:
    st.header("Ingresos nominales")
    periodo_ingreso = st.selectbox(
        "Período de referencia para ingresos",
        periodos_disponibles,
        index=len(periodos_disponibles) - 1,
        key="ingresos_periodo_referencia",
    )
    indice_ingreso = periodos_disponibles.index(periodo_ingreso)
    fila_ingreso = df.iloc[indice_ingreso]
    anterior_ingreso = df.iloc[indice_ingreso - 1] if indice_ingreso > 0 else None
    periodo_anterior_ingreso = (
        str(anterior_ingreso["periodo"]) if anterior_ingreso is not None else None
    )

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Ingreso promedio ponderado",
        formato_numero(fila_ingreso.get("ingreso_promedio_ponderado_observado"), prefijo="$"),
    )
    c2.metric(
        "Ingreso mediano",
        formato_numero(fila_ingreso.get("ingreso_mediano_observado"), prefijo="$"),
    )
    c3.metric(
        "No respuesta de ingresos",
        formato_tasa(fila_ingreso.get("tasa_no_respuesta_ingresos_ocupados")),
        delta=delta_pp(
            fila_ingreso.get("tasa_no_respuesta_ingresos_ocupados"),
            None if anterior_ingreso is None else anterior_ingreso.get("tasa_no_respuesta_ingresos_ocupados"),
            periodo_anterior_ingreso,
        ),
        delta_color="inverse",
    )
    st.warning(
        "Los ingresos son nominales y no representan directamente variaciones del poder "
        "adquisitivo. Para comparaciones reales se requiere deflactación."
    )

    ir1, ir2 = st.columns(2)
    with ir1:
        desde_ing = st.selectbox(
            "Serie desde", periodos_disponibles, index=0, key="ing_desde"
        )
    with ir2:
        hasta_ing = st.selectbox(
            "Serie hasta",
            periodos_disponibles,
            index=len(periodos_disponibles) - 1,
            key="ing_hasta",
        )
    df_ing = filtrar_rango_periodos(df, desde_ing, hasta_ing)
    grafico_series_interactivo(
        df_ing,
        ["ingreso_promedio_ponderado_observado", "ingreso_mediano_observado"],
        {
            "ingreso_promedio_ponderado_observado": "Promedio ponderado",
            "ingreso_mediano_observado": "Mediana",
        },
        "Evolución de ingresos nominales observados",
        "Pesos corrientes",
        moneda=True,
    )

    mensajes_ingresos = []

    for columna, etiqueta in [
        (
            "ingreso_promedio_ponderado_observado",
            "Ingreso promedio ponderado",
        ),
        (
            "ingreso_mediano_observado",
            "Ingreso mediano",
        ),
    ]:
        mensaje = lectura_serie_temporal(
            df_ing,
            columna,
            etiqueta,
            moneda=True,
        )

        if mensaje:
            mensajes_ingresos.append(mensaje)

    if mensajes_ingresos:
        with st.expander(
            "Lectura descriptiva de los ingresos",
            expanded=True,
        ):
            st.markdown(
                "\n\n".join(
                    f"- {mensaje}"
                    for mensaje in mensajes_ingresos
                )
            )

            st.warning(
                "Las variaciones son nominales. Un aumento del ingreso "
                "en pesos no implica necesariamente una mejora del poder "
                "adquisitivo; para eso sería necesario ajustar por inflación."
            )
with tab_calendario:
    st.header("Calendario de publicaciones EPH")
    st.caption(
        "Reutiliza el mismo calendario operativo del pipeline. El estado indica si el período "
        "ya fue validado/publicado localmente o si todavía está pendiente/futuro."
    )
    calendario = portal_admin.construir_calendario(DIR_ACTIVO)
    resumen_cal = portal_admin.resumen_calendario(calendario)
    c1, c2, c3 = st.columns(3)
    c1.metric("Último período validado", periodo_ultimo)
    pendiente = resumen_cal.get("pendiente")
    proxima = resumen_cal.get("proxima_publicacion")
    c2.metric(
        "Pendiente de incorporación",
        pendiente["periodo"] if pendiente else "Ninguno",
        pendiente["publicacion_estimada"] if pendiente else None,
    )
    c3.metric(
        "Próxima publicación esperada",
        proxima["periodo"] if proxima else "Sin fecha futura",
        proxima["publicacion_estimada"] if proxima else None,
    )

    visibles = calendario[
        calendario["periodo"].str[:4].astype(int) >= max(2023, int(periodo_ultimo[:4]) - 1)
    ].copy()
    st.dataframe(
        visibles[["periodo", "publicacion_estimada", "estado"]],
        width="stretch",
        hide_index=True,
    )
    st.info(
        "El calendario indica cuándo corresponde esperar cada publicación. El monitor del área "
        "administrativa verifica después si el ZIP oficial está efectivamente disponible en INDEC."
    )


with tab_calidad:
    st.header("Calidad y auditoría")
    validados = int(estados["estado"].isin(ESTADOS_VALIDOS).sum())
    advertencias = 0
    for periodo in df["periodo"].astype(str):
        esquema_periodo = leer_json(DIR_ACTIVO / f"validacion_esquema_{periodo}.json") or {}
        if any(
            resultado.get("nivel") == "advertencia"
            for resultado in esquema_periodo.values()
            if isinstance(resultado, dict)
        ):
            advertencias += 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Períodos validados", validados)
    c2.metric("Períodos con advertencias", advertencias)
    c3.metric("Última ejecución", str(estado_ultimo["estado"]))

    st.divider()
    st.subheader("Validación metodológica contra INDEC")
    st.caption(
        "Contraste reproducible entre las tasas principales calculadas por el pipeline y "
        "los valores publicados por INDEC para el Aglomerado 18."
    )

    ruta_validacion_metodologica = DIR_DOCS / "validacion_metodologica_indec.csv"
    validacion_metodologica = leer_csv(ruta_validacion_metodologica)

    if validacion_metodologica is not None and not validacion_metodologica.empty:
        vm = validacion_metodologica.copy()
        vm["estado"] = vm["estado"].astype(str).str.upper()
        total_comparaciones = len(vm)
        comparaciones_ok = int((vm["estado"] == "OK").sum())
        periodos_vm = sorted(vm["periodo"].astype(str).unique().tolist())
        indicadores_vm = int(vm["indicador"].nunique())

        v1, v2, v3, v4 = st.columns(4)
        v1.metric("Concordancias", f"{comparaciones_ok} / {total_comparaciones}")
        v2.metric("Períodos contrastados", len(periodos_vm))
        v3.metric("Indicadores contrastados", indicadores_vm)
        v4.metric(
            "Rango verificado",
            f"{periodos_vm[0]}–{periodos_vm[-1]}" if periodos_vm else "No disponible",
        )

        if comparaciones_ok == total_comparaciones:
            st.success(
                "Validación empírica superada: todas las comparaciones reproducen los "
                "valores publicados por INDEC al nivel de redondeo de una cifra decimal."
            )
        else:
            st.warning(
                f"Se detectaron {total_comparaciones - comparaciones_ok} comparaciones que "
                "requieren revisión metodológica."
            )

        nombres_indicadores = {
            "tasa_actividad_oficial": "Actividad",
            "tasa_empleo_oficial": "Empleo",
            "tasa_desocupacion": "Desocupación",
        }
        vista_vm = vm[
            [
                "periodo",
                "indicador",
                "pipeline",
                "indec_publicado",
                "diferencia_pp",
                "estado",
            ]
        ].copy()
        vista_vm["indicador"] = vista_vm["indicador"].map(
            lambda x: nombres_indicadores.get(str(x), str(x))
        )
        vista_vm["pipeline"] = pd.to_numeric(vista_vm["pipeline"], errors="coerce").map(
            lambda x: f"{x:.2f}" if pd.notna(x) else "—"
        )
        vista_vm["indec_publicado"] = pd.to_numeric(
            vista_vm["indec_publicado"], errors="coerce"
        ).map(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        vista_vm["diferencia_pp"] = pd.to_numeric(
            vista_vm["diferencia_pp"], errors="coerce"
        ).map(lambda x: f"{x:+.2f}" if pd.notna(x) else "—")
        vista_vm["estado"] = vista_vm["estado"].map(
            lambda x: "✅ OK" if str(x).upper() == "OK" else "⚠️ REVISAR"
        )
        vista_vm = vista_vm.rename(
            columns={
                "periodo": "Período",
                "indicador": "Indicador",
                "pipeline": "Pipeline",
                "indec_publicado": "INDEC",
                "diferencia_pp": "Diferencia (p.p.)",
                "estado": "Estado",
            }
        )

        with st.expander("Ver las comparaciones Pipeline vs INDEC", expanded=False):
            st.dataframe(vista_vm, width="stretch", hide_index=True)

        estado_componentes = pd.DataFrame(
            [
                {
                    "Componente": "Tasa de actividad",
                    "Estado metodológico": "✅ Validada y reproducida",
                    "Observación": "Contraste externo 2024T1–2026T1",
                },
                {
                    "Componente": "Tasa de empleo",
                    "Estado metodológico": "✅ Validada y reproducida",
                    "Observación": "Contraste externo 2024T1–2026T1",
                },
                {
                    "Componente": "Tasa de desocupación",
                    "Estado metodológico": "✅ Validada y reproducida",
                    "Observación": "Contraste externo 2024T1–2026T1",
                },
                {
                    "Componente": "Tasas específicas 14 años y más",
                    "Estado metodológico": "✅ Implementadas y testeadas",
                    "Observación": "Universo específico actual de comparación",
                },
                {
                    "Componente": "Indicadores 10 años y más",
                    "Estado metodológico": "ℹ️ Referencia histórica complementaria",
                    "Observación": "Se conservan para trazabilidad histórica",
                },
                {
                    "Componente": "Ingreso P21",
                    "Estado metodológico": "✅ PONDIIO implementado y testeado",
                    "Observación": "Sin fallback silencioso a PONDERA",
                },
                {
                    "Componente": "Deciles de ingreso",
                    "Estado metodológico": "✅ ADECOCUR",
                    "Observación": "No se fabrican deciles locales alternativos",
                },
                {
                    "Componente": "Informalidad laboral",
                    "Estado metodológico": "🟡 Contraste externo pendiente",
                    "Observación": "Implementación disponible; falta benchmark externo",
                },
            ]
        )

        st.markdown("**Estado de los componentes metodológicos**")
        st.dataframe(estado_componentes, width="stretch", hide_index=True)

        boton_descarga(
            ruta_validacion_metodologica,
            "Descargar evidencia de validación contra INDEC",
            "dl_validacion_metodologica_indec",
        )
        boton_descarga(
            DIR_DOCS / "MATRIZ_VALIDACION_METODOLOGICA.md",
            "Descargar matriz de validación metodológica",
            "dl_matriz_validacion_metodologica",
        )

        st.info(
            "La concordancia indica que el pipeline reproduce los valores publicados por "
            "INDEC al nivel de redondeo utilizado en los informes verificados. No constituye "
            "una certificación formal del INDEC o de la DGEyC, ni una prueba de significancia "
            "estadística."
        )
    else:
        st.info(
            "La evidencia de validación metodológica no está disponible en esta instalación. "
            "Puede regenerarse con `python scripts/validar_contra_indec.py`."
        )
        st.divider()

    st.subheader("Validación de presión laboral contra INDEC")

    st.caption(
        "Contraste de ocupados demandantes, subocupación horaria, "
        "subocupación demandante y subocupación no demandante para "
        "Santiago del Estero - La Banda."
    )

    ruta_referencia_presion = (
        DIR_DOCS / "referencia_indec_presion_laboral.csv"
    )

    referencia_presion = leer_csv(
        ruta_referencia_presion
    )

    columnas_presion_validacion = {
        "ocupados_demandantes": (
            "ocupados_demandantes_expandidos"
        ),
        "subocupacion": (
            "subocupados_expandidos"
        ),
        "subocupacion_demandante": (
            "subocupados_demandantes_expandidos"
        ),
        "subocupacion_no_demandante": (
            "subocupados_no_demandantes_expandidos"
        ),
    }

    if (
        referencia_presion is not None
        and not referencia_presion.empty
        and all(
            columna in df.columns
            for columna
            in columnas_presion_validacion.values()
        )
        and "pea_expandida" in df.columns
    ):
        filas_validacion_presion = []

        for _, fila_ref in referencia_presion.iterrows():

            periodo = str(
                fila_ref["periodo"]
            )

            fila_hist = df[
                df["periodo"].astype(str)
                == periodo
            ]

            if fila_hist.empty:
                continue

            fila_hist = fila_hist.iloc[-1]

            pea = float(
                fila_hist["pea_expandida"]
            )

            if pea <= 0:
                continue

            for (
                indicador_ref,
                columna_numerador,
            ) in columnas_presion_validacion.items():

                numerador = float(
                    fila_hist[columna_numerador]
                )

                # Se calcula desde numerador y denominador
                # sin utilizar una tasa previamente redondeada.
                tasa_cruda = (
                    numerador / pea * 100
                )

                pipeline_1d = (
                    redondear_un_decimal(
                        tasa_cruda
                    )
                )

                indec_1d = (
                    redondear_un_decimal(
                        float(
                            fila_ref[
                                indicador_ref
                            ]
                        )
                    )
                )

                filas_validacion_presion.append(
                    {
                        "periodo": periodo,
                        "indicador": indicador_ref,
                        "pipeline": pipeline_1d,
                        "indec": indec_1d,
                        "estado": (
                            "OK"
                            if pipeline_1d
                            == indec_1d
                            else "REVISAR"
                        ),
                    }
                )

        validacion_presion = pd.DataFrame(
            filas_validacion_presion
        )

        if not validacion_presion.empty:

            total_presion = len(
                validacion_presion
            )

            ok_presion = int(
                (
                    validacion_presion[
                        "estado"
                    ] == "OK"
                ).sum()
            )

            periodos_presion = (
                validacion_presion[
                    "periodo"
                ].nunique()
            )

            indicadores_presion = (
                validacion_presion[
                    "indicador"
                ].nunique()
            )

            p1, p2, p3, p4 = st.columns(4)

            p1.metric(
                "Concordancias",
                f"{ok_presion} / {total_presion}",
            )

            p2.metric(
                "Períodos contrastados",
                periodos_presion,
            )

            p3.metric(
                "Indicadores",
                indicadores_presion,
            )

            p4.metric(
                "Resultado",
                (
                    "VALIDADO"
                    if ok_presion
                    == total_presion
                    else "REVISAR"
                ),
            )

            if ok_presion == total_presion:
                st.success(
                    "Validación superada: las 52 comparaciones "
                    "reproducen los valores publicados por INDEC "
                    "al nivel de una cifra decimal."
                )
            else:
                st.warning(
                    f"{total_presion - ok_presion} "
                    "comparaciones requieren revisión."
                )

            nombres_presion = {
                "ocupados_demandantes":
                    "Ocupados demandantes",
                "subocupacion":
                    "Subocupación horaria",
                "subocupacion_demandante":
                    "Subocupación demandante",
                "subocupacion_no_demandante":
                    "Subocupación no demandante",
            }

            tabla_presion = (
                validacion_presion.copy()
            )

            tabla_presion[
                "indicador"
            ] = tabla_presion[
                "indicador"
            ].map(
                nombres_presion
            )

            with st.expander(
                "Ver detalle de las 52 comparaciones"
            ):
                st.dataframe(
                    tabla_presion,
                    width="stretch",
                    hide_index=True,
                )

            boton_descarga(
                ruta_referencia_presion,
                "Descargar referencia INDEC "
                "de presión laboral",
                "dl_referencia_presion_indec",
            )

            st.info(
                "La concordancia demuestra reproducción de "
                "los valores publicados al nivel de redondeo "
                "utilizado en los informes. No constituye una "
                "certificación formal del INDEC ni una prueba "
                "de significancia estadística."
            )

    else:
        st.info(
            "La referencia o las columnas necesarias para "
            "validar presión laboral no están disponibles."
        )
    st.divider()
    st.subheader("Estado de períodos")
    st.dataframe(estados, width="stretch", hide_index=True)

    periodo_seleccionado = st.selectbox(
        "Período a auditar", df["periodo"].astype(str).tolist(), index=len(df) - 1
    )
    fila_periodo = df[df["periodo"].astype(str) == periodo_seleccionado].iloc[-1]
    r1, r2, r3 = st.columns(3)
    r1.metric("Personas en muestra", formato_numero(fila_periodo.get("n_personas_muestra")))
    r2.metric("Hogares en muestra", formato_numero(fila_periodo.get("n_hogares_muestra")))
    r3.metric(
        "Población expandida", formato_numero(fila_periodo.get("poblacion_expandida_total"))
    )
    izquierda, derecha = st.columns(2)
    with izquierda:
        st.subheader("Variables, nulos y códigos especiales")
        calidad = leer_csv(DIR_ACTIVO / f"calidad_datos_SDE_{periodo_seleccionado}.csv")
        if calidad is not None and not calidad.empty:
            st.dataframe(calidad, width="stretch", hide_index=True)
        else:
            calidad_agregada = leer_csv(DIR_ACTIVO / "calidad_snapshot_SDE.csv")
            if calidad_agregada is not None:
                fila_calidad = calidad_agregada[
                    calidad_agregada["periodo"].astype(str) == periodo_seleccionado
                ]
                st.dataframe(fila_calidad, width="stretch", hide_index=True)
                st.caption(
                    "Control agregado del snapshot. Los conteos de nulos y códigos especiales por "
                    "variable requieren regenerar el período desde los microdatos."
                )
            else:
                st.info("No hay un reporte de calidad disponible para este período.")
    with derecha:
        st.subheader("Cambios de esquema")
        esquema = leer_json(DIR_ACTIVO / f"validacion_esquema_{periodo_seleccionado}.json")
        if esquema:
            for base in ["individual", "hogar"]:
                resultado = esquema.get(base, {})
                st.write(f"**Base {base}:** {resultado.get('nivel', 'sin estado')}")
                faltantes = resultado.get("obligatorias_faltantes", [])
                opcionales = resultado.get("opcionales_faltantes", [])
                st.caption(
                    f"Obligatorias faltantes: {faltantes or 'ninguna'} · "
                    f"Opcionales faltantes: {opcionales or 'ninguna'}"
                )
        else:
            st.info("No hay validación de esquema disponible para este período.")

    st.subheader("Validaciones lógicas")
    validacion_publicacion = leer_json(
        DIR_ACTIVO / f"validacion_publicacion_{periodo_seleccionado}.json"
    )
    if validacion_publicacion and validacion_publicacion.get("controles"):
        st.dataframe(
            pd.DataFrame(validacion_publicacion["controles"]),
            width="stretch",
            hide_index=True,
        )
    else:
        fila = df[df["periodo"].astype(str) == periodo_seleccionado].iloc[-1]
        chequeos = pd.DataFrame([
            {"control": "población total positiva", "cumple": fila["poblacion_expandida_total"] > 0},
            {"control": "tasas oficiales entre 0 y 100", "cumple": all(
                0 <= float(fila[col]) <= 100
                for col in ["tasa_actividad_oficial", "tasa_empleo_oficial", "tasa_desocupacion"]
            )},
            {"control": "actividad + proporción inactiva = 100", "cumple": abs(
                float(fila["tasa_actividad_oficial"])
                + float(fila["proporcion_inactiva_total"]) - 100
            ) <= 0.02},
        ])
        st.dataframe(chequeos, width="stretch", hide_index=True)

    boton_descarga(
        DIR_ACTIVO / f"indicadores_SDE_{periodo_seleccionado}.meta.json",
        "Descargar metadatos del período",
        f"meta_auditoria_{periodo_seleccionado}",
    )


with tab_documentacion:
    st.header("Documentación y descargas")
    st.caption(f"Fuente activa: {DESCRIPCION_FUENTE}.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Datos agregados")
        boton_descarga(DIR_ACTIVO / "historico_SDE.csv", "Descargar histórico", "dl_hist")
        boton_descarga(
            DIR_ACTIVO / f"indicadores_SDE_{periodo_ultimo}.csv",
            f"Descargar indicadores {periodo_ultimo}",
            "dl_ind",
        )
        boton_descarga(
            DIR_ACTIVO / f"calidad_datos_SDE_{periodo_ultimo}.csv",
            f"Descargar calidad {periodo_ultimo}",
            "dl_cal",
        )
        boton_descarga(DIR_ACTIVO / "estado_periodos.csv", "Descargar estado de períodos", "dl_estado")
    with c2:
        st.subheader("Metadatos y manifiesto")
        boton_descarga(
            DIR_ACTIVO / "historico_SDE.meta.json",
            "Descargar metadatos del histórico",
            "dl_meta_hist",
        )
        boton_descarga(
            DIR_ACTIVO / "manifest_salidas.json",
            "Descargar manifiesto de salidas",
            "dl_manifest",
        )
        boton_descarga(
            DIR_ACTIVO / f"validacion_esquema_{periodo_ultimo}.json",
            "Descargar validación de esquema",
            "dl_esquema",
        )

    st.subheader("Guías")
    for nombre, etiqueta in [
        ("DICCIONARIO_DATOS.md", "Diccionario de datos"),
        ("GUIA_USO.md", "Guía de uso"),
        ("METODOLOGIA.md", "Metodología"),
        ("MATRIZ_VALIDACION_METODOLOGICA.md", "Matriz de validación metodológica"),
        ("MONITOR_ACTUALIZACIONES.md", "Monitor de actualizaciones"),
        ("PORTAL_ADMINISTRACION.md", "Portal y administración"),
    ]:
        ruta = DIR_ACTIVO / nombre
        if not ruta.exists():
            ruta = DIR_DOCS / nombre
        boton_descarga(ruta, f"Descargar {etiqueta}", f"doc_{nombre}")

    st.info(
        "Los posibles indicadores operativos futuros requieren bases internas y una "
        "definición institucional previa. No se derivan de los microdatos públicos."
    )


with tab_admin:
    st.header("Administración del Pipeline EPH")
    st.caption(
        "Área para operadores autorizados. Consulta INDEC, prevalida períodos y, sólo con "
        "confirmación explícita, incorpora un trimestre al histórico."
    )

    if administrador_autenticado():
        escrituras_habilitadas = _config_bool(
            "admin_enable_writes", "EPH_ADMIN_ENABLE_WRITES", default=False
        )
        if escrituras_habilitadas:
            st.success("Modo de incorporación habilitado para esta instalación.")
        else:
            st.info(
                "Monitor y prevalidación habilitados. La incorporación final está bloqueada "
                "hasta configurar `admin_enable_writes=true` o `EPH_ADMIN_ENABLE_WRITES=1`."
            )

        st.subheader("1. Buscar nuevas publicaciones")
        if st.button("Consultar INDEC ahora", key="admin_monitor", type="primary"):
            with st.spinner("Consultando disponibilidad de nuevas publicaciones..."):
                consulta = monitor.detectar_nuevas_publicaciones()
                try:
                    monitor.guardar_consulta_monitor(consulta)
                except OSError:
                    pass
                st.session_state["consulta_monitor"] = consulta

        consulta = st.session_state.get("consulta_monitor")
        if consulta:
            m1, m2, m3 = st.columns(3)
            m1.metric("Último período local", consulta.get("ultimo_periodo_local", ""))
            m2.metric(
                "Nuevas publicaciones", len(consulta.get("nuevas_publicaciones", []))
            )
            m3.metric("Estado del monitor", consulta.get("estado_monitor", ""))
            items = consulta.get("periodos_consultados", [])
            if items:
                st.dataframe(
                    pd.DataFrame(items)[
                        ["periodo", "estado_consulta", "estado_http", "detalle"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            if consulta.get("errores_consulta"):
                st.warning(
                    "Hubo errores de conectividad. No se interpreta un error de consulta como "
                    "ausencia de una publicación."
                )

        st.subheader("2. Prevalidar un trimestre")
        nuevas = [] if not consulta else [
            x["periodo"] for x in consulta.get("nuevas_publicaciones", [])
        ]
        col_a, col_b = st.columns(2)
        with col_a:
            anio_objetivo = st.number_input(
                "Año", min_value=2023, max_value=2100, value=2026, step=1, key="admin_anio"
            )
        with col_b:
            trimestre_objetivo = st.selectbox(
                "Trimestre", core.TRIMESTRES, key="admin_trimestre"
            )
        if nuevas:
            sugerido = nuevas[0]
            st.info(f"El monitor detectó como primer período nuevo disponible: **{sugerido}**.")
            st.button(
                f"Usar {sugerido}",
                key="usar_sugerido",
                on_click=definir_periodo_admin,
                args=(sugerido,),
            )

        periodo_objetivo = monitor.Periodo(int(anio_objetivo), int(trimestre_objetivo))
        forzar_pre = st.checkbox("Forzar redescarga del ZIP", key="admin_forzar_pre")
        if st.button(
            f"Prevalidar {periodo_objetivo.codigo}", key="admin_prevalidar"
        ):
            with st.spinner(
                f"Descargando y prevalidando {periodo_objetivo.codigo} sin publicar..."
            ):
                try:
                    reporte = monitor.prevalidar_periodo(
                        periodo_objetivo, forzar_descarga=forzar_pre
                    )
                    st.session_state["reporte_prevalidacion"] = reporte
                    st.success(
                        f"Prevalidación terminada: {reporte['estado_prevalidacion']}."
                    )
                except Exception as error:
                    st.error(f"No se pudo completar la prevalidación: {error}")

        prevalidaciones = portal_admin.listar_prevalidaciones()
        if not prevalidaciones.empty:
            st.caption("Prevalidaciones guardadas en esta instalación")
            st.dataframe(
                prevalidaciones[
                    ["periodo", "estado_prevalidacion", "fecha_prevalidacion", "n_alertas"]
                ],
                width="stretch",
                hide_index=True,
            )
            opciones = prevalidaciones["periodo"].tolist()
            elegido = st.selectbox(
                "Abrir reporte", opciones, index=len(opciones) - 1, key="admin_reporte_select"
            )
            if st.button("Cargar reporte", key="admin_cargar_reporte"):
                try:
                    st.session_state["reporte_prevalidacion"] = (
                        portal_admin.cargar_prevalidacion(elegido)
                    )
                except Exception as error:
                    st.error(str(error))

        reporte_activo = st.session_state.get("reporte_prevalidacion")
        if reporte_activo:
            mostrar_reporte_prevalidacion(reporte_activo)

            st.subheader("3. Incorporar al histórico")
            periodo_publicar = str(reporte_activo.get("periodo", ""))
            if reporte_activo.get("estado_prevalidacion") != "LISTO_PARA_REVISION":
                st.error(
                    "Este reporte no está listo para revisión final. La incorporación permanece bloqueada."
                )
            elif not escrituras_habilitadas:
                st.warning(
                    "La prevalidación está lista, pero esta instalación está configurada en modo "
                    "seguro sin escrituras finales."
                )
            else:
                st.warning(
                    "Esta acción ejecuta nuevamente el pipeline completo, actualiza `results/` y, "
                    "si todos los controles vuelven a aprobarse, actualiza el snapshot."
                )
                revisado = st.checkbox(
                    "Confirmo que revisé los controles, alertas y metodología del período.",
                    key="admin_revisado",
                )
                confirmacion = st.text_input(
                    f"Escriba {periodo_publicar} para confirmar", key="admin_confirmacion"
                )
                if st.button(
                    f"Incorporar {periodo_publicar} y actualizar snapshot",
                    key="admin_publicar",
                    disabled=not revisado,
                    type="primary",
                ):
                    with st.spinner("Ejecutando validación final y publicación transaccional..."):
                        try:
                            resultado = portal_admin.publicar_periodo_asistido(
                                periodo_publicar,
                                confirmacion=confirmacion,
                                publicar_snapshot=True,
                            )
                            st.success(
                                f"{resultado['periodo']} incorporado correctamente. "
                                "El snapshot fue actualizado."
                            )
                            st.session_state.pop("reporte_prevalidacion", None)
                            st.session_state.pop("consulta_monitor", None)
                            st.rerun()
                        except Exception as error:
                            st.error(
                                f"La incorporación no se completó y se conserva el último estado válido: {error}"
                            )

        st.caption(
            "En Streamlit Cloud el sistema de archivos puede ser efímero. Para uso institucional "
            "persistente, la incorporación debe ejecutarse en infraestructura de la Dirección o "
            "sobre un almacenamiento persistente."
        )


st.divider()
st.caption(
    "Práctica Profesionalizante III · ITSE 2026 · "
    "Achaval · Cabaña · Constantinidi · Gomez · Pinto Villegas"
)
