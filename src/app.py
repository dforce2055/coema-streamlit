"""
COEMA - Sistema de Facturación Eléctrica
MVP Demo - Streamlit
Datos basados en facturas reales Nov-Dic 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict

# ============================================
# CONFIGURACIÓN Y DATOS REALES
# ============================================

# Resoluciones tarifarias vigentes (extraídas de facturas reales)
RESOLUCIONES = {
    "Res.1176/25 Anexo 6": {
        "vigencia_desde": "2025-12-01",
        "vigencia_hasta": "2025-12-31",
        "tarifas": {
            "T1R": {  # Monotributista - IVA 27%
                "nombre": "Tarifa 1 Residencial",
                "descripcion": "Monotributista - IVA 27%",
                "iva": 0.27,
                "escalones": [
                    {"num": 1, "desde": 0, "hasta": 150, "cargo_fijo": 5200.00, "precio_kwh": 158.50},
                    {"num": 2, "desde": 150, "hasta": 200, "cargo_fijo": 6100.00, "precio_kwh": 162.80},
                    {"num": 3, "desde": 200, "hasta": 400, "cargo_fijo": 6895.82, "precio_kwh": 165.4024},
                    {"num": 4, "desde": 400, "hasta": 500, "cargo_fijo": 8846.72, "precio_kwh": 173.6190},
                    {"num": 5, "desde": 500, "hasta": 600, "cargo_fijo": 10500.00, "precio_kwh": 182.50},
                    {"num": 6, "desde": 600, "hasta": 99999, "cargo_fijo": 12500.00, "precio_kwh": 195.80},
                ],
                "ctt_por_kwh": 9.8780,  # CTT Art 5º Res 2019-189 (Dic 2025)
            },
            "T1RE": {  # Consumidor Final - IVA 21%
                "nombre": "Tarifa 1 Residencial Exento",
                "descripcion": "Consumidor Final - IVA 21%",
                "iva": 0.21,
                "escalones": [
                    {"num": 1, "desde": 0, "hasta": 500, "cargo_fijo": 11911.11, "precio_kwh": 206.6378},
                    {"num": 2, "desde": 500, "hasta": 99999, "cargo_fijo": 15000.00, "precio_kwh": 225.00},
                ],
                "ctt_por_kwh": 4.2020,  # CTT menor para T1RE
            },
        },
    },
}

# Impuestos y contribuciones (valores reales de facturas)
# Base de cálculo: Subtotal Energía
IMPUESTOS = {
    "ley_7290": {
        "nombre": "Ley Provincial 7290",
        "porcentaje": 0.04,  # 4%
    },
    "ley_11769_art75": {
        "nombre": "Ley 11769 Art 75 (6%- Ex.9226)",
        "porcentaje": 0.06,  # 6%
    },
    "ley_11769_art72bis": {
        "nombre": "Ley 11769 art.72 Bis (0,001%)",
        "porcentaje": 0.00001,  # 0.001%
    },
    "ley_11769_fondo": {
        "nombre": "Ley 11769 Fondo Compensador",
        "porcentaje": 0.055,  # 5.5%
    },
}

# Otros cargos (mostrados aparte, NO incluidos en Total Liq. Serv. Públicos)
OTROS_CONCEPTOS = {
    "res_asamblea": {
        "nombre": "Res. Asam 21/10/15",
        "porcentaje": 0.1346,  # ~13.46% del subtotal energía
    },
    "bomberos": {
        "nombre": "Bomberos",
        "valor_fijo": 960.00,
    },
}

# Alumbrado público por zona
ALUMBRADO_PUBLICO = {
    1: {"nombre": "Zona 1", "valor_nov": 9284.00, "valor_dic": 14000.00},
}

# Clientes de ejemplo (datos reales de las facturas)
CLIENTES = {
    "10140": {
        "nombre": "PEREZ DIEGO OBDULIO FABIAN",
        "direccion": "URRUTIA N° 452 Dto 01",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1R",
        "condicion_iva": "Monotributista",
        "cuit": "20-32465169-2",
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "19740904",
        "servicio": "101400007",
        "historial": [
            {"periodo": "2025-07", "kwh": 280, "total": 78500.00},
            {"periodo": "2025-08", "kwh": 310, "total": 85200.00},
            {"periodo": "2025-09", "kwh": 295, "total": 82100.00},
            {"periodo": "2025-10", "kwh": 320, "total": 88900.00},
            {"periodo": "2025-11", "kwh": 296, "total": 90713.36},
            {"periodo": "2025-12", "kwh": 422, "total": 137909.74},
        ],
    },
    "1564": {
        "nombre": "CRINIGAN MARIA CRISTINA",
        "direccion": "ZUBIAURRE N° 209",
        "localidad": "GENERAL MADARIAGA",
        "tarifa": "T1RE",
        "condicion_iva": "Consumidor Final",
        "dni": "3324947",
        "segmentacion": "N1",
        "zona_alumbrado": 1,
        "medidor": "31532773",
        "servicio": "15640027",
        "historial": [
            {"periodo": "2025-07", "kwh": 65, "total": 42300.00},
            {"periodo": "2025-08", "kwh": 72, "total": 45800.00},
            {"periodo": "2025-09", "kwh": 58, "total": 39500.00},
            {"periodo": "2025-10", "kwh": 61, "total": 41200.00},
            {"periodo": "2025-11", "kwh": 44, "total": 37642.79},
            {"periodo": "2025-12", "kwh": 170, "total": 79270.15},
        ],
    },
}


# ============================================
# FUNCIONES DE CÁLCULO
# ============================================

def obtener_escalon(tarifa: str, kwh: int, resolucion: str = "Res.1176/25 Anexo 6") -> Dict:
    """Obtiene el escalón correspondiente según el consumo."""
    escalones = RESOLUCIONES[resolucion]["tarifas"][tarifa]["escalones"]
    for escalon in escalones:
        if escalon["desde"] <= kwh < escalon["hasta"]:
            return escalon
    return escalones[-1]


def calcular_factura(
    tarifa: str,
    kwh: int,
    zona_alumbrado: int = 1,
    periodo: str = "2025-12",
    resolucion: str = "Res.1176/25 Anexo 6"
) -> Dict:
    """
    Calcula todos los componentes de una factura eléctrica.
    Fórmula real basada en facturas de COEMA:

    Total = Subtotal Energía + Subtotal Leyes + Alumbrado

    Donde Subtotal Leyes = IVA + Ley 7290 + Ley 11769 (Art75 + Art72bis + Fondo)
    """
    config_tarifa = RESOLUCIONES[resolucion]["tarifas"][tarifa]
    escalon = obtener_escalon(tarifa, kwh, resolucion)

    # ===== COMPONENTES DE ENERGÍA =====
    cargo_fijo = escalon["cargo_fijo"]
    cargo_variable = kwh * escalon["precio_kwh"]
    ctt = kwh * config_tarifa["ctt_por_kwh"]

    subtotal_energia = cargo_fijo + cargo_variable + ctt

    # ===== IVA (sobre subtotal energía) =====
    iva = subtotal_energia * config_tarifa["iva"]

    # ===== LEYES (sobre subtotal energía) =====
    ley_7290 = subtotal_energia * IMPUESTOS["ley_7290"]["porcentaje"]
    ley_11769_art75 = subtotal_energia * IMPUESTOS["ley_11769_art75"]["porcentaje"]
    ley_11769_art72bis = subtotal_energia * IMPUESTOS["ley_11769_art72bis"]["porcentaje"]
    ley_11769_fondo = subtotal_energia * IMPUESTOS["ley_11769_fondo"]["porcentaje"]

    # Subtotal Leyes incluye IVA + todas las leyes
    subtotal_leyes = iva + ley_7290 + ley_11769_art75 + ley_11769_art72bis + ley_11769_fondo

    # ===== ALUMBRADO PÚBLICO =====
    alumbrado_key = "valor_dic" if "12" in periodo else "valor_nov"
    alumbrado = ALUMBRADO_PUBLICO[zona_alumbrado][alumbrado_key]

    # ===== TOTAL LIQUIDACIÓN SERVICIOS PÚBLICOS =====
    total = subtotal_energia + subtotal_leyes + alumbrado

    # ===== OTROS CONCEPTOS (mostrados aparte) =====
    res_asamblea = subtotal_energia * OTROS_CONCEPTOS["res_asamblea"]["porcentaje"]
    bomberos = OTROS_CONCEPTOS["bomberos"]["valor_fijo"]
    total_otros_conceptos = res_asamblea + bomberos

    return {
        "desglose": [
            {"concepto": f"Cargo Fijo {tarifa}", "importe": cargo_fijo, "tipo": "energia"},
            {"concepto": f"Cargo Variable {tarifa}", "importe": cargo_variable, "tipo": "energia"},
            {"concepto": f"CTT Art 5º Resol 2019-189 ({kwh}x{config_tarifa['ctt_por_kwh']:.4f})", "importe": ctt, "tipo": "energia"},
            {"concepto": "Subtotal Energía", "importe": subtotal_energia, "tipo": "subtotal"},
            {"concepto": f"{'Monotributo IVA' if config_tarifa['iva'] == 0.27 else 'I.V.A.'} {config_tarifa['iva']*100:.0f}%", "importe": iva, "tipo": "ley"},
            {"concepto": "Ley Provincial 7290", "importe": ley_7290, "tipo": "ley"},
            {"concepto": "Ley 11769 Art 75 (6%- Ex.9226)", "importe": ley_11769_art75, "tipo": "ley"},
            {"concepto": "Ley 11769 art.72 Bis (0,001%)", "importe": ley_11769_art72bis, "tipo": "ley"},
            {"concepto": "Ley 11769 Fondo Compensador", "importe": ley_11769_fondo, "tipo": "ley"},
            {"concepto": "Subtotal Leyes", "importe": subtotal_leyes, "tipo": "subtotal"},
            {"concepto": "Alumbrado Público ord 2945/23", "importe": alumbrado, "tipo": "otro"},
            {"concepto": "Subtotal Otros Conceptos", "importe": alumbrado, "tipo": "subtotal"},
        ],
        "otros_conceptos": [
            {"concepto": "Res. Asam 21/10/15", "importe": res_asamblea},
            {"concepto": "Bomberos", "importe": bomberos},
            {"concepto": "TOTAL", "importe": total_otros_conceptos},
        ],
        "resumen": {
            "subtotal_energia": subtotal_energia,
            "iva": iva,
            "subtotal_leyes": subtotal_leyes,
            "alumbrado": alumbrado,
            "total": total,
            "otros_conceptos": total_otros_conceptos,
        },
        "escalon": escalon,
        "tarifa_config": config_tarifa,
    }


def formatear_moneda(valor: float) -> str:
    """Formatea un valor como moneda argentina."""
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================
# INTERFAZ STREAMLIT
# ============================================

st.set_page_config(
    page_title="COEMA - Facturación",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ COEMA - Sistema de Facturación Eléctrica")
st.caption("Cooperativa de Provisión de Energía Eléctrica y Otros Servicios de Madariaga Ltda.")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "Calculadora de Factura",
    "Simulador de Consumo",
    "Historial de Cliente",
    "Comparador de Tarifas"
])

# ============================================
# TAB 1: CALCULADORA DE FACTURA
# ============================================
with tab1:
    st.header("Calculadora de Factura")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Datos de entrada")

        # Selector de cliente
        cliente_id = st.selectbox(
            "Seleccione cliente",
            options=list(CLIENTES.keys()),
            format_func=lambda x: f"Socio {x} - {CLIENTES[x]['nombre']} ({CLIENTES[x]['tarifa']})"
        )

        cliente = CLIENTES[cliente_id]
        tarifa_info = RESOLUCIONES["Res.1176/25 Anexo 6"]["tarifas"][cliente["tarifa"]]

        # Info del cliente
        st.info(f"""
        **Titular:** {cliente['nombre']}
        **Dirección:** {cliente['direccion']}
        **Tarifa:** {tarifa_info['nombre']}
        **Condición IVA:** {cliente['condicion_iva']} ({tarifa_info['iva']*100:.0f}%)
        **Segmentación:** {cliente['segmentacion']}
        **Medidor:** {cliente['medidor']}
        """)

        # Input de consumo
        ultimo_consumo = cliente["historial"][-1]["kwh"] if cliente["historial"] else 200
        consumo_kwh = st.number_input(
            "Consumo (kWh)",
            min_value=0,
            max_value=2000,
            value=ultimo_consumo,
            step=10,
            help="Ingrese el consumo en kilovatios-hora"
        )

        periodo = st.selectbox(
            "Período",
            options=["2025-12", "2025-11"],
            format_func=lambda x: "DICIEMBRE/2025" if x == "2025-12" else "NOVIEMBRE/2025"
        )

        calcular = st.button("Calcular Factura", type="primary", use_container_width=True)

    with col2:
        if calcular or consumo_kwh > 0:
            factura = calcular_factura(
                tarifa=cliente["tarifa"],
                kwh=consumo_kwh,
                zona_alumbrado=cliente["zona_alumbrado"],
                periodo=periodo,
            )

            st.subheader(f"Liquidación de Servicios Públicos - {periodo}")

            # Mostrar desglose
            for item in factura["desglose"]:
                if item["tipo"] == "subtotal":
                    st.markdown(f"**{item['concepto']}:** **{formatear_moneda(item['importe'])}**")
                    st.divider()
                else:
                    col_a, col_b = st.columns([3, 1])
                    col_a.write(item["concepto"])
                    col_b.write(formatear_moneda(item["importe"]))

            # Total destacado
            st.success(f"### Total Liq. Serv. Públicos: {formatear_moneda(factura['resumen']['total'])}")

            # Otros conceptos (en caja aparte)
            with st.expander("Otros Conceptos (adicionales)"):
                for item in factura["otros_conceptos"]:
                    col_a, col_b = st.columns([3, 1])
                    if item["concepto"] == "TOTAL":
                        col_a.markdown(f"**{item['concepto']}**")
                        col_b.markdown(f"**{formatear_moneda(item['importe'])}**")
                    else:
                        col_a.write(item["concepto"])
                        col_b.write(formatear_moneda(item["importe"]))

            # Info del escalón
            st.caption(f"""
            **Escalón aplicado:** {factura['escalon']['num']} ({factura['escalon']['desde']}-{factura['escalon']['hasta']} kWh) |
            **Cargo Fijo:** {formatear_moneda(factura['escalon']['cargo_fijo'])} |
            **Precio kWh:** {formatear_moneda(factura['escalon']['precio_kwh'])}
            """)

            # Gráfico de composición
            st.subheader("Composición de la Factura")

            fig = go.Figure(data=[go.Pie(
                labels=["Energía", "Leyes (inc. IVA)", "Alumbrado"],
                values=[
                    factura["resumen"]["subtotal_energia"],
                    factura["resumen"]["subtotal_leyes"],
                    factura["resumen"]["alumbrado"],
                ],
                hole=0.4,
                marker_colors=["#27ae60", "#3498db", "#9b59b6"],
                textinfo="label+percent",
            )])
            fig.update_layout(height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# TAB 2: SIMULADOR DE CONSUMO
# ============================================
with tab2:
    st.header("Simulador de Consumo")
    st.write("Visualice cómo varía el monto de su factura según el consumo")

    col1, col2 = st.columns([1, 2])

    with col1:
        tarifa_sim = st.selectbox(
            "Seleccione tarifa",
            options=["T1R", "T1RE"],
            format_func=lambda x: f"{x} - {RESOLUCIONES['Res.1176/25 Anexo 6']['tarifas'][x]['nombre']}"
        )

        rango = st.slider(
            "Rango de consumo a simular (kWh)",
            min_value=0,
            max_value=800,
            value=(50, 500),
            step=25
        )

        st.subheader("Escalones de Tarifa")
        tarifa_data = RESOLUCIONES["Res.1176/25 Anexo 6"]["tarifas"][tarifa_sim]
        for esc in tarifa_data["escalones"]:
            if esc["hasta"] < 99999:
                st.caption(f"**Esc. {esc['num']}** ({esc['desde']}-{esc['hasta']} kWh): CF={formatear_moneda(esc['cargo_fijo'])}, CV={formatear_moneda(esc['precio_kwh'])}/kWh")

    with col2:
        # Generar datos de simulación
        consumos = list(range(rango[0], rango[1] + 1, 25))
        totales = []

        for c in consumos:
            f = calcular_factura(tarifa=tarifa_sim, kwh=c, periodo="2025-12")
            totales.append(f["resumen"]["total"])

        df_sim = pd.DataFrame({
            "Consumo (kWh)": consumos,
            "Total Factura": totales,
        })

        # Gráfico de línea
        fig = px.line(
            df_sim,
            x="Consumo (kWh)",
            y="Total Factura",
            title=f"Proyección de Factura - {tarifa_data['nombre']}",
            markers=True,
        )
        fig.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabla de referencia rápida
        st.subheader("Referencia rápida")
        consumos_ref = [100, 200, 300, 400, 500]
        data_ref = []
        for c in consumos_ref:
            f = calcular_factura(tarifa=tarifa_sim, kwh=c, periodo="2025-12")
            data_ref.append({
                "Consumo": f"{c} kWh",
                "Total": formatear_moneda(f["resumen"]["total"]),
                "$/kWh promedio": formatear_moneda(f["resumen"]["total"] / c if c > 0 else 0),
            })
        st.dataframe(pd.DataFrame(data_ref), hide_index=True, use_container_width=True)

# ============================================
# TAB 3: HISTORIAL DE CLIENTE
# ============================================
with tab3:
    st.header("Historial de Cliente")

    cliente_hist_id = st.selectbox(
        "Seleccione cliente para ver historial",
        options=list(CLIENTES.keys()),
        format_func=lambda x: f"Socio {x} - {CLIENTES[x]['nombre']}",
        key="hist_cliente"
    )

    cliente_hist = CLIENTES[cliente_hist_id]

    # Info del cliente
    st.markdown(f"""
    **Titular:** {cliente_hist['nombre']} | **Tarifa:** {cliente_hist['tarifa']} | **Condición:** {cliente_hist['condicion_iva']}
    """)

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de consumo histórico
        df_hist = pd.DataFrame(cliente_hist["historial"])

        fig_consumo = px.bar(
            df_hist,
            x="periodo",
            y="kwh",
            title="Consumo Histórico (kWh)",
            color="kwh",
            color_continuous_scale="Blues",
            text="kwh",
        )
        fig_consumo.update_layout(height=350, showlegend=False)
        fig_consumo.update_traces(textposition="outside")
        st.plotly_chart(fig_consumo, use_container_width=True)

    with col2:
        # Gráfico de facturación histórica
        fig_factura = px.line(
            df_hist,
            x="periodo",
            y="total",
            title="Evolución de Facturación ($)",
            markers=True,
        )
        fig_factura.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=350
        )
        st.plotly_chart(fig_factura, use_container_width=True)

    # Estadísticas
    st.subheader("Estadísticas")
    col1, col2, col3, col4 = st.columns(4)

    consumos = [h["kwh"] for h in cliente_hist["historial"]]
    totales = [h["total"] for h in cliente_hist["historial"]]

    col1.metric("Consumo Promedio", f"{sum(consumos)/len(consumos):.0f} kWh")
    col2.metric("Consumo Máximo", f"{max(consumos)} kWh", f"+{max(consumos) - sum(consumos)//len(consumos)} vs prom.")
    col3.metric("Factura Promedio", formatear_moneda(sum(totales)/len(totales)))
    col4.metric(
        "Última Factura",
        formatear_moneda(totales[-1]),
        f"{((totales[-1] - totales[-2]) / totales[-2] * 100):+.1f}%" if len(totales) > 1 else None
    )

    # Tabla detallada
    st.subheader("Detalle por Período")
    df_detalle = pd.DataFrame(cliente_hist["historial"])
    df_detalle["total_fmt"] = df_detalle["total"].apply(formatear_moneda)
    df_detalle["costo_kwh"] = (df_detalle["total"] / df_detalle["kwh"]).apply(lambda x: formatear_moneda(x))
    df_detalle = df_detalle.rename(columns={
        "periodo": "Período",
        "kwh": "Consumo (kWh)",
        "total_fmt": "Total Factura",
        "costo_kwh": "$/kWh"
    })
    st.dataframe(df_detalle[["Período", "Consumo (kWh)", "Total Factura", "$/kWh"]], hide_index=True, use_container_width=True)

# ============================================
# TAB 4: COMPARADOR DE TARIFAS
# ============================================
with tab4:
    st.header("Comparador de Tarifas")
    st.write("Compare el costo para un mismo consumo entre T1R (Monotributista) y T1RE (Consumidor Final)")

    consumo_comp = st.slider(
        "Consumo a comparar (kWh)",
        min_value=50,
        max_value=600,
        value=200,
        step=25,
    )

    # Calcular para ambas tarifas
    comparacion = []
    for tarifa_key in ["T1R", "T1RE"]:
        tarifa_data = RESOLUCIONES["Res.1176/25 Anexo 6"]["tarifas"][tarifa_key]
        factura = calcular_factura(tarifa=tarifa_key, kwh=consumo_comp, periodo="2025-12")
        escalon = factura["escalon"]
        comparacion.append({
            "Tarifa": tarifa_data["nombre"],
            "Código": tarifa_key,
            "Condición IVA": tarifa_data["descripcion"].split(" - ")[0],
            "IVA": f"{tarifa_data['iva']*100:.0f}%",
            "Cargo Fijo": escalon["cargo_fijo"],
            "Precio kWh": escalon["precio_kwh"],
            "Subtotal Energía": factura["resumen"]["subtotal_energia"],
            "Total": factura["resumen"]["total"],
        })

    df_comp = pd.DataFrame(comparacion)

    # Mostrar comparativa
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tabla Comparativa")

        # Mostrar cada tarifa en un card
        for i, row in df_comp.iterrows():
            with st.container():
                st.markdown(f"### {row['Código']} - {row['Condición IVA']}")
                st.markdown(f"""
                - **IVA:** {row['IVA']}
                - **Cargo Fijo:** {formatear_moneda(row['Cargo Fijo'])}
                - **Precio kWh:** {formatear_moneda(row['Precio kWh'])}
                - **Subtotal Energía:** {formatear_moneda(row['Subtotal Energía'])}
                - **TOTAL:** **{formatear_moneda(row['Total'])}**
                """)
                st.divider()

        diferencia = abs(comparacion[0]["Total"] - comparacion[1]["Total"])
        mas_barata = "T1R" if comparacion[0]["Total"] < comparacion[1]["Total"] else "T1RE"
        st.success(f"Para {consumo_comp} kWh, **{mas_barata}** es más económica por **{formatear_moneda(diferencia)}**")

    with col2:
        st.subheader("Comparación Visual")
        fig = px.bar(
            df_comp,
            x="Código",
            y="Total",
            color="Código",
            title=f"Total a pagar por {consumo_comp} kWh",
            text_auto='.2s',
            color_discrete_map={"T1R": "#3498db", "T1RE": "#e74c3c"}
        )
        fig.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de comparación por rango
        st.subheader("Comparación por Rango de Consumo")
        consumos_rango = list(range(50, 501, 50))
        data_rango = []
        for c in consumos_rango:
            for t in ["T1R", "T1RE"]:
                f = calcular_factura(tarifa=t, kwh=c, periodo="2025-12")
                data_rango.append({"Consumo": c, "Tarifa": t, "Total": f["resumen"]["total"]})

        df_rango = pd.DataFrame(data_rango)
        fig_rango = px.line(
            df_rango,
            x="Consumo",
            y="Total",
            color="Tarifa",
            markers=True,
            color_discrete_map={"T1R": "#3498db", "T1RE": "#e74c3c"}
        )
        fig_rango.update_layout(
            yaxis_tickprefix="$",
            yaxis_tickformat=",.0f",
            height=350,
            xaxis_title="Consumo (kWh)",
            yaxis_title="Total Factura ($)"
        )
        st.plotly_chart(fig_rango, use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.divider()
st.caption("""
**Resolución aplicada:** Res. 1176/25 Anexo 6 (Vigencia: 01/12/2025 al 31/12/2025)

**Nota:** Este es un prototipo de demostración basado en facturas reales de Nov-Dic 2025.
Los valores pueden tener pequeñas diferencias debido al prorrateo entre resoluciones.

*COEMA - Cooperativa de Provisión de Energía Eléctrica y Otros Servicios de Madariaga Ltda.*
*Zubiaurre 248 - CP 7163 - Gral. Madariaga | Tel: 02267-424347*
""")
