"""
COEMA - Motor de Facturación Eléctrica
Demo con proceso guiado (stepper) para la demo con el cliente.
Extrae datos tarifarios de PDFs de OCEBA, valida, y calcula facturación.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import time
from typing import Dict, List

# ---------------------------------------------------------------------------
# Import PDF extractor (same directory)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_extractor import (
    extract_tariffs_from_pdf,
    extract_tariffs_from_bytes,
    extract_tariffs_from_url,
)

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "cuadros-tarifarios")

PDF_EXAMPLES = {
    "Anexo 6 (N1 - Precio completo)": os.path.join(DOCS_DIR, "IF-2026-01658521-GDEBA-GMOCEBA (1).pdf"),
    "Anexo 14 (N2 - Subsidio hasta 350 kWh)": os.path.join(DOCS_DIR, "IF-2026-01666577-GDEBA-GMOCEBA.pdf"),
    "Anexo 104 (N3 - Tarifa Social)": os.path.join(DOCS_DIR, "IF-2025-45079914-GDEBA-GMOCEBA.pdf"),
}

# URL de la página de OCEBA con cuadros tarifarios
OCEBA_TARIFAS_URL = "https://oceba.gba.gov.ar/nueva_web/s.php?i=17"

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

# Impuestos y leyes (sobre subtotal energía)
IMPUESTOS = {
    "iva": {"nombre": "I.V.A.", "porcentaje": None},  # varía por cliente
    "ley_7290": {"nombre": "Ley Provincial 7290", "porcentaje": 0.04},
    "art_75": {"nombre": "Ley 11769 Art 75 (6%- Ex.9226)", "porcentaje": 0.06},
    "art_72bis": {"nombre": "Ley 11769 art.72 Bis (0,001%)", "porcentaje": 0.00001},
    "fondo": {"nombre": "Ley 11769 Fondo Compensador", "porcentaje": 0.055},
}

# CTT de resolución OCEBA separada (Res 2019-189)
CTT_POR_KWH = {"T1R": 9.8780, "T1RE": 4.2020}

# Alumbrado público
ALUMBRADO_PUBLICO = {1: 14000.00}

# Otros conceptos (punto de venta aparte)
OTROS_CONCEPTOS_PORCENTAJE_RES_ASAM = 0.1346  # ~13.46% subtotal energía
BOMBEROS = 960.00

# Tarifa ANTERIOR (hardcoded de la demo vieja, sirve para comparar)
TARIFAS_ANTERIORES = {
    "T1R": {
        "nombre": "Tarifa 1 Residencial",
        "escalones": [
            {"num": 1, "nombre": "R1", "desde": 0, "hasta": 150, "cargo_fijo": 5200.00, "cargo_variable": 158.50},
            {"num": 2, "nombre": "R2", "desde": 150, "hasta": 200, "cargo_fijo": 6100.00, "cargo_variable": 162.80},
            {"num": 3, "nombre": "R3", "desde": 200, "hasta": 400, "cargo_fijo": 6895.82, "cargo_variable": 165.40},
            {"num": 4, "nombre": "R4", "desde": 400, "hasta": 500, "cargo_fijo": 8846.72, "cargo_variable": 173.62},
            {"num": 5, "nombre": "R5", "desde": 500, "hasta": 600, "cargo_fijo": 10500.00, "cargo_variable": 182.50},
            {"num": 6, "nombre": "R6", "desde": 600, "hasta": 99999, "cargo_fijo": 12500.00, "cargo_variable": 195.80},
        ],
    },
    "T1RE": {
        "nombre": "Tarifa 1 Residencial Estacional",
        "escalones": [
            {"num": 1, "nombre": "RE1", "desde": 0, "hasta": 500, "cargo_fijo": 11911.11, "cargo_variable": 206.64},
            {"num": 2, "nombre": "RE2", "desde": 500, "hasta": 99999, "cargo_fijo": 15000.00, "cargo_variable": 225.00},
        ],
    },
}

# Clientes demo (datos ofuscados)
CLIENTES = {
    "10140": {
        "nombre": "DIEGO P.",
        "direccion": "Calle *** N. 452",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1R",
        "condicion_iva": "Monotributista",
        "iva": 0.27,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "197*****",
        "servicio": "1014*****",
        "consumo_kwh": 422,
        "historial": [
            {"periodo": "2025-07", "kwh": 280},
            {"periodo": "2025-08", "kwh": 310},
            {"periodo": "2025-09", "kwh": 295},
            {"periodo": "2025-10", "kwh": 320},
            {"periodo": "2025-11", "kwh": 296},
            {"periodo": "2025-12", "kwh": 422},
        ],
    },
    "1564": {
        "nombre": "CRISTINA C.",
        "direccion": "Calle *** N. 209",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1RE",
        "condicion_iva": "Consumidor Final",
        "iva": 0.21,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "315*****",
        "servicio": "1564*****",
        "consumo_kwh": 170,
        "historial": [
            {"periodo": "2025-07", "kwh": 65},
            {"periodo": "2025-08", "kwh": 72},
            {"periodo": "2025-09", "kwh": 58},
            {"periodo": "2025-10", "kwh": 61},
            {"periodo": "2025-11", "kwh": 44},
            {"periodo": "2025-12", "kwh": 170},
        ],
    },
    "20331": {
        "nombre": "CARLOS M.",
        "direccion": "Av. *** N. 1205",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1R",
        "condicion_iva": "Monotributista",
        "iva": 0.27,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "224*****",
        "servicio": "2033*****",
        "consumo_kwh": 180,
        "historial": [
            {"periodo": "2025-07", "kwh": 195},
            {"periodo": "2025-08", "kwh": 210},
            {"periodo": "2025-09", "kwh": 175},
            {"periodo": "2025-10", "kwh": 190},
            {"periodo": "2025-11", "kwh": 165},
            {"periodo": "2025-12", "kwh": 180},
        ],
    },
    "5892": {
        "nombre": "MARIA L.",
        "direccion": "Calle *** N. 87",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1RE",
        "condicion_iva": "Consumidor Final",
        "iva": 0.21,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "412*****",
        "servicio": "5892*****",
        "consumo_kwh": 320,
        "historial": [
            {"periodo": "2025-07", "kwh": 285},
            {"periodo": "2025-08", "kwh": 310},
            {"periodo": "2025-09", "kwh": 275},
            {"periodo": "2025-10", "kwh": 340},
            {"periodo": "2025-11", "kwh": 290},
            {"periodo": "2025-12", "kwh": 320},
        ],
    },
    "30102": {
        "nombre": "ROBERTO S.",
        "direccion": "Ruta *** Km 12",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1R",
        "condicion_iva": "Monotributista",
        "iva": 0.27,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "508*****",
        "servicio": "3010*****",
        "consumo_kwh": 580,
        "historial": [
            {"periodo": "2025-07", "kwh": 520},
            {"periodo": "2025-08", "kwh": 545},
            {"periodo": "2025-09", "kwh": 510},
            {"periodo": "2025-10", "kwh": 560},
            {"periodo": "2025-11", "kwh": 535},
            {"periodo": "2025-12", "kwh": 580},
        ],
    },
    "7721": {
        "nombre": "ANA G.",
        "direccion": "Calle *** N. 33",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1R",
        "condicion_iva": "Monotributista",
        "iva": 0.27,
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "189*****",
        "servicio": "7721*****",
        "consumo_kwh": 95,
        "historial": [
            {"periodo": "2025-07", "kwh": 88},
            {"periodo": "2025-08", "kwh": 102},
            {"periodo": "2025-09", "kwh": 78},
            {"periodo": "2025-10", "kwh": 92},
            {"periodo": "2025-11", "kwh": 85},
            {"periodo": "2025-12", "kwh": 95},
        ],
    },
}

# Procedimiento de facturación (42 pasos)
PROCEDIMIENTO = [
    (1, "Descarga consumos SgiMovil", False),
    (2, "División/Ajuste de consumos", False),
    (3, "Cargar Cuadro Tarifario", True),
    (4, "Cargar tasa interés OCEBA", False),
    (5, "Cargar Padrón ARBA", False),
    (6, "Cargar tasa alumbrado público", False),
    (7, "Cargar Padrón Subsidio RASE", True),
    (8, "Sincronizar Perfil Tarifa Social", True),
    (9, "Generar Intereses (entre 15 y 18)", False),
    (10, "Cargar archivo Multas", False),
    (11, "Proceso pre facturación", True),
    (12, "Reportes usuarios activos/no activos", False),
    (13, "Reportes lecturas fuera de fecha", False),
    (14, "Ejecutar validador Pre-Facturación", True),
    (15, "Cargar CESP", False),
    (16, "GENERAR - CONTROLAR - CERRAR Facturación", True),
    (17, "Generar Otros Servicios", False),
    (18, "Controlar cant. usuarios vs ruta", False),
    (19, "Cerrar Otros Servicios", False),
    (20, "Ejecutar validador POST-Facturación", True),
    (21, "Conciliación Recibo/Factura", False),
    (22, "Conciliación Factura Negativa", False),
    (23, "Generación de Cupones", False),
    (24, "Generación QR de Cupones", False),
    (25, "Impresión masiva en papel", False),
    (26, "Impresión masiva en PDF", False),
    (27, "Publicación PDF en Oficina Virtual", False),
    (28, "Envío PDF por mail", False),
    (29, "Envío archivos RIPSA", False),
    (30, "Envío archivos BANELCO", False),
    (31, "Envío archivos LINK", False),
    (32, "Envío archivos DÉBITOS VISA", False),
    (33, "Envío archivos Mercado Pago", False),
    (34, "Envío archivos Botón Macro", False),
    (35, "Envío facturas Municipalidad", False),
    (36, "Envío facturas Fedecoba", False),
    (37, "Envío facturas OCEBA Bomberos", False),
    (38, "Envío consumo Coto p/ Cammesa", False),
    (39, "Envío OCEBA protocolo A", False),
    (40, "Agregado tarifario", False),
    (41, "Envío OCEBA violencia de género", False),
    (42, "Envío OCEBA entidades bien público", False),
]


# ============================================
# MOTOR DE FACTURACIÓN
# ============================================

def obtener_escalon(tarifa: str, kwh: int, tarifas: dict) -> dict:
    """Obtiene el escalón correspondiente según tarifa y consumo."""
    escalones = tarifas[tarifa]["escalones"]
    for e in escalones:
        if e["desde"] <= kwh < e["hasta"]:
            return e
    return escalones[-1]


def calcular_factura(tarifa: str, kwh: int, iva_rate: float, tarifas: dict,
                     zona_alumbrado: int = 1) -> dict:
    """Calcula todos los componentes de una factura eléctrica."""
    escalon = obtener_escalon(tarifa, kwh, tarifas)

    # Energía
    cargo_fijo = escalon["cargo_fijo"]
    cargo_variable = kwh * escalon["cargo_variable"]
    ctt = kwh * CTT_POR_KWH.get(tarifa, 0)
    subtotal_energia = cargo_fijo + cargo_variable + ctt

    # Impuestos (sobre subtotal energía)
    iva = subtotal_energia * iva_rate
    ley_7290 = subtotal_energia * 0.04
    art_75 = subtotal_energia * 0.06
    art_72bis = subtotal_energia * 0.00001
    fondo = subtotal_energia * 0.055
    subtotal_leyes = iva + ley_7290 + art_75 + art_72bis + fondo

    # Alumbrado
    alumbrado = ALUMBRADO_PUBLICO.get(zona_alumbrado, 14000.00)

    # Total Liquidación Servicios Públicos
    total = subtotal_energia + subtotal_leyes + alumbrado

    # Otros conceptos (punto de venta aparte)
    res_asamblea = subtotal_energia * OTROS_CONCEPTOS_PORCENTAJE_RES_ASAM
    total_otros = res_asamblea + BOMBEROS

    iva_label = "Monotributo IVA 27%" if iva_rate == 0.27 else f"I.V.A. {iva_rate*100:.0f}%"

    return {
        "escalon": escalon,
        "desglose": [
            {"concepto": f"Cargo Fijo {tarifa} ({escalon['nombre']})", "importe": cargo_fijo, "tipo": "energia"},
            {"concepto": f"Cargo Variable {tarifa} ({kwh} kWh x ${escalon['cargo_variable']:.4f})", "importe": cargo_variable, "tipo": "energia"},
            {"concepto": f"CTT Art 5° Resol 2019-189 ({kwh} x {CTT_POR_KWH.get(tarifa, 0):.4f})", "importe": ctt, "tipo": "energia"},
            {"concepto": "Subtotal Energía", "importe": subtotal_energia, "tipo": "subtotal"},
            {"concepto": iva_label, "importe": iva, "tipo": "ley"},
            {"concepto": "Ley Provincial 7290", "importe": ley_7290, "tipo": "ley"},
            {"concepto": "Ley 11769 Art 75 (6%- Ex.9226)", "importe": art_75, "tipo": "ley"},
            {"concepto": "Ley 11769 art.72 Bis (0,001%)", "importe": art_72bis, "tipo": "ley"},
            {"concepto": "Ley 11769 Fondo Compensador", "importe": fondo, "tipo": "ley"},
            {"concepto": "Subtotal Leyes", "importe": subtotal_leyes, "tipo": "subtotal"},
            {"concepto": "Alumbrado Público ord 2945/23", "importe": alumbrado, "tipo": "otro"},
        ],
        "otros_conceptos": [
            {"concepto": "Res. Asam 21/10/15", "importe": res_asamblea},
            {"concepto": "Bomberos", "importe": BOMBEROS},
            {"concepto": "TOTAL", "importe": total_otros},
        ],
        "resumen": {
            "subtotal_energia": subtotal_energia,
            "iva": iva,
            "subtotal_leyes": subtotal_leyes,
            "alumbrado": alumbrado,
            "total": total,
            "otros_conceptos": total_otros,
            "total_general": total + total_otros,
        },
    }


def fmt(valor: float) -> str:
    """Formatea como moneda argentina."""
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================
# SESSION STATE
# ============================================

def init_state():
    defaults = {
        'paso': 1,
        'datos_oceba': None,
        'datos_validados': False,
        'resultados_facturacion': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def ir_a_paso(n):
    st.session_state.paso = n


# ============================================
# COMPONENTES UI
# ============================================

def render_stepper(paso_actual: int):
    """Indicador de pasos clickable en la parte superior."""
    nombres = ["Datos OCEBA", "Validación", "Padrón Socios", "Facturación"]
    # Determinar qué pasos son accesibles
    puede_ir = {
        1: True,
        2: st.session_state.datos_oceba is not None,
        3: st.session_state.datos_validados,
        4: st.session_state.datos_validados,
    }
    cols = st.columns(len(nombres))
    for i, (col, nombre) in enumerate(zip(cols, nombres)):
        n = i + 1
        with col:
            if n == paso_actual:
                st.button(f"▶ Paso {n} - {nombre}", key=f"step_{n}",
                          disabled=True, type="primary", use_container_width=True)
            elif n < paso_actual:
                st.button(f"✓ Paso {n} - {nombre}", key=f"step_{n}",
                          on_click=ir_a_paso, args=(n,), use_container_width=True)
            elif puede_ir.get(n, False):
                st.button(f"Paso {n} - {nombre}", key=f"step_{n}",
                          on_click=ir_a_paso, args=(n,), use_container_width=True)
            else:
                st.button(f"Paso {n} - {nombre}", key=f"step_{n}",
                          disabled=True, use_container_width=True)


def render_sidebar():
    """Sidebar con resumen del procedimiento y métricas."""
    with st.sidebar:
        st.header("Motor de Facturación")
        st.caption("COEMA - Gral. Madariaga")
        st.divider()

        st.subheader("Procedimiento Actual")
        pasos_auto = sum(1 for _, _, auto in PROCEDIMIENTO if auto)
        c1, c2 = st.columns(2)
        c1.metric("Total pasos", len(PROCEDIMIENTO))
        c2.metric("Automatizados", pasos_auto)

        st.metric("Tiempo ahorrado estimado", "~4 días/mes")
        st.caption("Paso 3 (Cargar Cuadro Tarifario) hoy toma 3-4 días de carga manual. "
                   "Con el motor: 30 segundos.")

        with st.expander("Ver los 42 pasos del procedimiento"):
            for num, desc, auto in PROCEDIMIENTO:
                if auto:
                    st.markdown(f":robot_face: ~~{num}. {desc}~~  **Automatizado**")
                else:
                    st.markdown(f":white_circle: {num}. {desc}")

        st.divider()
        st.caption("Pasos automatizados: 3, 7, 8, 11, 14, 16, 20")
        st.caption("Próximos: 23-28 (generación y distribución), 29-34 (medios de pago)")

        st.divider()
        if st.session_state.datos_oceba:
            d = st.session_state.datos_oceba
            st.success(f"Cuadro cargado: Anexo {d['anexo']} ({d['nivel']})")
            for cod, tar in d['tarifas'].items():
                st.caption(f"{cod}: {len(tar['escalones'])} escalones")


def render_navegacion(puede_avanzar: bool = True):
    """Botones de navegación Anterior/Siguiente."""
    paso = st.session_state.paso
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    if paso > 1:
        c1.button(":arrow_left: Anterior", on_click=ir_a_paso, args=(paso - 1,),
                  use_container_width=True)
    if paso < 4 and puede_avanzar:
        c3.button("Siguiente :arrow_right:", on_click=ir_a_paso, args=(paso + 1,),
                  type="primary", use_container_width=True)


# ============================================
# PASO 1: DATOS OCEBA
# ============================================

def render_paso_1():
    st.header("Paso 1: Obtener Datos de OCEBA")
    st.markdown("Obtenga el cuadro tarifario publicado por OCEBA. "
                "El sistema extrae automáticamente los valores de cada escalón.")

    tab_url, tab_upload, tab_example = st.tabs([
        "Descargar desde OCEBA",
        "Subir PDF",
        "Usar PDF de ejemplo",
    ])

    # --- TAB 1: DESCARGAR DESDE OCEBA ---
    with tab_url:
        st.markdown(
            f"Los cuadros tarifarios se publican en la web de OCEBA: "
            f"[oceba.gba.gov.ar/nueva_web/s.php?i=17]({OCEBA_TARIFAS_URL})"
        )
        st.markdown("Copie la URL del PDF del cuadro tarifario que desea cargar y péguela aquí.")

        pdf_url = st.text_input(
            "URL del PDF de OCEBA",
            placeholder="https://oceba.gba.gov.ar/.../IF-2026-XXXXX-GDEBA-GMOCEBA.pdf",
            help="Pegue la URL directa al PDF del cuadro tarifario desde la web de OCEBA",
        )
        if st.button("Descargar y extraer datos", type="primary", key="btn_url"):
            if not pdf_url:
                st.warning("Ingrese la URL del PDF.")
            elif not pdf_url.lower().endswith('.pdf'):
                st.warning("La URL debe apuntar a un archivo PDF.")
            else:
                try:
                    with st.spinner("Descargando PDF desde OCEBA..."):
                        time.sleep(0.5)
                        data = extract_tariffs_from_url(pdf_url)
                    _mostrar_resultado_extraccion(data, f"Descargado desde: {pdf_url}")
                except Exception as e:
                    st.error(f"No se pudo descargar el PDF: {e}")
                    st.info("Puede intentar descargarlo manualmente y subirlo en la pestaña **Subir PDF**.")

    # --- TAB 2: SUBIR PDF ---
    with tab_upload:
        uploaded = st.file_uploader(
            "Arrastre aquí el PDF de Resolución OCEBA",
            type="pdf",
            help="PDFs de cuadros tarifarios descargados de oceba.gba.gov.ar",
        )
        if uploaded:
            with st.spinner("Extrayendo datos del PDF..."):
                time.sleep(0.5)
                data = extract_tariffs_from_bytes(uploaded.read())
            _mostrar_resultado_extraccion(data, f"Archivo: {uploaded.name}")

    # --- TAB 3: USAR PDF DE EJEMPLO ---
    with tab_example:
        st.markdown("PDFs de cuadros tarifarios disponibles en el sistema:")
        selected = st.radio(
            "Seleccione un cuadro tarifario",
            options=list(PDF_EXAMPLES.keys()),
            index=0,
        )
        if st.button("Extraer datos del PDF", type="primary", key="btn_example"):
            pdf_path = PDF_EXAMPLES[selected]
            if os.path.exists(pdf_path):
                with st.spinner("Extrayendo datos del PDF..."):
                    time.sleep(0.5)
                    data = extract_tariffs_from_pdf(pdf_path)
                _mostrar_resultado_extraccion(data, f"Archivo: {os.path.basename(pdf_path)}")
            else:
                st.error(f"No se encontró el archivo: {pdf_path}")

    puede_avanzar = st.session_state.datos_oceba is not None
    render_navegacion(puede_avanzar)


def _mostrar_resultado_extraccion(data: dict, fuente: str = ""):
    """Muestra resultados de extracción y guarda en session state."""
    if not data.get('tarifas'):
        st.error("No se pudieron extraer datos tarifarios del PDF. "
                 "Verifique que sea un cuadro tarifario OCEBA válido.")
        return

    st.session_state.datos_oceba = data
    st.session_state.datos_validados = False
    st.session_state.resultados_facturacion = None

    st.success(
        f"Detectado: **Anexo {data['anexo']}** - Nivel **{data['nivel']}** "
        f"({data['descripcion']})"
    )
    if fuente:
        st.caption(fuente)

    for cod, tarifa in data['tarifas'].items():
        st.subheader(f"{cod} - {tarifa['nombre']} ({len(tarifa['escalones'])} escalones)")
        rows = []
        for e in tarifa['escalones']:
            hasta_label = f"{e['hasta']:,}" if e['hasta'] < 99999 else "+"
            rows.append({
                "Escalón": e['nombre'],
                "Rango kWh": f"{e['desde']} - {hasta_label}",
                "Cargo Fijo ($/mes)": fmt(e['cargo_fijo']),
                "Cargo Variable ($/kWh)": fmt(e['cargo_variable']),
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


# ============================================
# PASO 2: VALIDACIÓN
# ============================================

def render_paso_2():
    st.header("Paso 2: Validar Cuadro Tarifario")

    data = st.session_state.datos_oceba
    if data is None:
        st.warning("Primero debe cargar un cuadro tarifario en el Paso 1.")
        render_navegacion(False)
        return

    st.markdown(f"Comparando **Anexo {data['anexo']} ({data['nivel']})** "
                "con los valores de la resolución anterior. "
                "Puede editar los valores de Cargo Fijo y Cargo Variable si detecta algún error.")

    # --- Comparación y edición por tarifa ---
    edited_tarifas = {}
    for cod in ["T1R", "T1RE"]:
        if cod not in data['tarifas']:
            continue
        nuevos = data['tarifas'][cod]['escalones']
        anteriores = TARIFAS_ANTERIORES.get(cod, {}).get('escalones', [])
        ant_map = {e['num']: e for e in anteriores}

        st.subheader(f"{cod} - {data['tarifas'][cod]['nombre']}")

        if len(nuevos) != len(anteriores):
            st.info(f"Cantidad de escalones cambió: {len(anteriores)} :arrow_right: {len(nuevos)}")

        # Comparación con anterior (read-only, en expander)
        with st.expander("Ver comparación con resolución anterior", expanded=False):
            comp_rows = []
            for e in nuevos:
                ant = ant_map.get(e['num'])
                if ant:
                    delta_cf = ((e['cargo_fijo'] - ant['cargo_fijo']) / ant['cargo_fijo'] * 100) if ant['cargo_fijo'] else 0
                    delta_cv = ((e['cargo_variable'] - ant['cargo_variable']) / ant['cargo_variable'] * 100) if ant['cargo_variable'] else 0
                    comp_rows.append({
                        "Esc.": e['nombre'],
                        "CF Anterior": fmt(ant['cargo_fijo']),
                        "CF Nuevo": fmt(e['cargo_fijo']),
                        "CF %": f"{delta_cf:+.1f}%",
                        "CV Anterior": fmt(ant['cargo_variable']),
                        "CV Nuevo": fmt(e['cargo_variable']),
                        "CV %": f"{delta_cv:+.1f}%",
                    })
                else:
                    comp_rows.append({
                        "Esc.": e['nombre'],
                        "CF Anterior": "—",
                        "CF Nuevo": fmt(e['cargo_fijo']),
                        "CF %": "NUEVO",
                        "CV Anterior": "—",
                        "CV Nuevo": fmt(e['cargo_variable']),
                        "CV %": "NUEVO",
                    })
            st.dataframe(pd.DataFrame(comp_rows), hide_index=True, use_container_width=True)

        # Tabla editable con valores extraídos
        edit_rows = []
        for e in nuevos:
            hasta_label = e['hasta'] if e['hasta'] < 99999 else 99999
            edit_rows.append({
                "Escalón": e['nombre'],
                "Desde kWh": e['desde'],
                "Hasta kWh": hasta_label,
                "Cargo Fijo ($/mes)": e['cargo_fijo'],
                "Cargo Variable ($/kWh)": e['cargo_variable'],
            })

        edited_df = st.data_editor(
            pd.DataFrame(edit_rows),
            column_config={
                "Escalón": st.column_config.TextColumn("Escalón", disabled=True),
                "Desde kWh": st.column_config.NumberColumn("Desde kWh", disabled=True),
                "Hasta kWh": st.column_config.NumberColumn("Hasta kWh", disabled=True),
                "Cargo Fijo ($/mes)": st.column_config.NumberColumn(
                    "Cargo Fijo ($/mes)", format="%.2f", min_value=0.0,
                ),
                "Cargo Variable ($/kWh)": st.column_config.NumberColumn(
                    "Cargo Variable ($/kWh)", format="%.4f", min_value=0.0,
                ),
            },
            hide_index=True,
            use_container_width=True,
            key=f"editor_{cod}",
        )
        edited_tarifas[cod] = edited_df

    # CTT info
    st.subheader("CTT (Compensación Tarifaria Transitoria)")
    st.caption("Valores de la Res 2019-189 (cargados manualmente, fuente separada)")
    ctt_rows = [{"Tarifa": k, "CTT $/kWh": fmt(v)} for k, v in CTT_POR_KWH.items()]
    st.dataframe(pd.DataFrame(ctt_rows), hide_index=True, use_container_width=True)

    # Confirmar
    st.divider()
    if st.button(":white_check_mark: Confirmar y aplicar cuadro tarifario", type="primary",
                 use_container_width=True):
        # Aplicar valores editados al session state
        for cod, edited_df in edited_tarifas.items():
            escalones = data['tarifas'][cod]['escalones']
            for i, row in edited_df.iterrows():
                escalones[i]['cargo_fijo'] = row['Cargo Fijo ($/mes)']
                escalones[i]['cargo_variable'] = row['Cargo Variable ($/kWh)']
        st.session_state.datos_validados = True
        st.session_state.resultados_facturacion = None
        st.success("Cuadro tarifario validado y aplicado.")

    render_navegacion(st.session_state.datos_validados)


# ============================================
# PASO 3: PADRÓN DE SOCIOS
# ============================================

def render_paso_3():
    st.header("Paso 3: Padrón de Socios")

    if not st.session_state.datos_validados:
        st.warning("Primero debe validar el cuadro tarifario en el Paso 2.")
        render_navegacion(False)
        return

    st.markdown("Socios cargados para el período de facturación. "
                "En producción, estos datos vienen del sistema de lecturas (SgiMovil).")

    tarifas = st.session_state.datos_oceba['tarifas']

    rows = []
    for cid, c in CLIENTES.items():
        escalon = obtener_escalon(c['tarifa'], c['consumo_kwh'], tarifas) if c['tarifa'] in tarifas else None
        rows.append({
            "Socio": cid,
            "Nombre": c['nombre'],
            "Tarifa": c['tarifa'],
            "Segm.": c['segmentacion'],
            "Cond. IVA": c['condicion_iva'],
            "Consumo kWh": c['consumo_kwh'],
            "Escalón": escalon['nombre'] if escalon else "N/A",
            "Medidor": c['medidor'],
        })

    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # Resumen
    c1, c2, c3, c4 = st.columns(4)
    total_socios = len(CLIENTES)
    t1r_count = sum(1 for c in CLIENTES.values() if c['tarifa'] == 'T1R')
    t1re_count = sum(1 for c in CLIENTES.values() if c['tarifa'] == 'T1RE')
    avg_kwh = sum(c['consumo_kwh'] for c in CLIENTES.values()) / total_socios

    c1.metric("Total Socios", total_socios)
    c2.metric("T1R", t1r_count)
    c3.metric("T1RE", t1re_count)
    c4.metric("Consumo Promedio", f"{avg_kwh:.0f} kWh")

    st.caption("En producción: ~10.000 servicios en 29-30 rutas de lectura.")

    render_navegacion(True)


# ============================================
# PASO 4: FACTURACIÓN
# ============================================

def render_paso_4():
    st.header("Paso 4: Facturación")

    if not st.session_state.datos_validados:
        st.warning("Debe completar los pasos anteriores primero.")
        render_navegacion(False)
        return

    tarifas = st.session_state.datos_oceba['tarifas']

    # Calcular si aún no se hizo
    if st.session_state.resultados_facturacion is None:
        if st.button("Generar Facturación", type="primary", use_container_width=True):
            resultados = {}
            progress = st.progress(0, text="Calculando facturas...")
            clientes_list = list(CLIENTES.items())
            for i, (cid, c) in enumerate(clientes_list):
                if c['tarifa'] in tarifas:
                    f = calcular_factura(
                        tarifa=c['tarifa'],
                        kwh=c['consumo_kwh'],
                        iva_rate=c['iva'],
                        tarifas=tarifas,
                        zona_alumbrado=c['zona_alumbrado'],
                    )
                    resultados[cid] = f
                progress.progress((i + 1) / len(clientes_list),
                                  text=f"Calculando {c['nombre']}...")
                time.sleep(0.3)  # efecto demo
            progress.empty()
            st.session_state.resultados_facturacion = resultados
            st.rerun()
        return

    resultados = st.session_state.resultados_facturacion

    # Métricas resumen
    total_facturado = sum(r['resumen']['total'] for r in resultados.values())
    total_otros = sum(r['resumen']['otros_conceptos'] for r in resultados.values())
    total_general = sum(r['resumen']['total_general'] for r in resultados.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Socios Facturados", len(resultados))
    c2.metric("Total Liq. Serv. Púb.", fmt(total_facturado))
    c3.metric("Total Otros Conceptos", fmt(total_otros))
    c4.metric("Total General", fmt(total_general))

    # Tabs para distintas vistas
    tab_resumen, tab_detalle, tab_simulador, tab_comparador = st.tabs([
        "Resumen", "Detalle por Socio", "Simulador", "Comparador"
    ])

    with tab_resumen:
        _render_resumen(resultados, tarifas)
    with tab_detalle:
        _render_detalle(resultados, tarifas)
    with tab_simulador:
        _render_simulador(tarifas)
    with tab_comparador:
        _render_comparador(tarifas)

    # Navegación
    st.divider()
    c1, _, c3 = st.columns([1, 2, 1])
    c1.button(":arrow_left: Anterior", on_click=ir_a_paso, args=(3,), use_container_width=True)
    if c3.button(":arrows_counterclockwise: Recalcular", use_container_width=True):
        st.session_state.resultados_facturacion = None
        st.rerun()


def _render_resumen(resultados: dict, tarifas: dict):
    """Resumen de facturación batch."""
    st.subheader("Resumen de Facturación")

    rows = []
    for cid, r in resultados.items():
        c = CLIENTES[cid]
        rows.append({
            "Socio": cid,
            "Nombre": c['nombre'],
            "Tarifa": c['tarifa'],
            "kWh": c['consumo_kwh'],
            "Escalón": r['escalon']['nombre'],
            "Subtotal Energía": r['resumen']['subtotal_energia'],
            "Leyes + IVA": r['resumen']['subtotal_leyes'],
            "Alumbrado": r['resumen']['alumbrado'],
            "Total": r['resumen']['total'],
            "Otros": r['resumen']['otros_conceptos'],
            "Total General": r['resumen']['total_general'],
        })

    df = pd.DataFrame(rows)

    currency_cols = ["Subtotal Energía", "Leyes + IVA", "Alumbrado", "Total", "Otros", "Total General"]
    df_display = df.copy()
    for col in currency_cols:
        df_display[col] = df_display[col].apply(fmt)

    st.dataframe(df_display, hide_index=True, use_container_width=True)

    # Gráficos
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Total por Socio")
        fig = px.bar(
            df, x="Nombre", y="Total", color="Tarifa",
            text_auto='.2s',
            color_discrete_map={"T1R": "#3498db", "T1RE": "#e74c3c"},
        )
        fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",.0f", height=350,
                          showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Composición Promedio")
        avg_energia = df["Subtotal Energía"].mean()
        avg_leyes = df["Leyes + IVA"].mean()
        avg_alumbrado = df["Alumbrado"].mean()

        fig = go.Figure(data=[go.Pie(
            labels=["Energía", "Leyes (inc. IVA)", "Alumbrado"],
            values=[avg_energia, avg_leyes, avg_alumbrado],
            hole=0.4,
            marker_colors=["#27ae60", "#3498db", "#9b59b6"],
            textinfo="label+percent",
        )])
        fig.update_layout(height=350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)


def _render_detalle(resultados: dict, tarifas: dict):
    """Detalle de factura individual."""
    st.subheader("Detalle de Factura")

    cid = st.selectbox(
        "Seleccione socio",
        options=list(resultados.keys()),
        format_func=lambda x: f"Socio {x} - {CLIENTES[x]['nombre']} ({CLIENTES[x]['tarifa']})"
    )

    c = CLIENTES[cid]
    f = resultados[cid]

    st.info(f"""
    **Titular:** {c['nombre']} | **Tarifa:** {c['tarifa']} | **{c['condicion_iva']}** (IVA {c['iva']*100:.0f}%)
    **Segmentación:** {c['segmentacion']} | **Medidor:** {c['medidor']} | **Consumo:** {c['consumo_kwh']} kWh
    """)

    col_factura, col_hist = st.columns([3, 2])

    with col_factura:
        st.markdown("**Liquidación de Servicios Públicos**")
        for item in f['desglose']:
            if item['tipo'] == 'subtotal':
                st.markdown(f"**{item['concepto']}:** **{fmt(item['importe'])}**")
                st.divider()
            else:
                ca, cb = st.columns([3, 1])
                ca.write(item['concepto'])
                cb.write(fmt(item['importe']))

        st.success(f"### Total Liq. Serv. Púb.: {fmt(f['resumen']['total'])}")

        with st.expander("Otros Conceptos (punto de venta adicional)"):
            for item in f['otros_conceptos']:
                ca, cb = st.columns([3, 1])
                if item['concepto'] == 'TOTAL':
                    ca.markdown(f"**{item['concepto']}**")
                    cb.markdown(f"**{fmt(item['importe'])}**")
                else:
                    ca.write(item['concepto'])
                    cb.write(fmt(item['importe']))

        st.caption(f"**Escalón:** {f['escalon']['nombre']} "
                   f"({f['escalon']['desde']}-{f['escalon']['hasta'] if f['escalon']['hasta'] < 99999 else '+'} kWh)")

    with col_hist:
        st.markdown("**Historial de Consumo**")
        if c['historial']:
            df_h = pd.DataFrame(c['historial'])
            fig = px.bar(df_h, x="periodo", y="kwh", text="kwh",
                         color_discrete_sequence=["#3498db"])
            fig.update_layout(height=250, showlegend=False,
                              xaxis_title="", yaxis_title="kWh")
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            consumos = [h['kwh'] for h in c['historial']]
            mc1, mc2 = st.columns(2)
            mc1.metric("Promedio", f"{sum(consumos)/len(consumos):.0f} kWh")
            mc2.metric("Máximo", f"{max(consumos)} kWh")


def _render_simulador(tarifas: dict):
    """Simulador de consumo."""
    st.subheader("Simulador de Consumo")
    st.write("Visualice cómo varía la factura según el consumo.")

    c1, c2 = st.columns([1, 2])

    with c1:
        tarifa_sim = st.selectbox(
            "Tarifa",
            options=[t for t in ["T1R", "T1RE"] if t in tarifas],
            format_func=lambda x: f"{x} - {tarifas[x]['nombre']}",
            key="sim_tarifa",
        )
        iva_sim = st.selectbox(
            "Condición IVA",
            options=[0.27, 0.21],
            format_func=lambda x: f"Monotributista ({x*100:.0f}%)" if x == 0.27 else f"Consumidor Final ({x*100:.0f}%)",
            key="sim_iva",
        )
        rango = st.slider("Rango de consumo (kWh)", 0, 1000, (50, 500), 25, key="sim_rango")

        st.markdown("**Escalones**")
        for e in tarifas[tarifa_sim]['escalones']:
            hasta = f"{e['hasta']}" if e['hasta'] < 99999 else "+"
            st.caption(f"**{e['nombre']}** ({e['desde']}-{hasta}): "
                       f"CF={fmt(e['cargo_fijo'])}, CV={fmt(e['cargo_variable'])}/kWh")

    with c2:
        consumos = list(range(rango[0], rango[1] + 1, 25))
        totales = []
        for c in consumos:
            f = calcular_factura(tarifa_sim, c, iva_sim, tarifas)
            totales.append(f['resumen']['total'])

        df_sim = pd.DataFrame({"Consumo (kWh)": consumos, "Total Factura": totales})

        fig = px.line(df_sim, x="Consumo (kWh)", y="Total Factura",
                      title=f"Proyección de Factura - {tarifas[tarifa_sim]['nombre']}",
                      markers=True)
        fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",.0f", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Referencia rápida**")
        refs = [100, 200, 300, 400, 500]
        ref_data = []
        for c in refs:
            f = calcular_factura(tarifa_sim, c, iva_sim, tarifas)
            ref_data.append({
                "Consumo": f"{c} kWh",
                "Total": fmt(f['resumen']['total']),
                "$/kWh prom.": fmt(f['resumen']['total'] / c) if c > 0 else "-",
            })
        st.dataframe(pd.DataFrame(ref_data), hide_index=True, use_container_width=True)


def _render_comparador(tarifas: dict):
    """Comparador de tarifas T1R vs T1RE."""
    st.subheader("Comparador de Tarifas")

    available = [t for t in ["T1R", "T1RE"] if t in tarifas]
    if len(available) < 2:
        st.info("Se necesitan al menos 2 tarifas para comparar.")
        return

    consumo_comp = st.slider("Consumo a comparar (kWh)", 50, 800, 200, 25, key="comp_consumo")

    comparacion = []
    for tarifa_key in available:
        iva = 0.27 if tarifa_key == "T1R" else 0.21
        f = calcular_factura(tarifa_key, consumo_comp, iva, tarifas)
        e = f['escalon']
        comparacion.append({
            "Tarifa": tarifas[tarifa_key]['nombre'],
            "Código": tarifa_key,
            "IVA": f"{iva*100:.0f}%",
            "Cargo Fijo": e['cargo_fijo'],
            "Precio kWh": e['cargo_variable'],
            "Subtotal Energía": f['resumen']['subtotal_energia'],
            "Total": f['resumen']['total'],
        })

    c1, c2 = st.columns(2)

    with c1:
        for row in comparacion:
            with st.container(border=True):
                st.markdown(f"### {row['Código']}")
                st.markdown(f"""
                - **IVA:** {row['IVA']}
                - **Cargo Fijo:** {fmt(row['Cargo Fijo'])}
                - **Precio kWh:** {fmt(row['Precio kWh'])}
                - **Subtotal Energía:** {fmt(row['Subtotal Energía'])}
                - **TOTAL:** **{fmt(row['Total'])}**
                """)

        dif = abs(comparacion[0]['Total'] - comparacion[1]['Total'])
        mas_barata = comparacion[0]['Código'] if comparacion[0]['Total'] < comparacion[1]['Total'] else comparacion[1]['Código']
        st.success(f"Para {consumo_comp} kWh, **{mas_barata}** es más económica por **{fmt(dif)}**")

    with c2:
        df_comp = pd.DataFrame(comparacion)
        fig = px.bar(df_comp, x="Código", y="Total", color="Código",
                     title=f"Total a pagar por {consumo_comp} kWh",
                     text_auto='.2s',
                     color_discrete_map={"T1R": "#3498db", "T1RE": "#e74c3c"})
        fig.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                          height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Comparación por rango
        consumos_rango = list(range(50, 701, 50))
        data_rango = []
        for c in consumos_rango:
            for t in available:
                iva = 0.27 if t == "T1R" else 0.21
                f = calcular_factura(t, c, iva, tarifas)
                data_rango.append({"Consumo": c, "Tarifa": t, "Total": f['resumen']['total']})

        fig2 = px.line(pd.DataFrame(data_rango), x="Consumo", y="Total",
                       color="Tarifa", markers=True,
                       color_discrete_map={"T1R": "#3498db", "T1RE": "#e74c3c"})
        fig2.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",.0f",
                           height=300, xaxis_title="Consumo (kWh)", yaxis_title="Total ($)")
        st.plotly_chart(fig2, use_container_width=True)


# ============================================
# APLICACIÓN PRINCIPAL
# ============================================

st.set_page_config(
    page_title="COEMA - Motor de Facturación",
    page_icon="⚡",
    layout="wide",
)

init_state()

# Header
st.title("⚡ COEMA - Motor de Facturación Eléctrica")
st.caption("Cooperativa de Provisión de Energía Eléctrica y Otros Servicios de Madariaga Ltda.")

# Indicador de pasos
render_stepper(st.session_state.paso)
st.divider()

# Contenido según paso actual
if st.session_state.paso == 1:
    render_paso_1()
elif st.session_state.paso == 2:
    render_paso_2()
elif st.session_state.paso == 3:
    render_paso_3()
elif st.session_state.paso == 4:
    render_paso_4()

# Sidebar
render_sidebar()

# Footer
st.divider()
st.caption("""
**COEMA** - Cooperativa de Provisión de Energía Eléctrica y Otros Servicios de Madariaga Ltda.
Zubiaurre 248 - CP 7163 - Gral. Madariaga | Tel: 02267-424347

*Motor de Facturación - Demo v2.0*
""")
