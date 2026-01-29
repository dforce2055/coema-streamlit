# COEMA - Sistema de Facturación Eléctrica
## Documento de Análisis y Requisitos

**Fecha:** Enero 2026  
**Cliente:** Cooperativa de Provisión de Energía Eléctrica y Otros Servicios de Madariaga Ltda.  
**Ubicación:** General Madariaga, Buenos Aires, Argentina

---

## 1. Resumen Ejecutivo

COEMA necesita modernizar su sistema de facturación eléctrica. Los problemas actuales son:
- Sistema de facturación lento e ineficiente
- Lecturas de medidores aproximadas (no reales)
- Necesidad de integración con sistemas externos vía API

**Objetivo de la Demo:** Crear un prototipo funcional que calcule facturas eléctricas basándose en el consumo en kWh y las variables tarifarias del abonado.

---

## 2. Preguntas Pendientes para COEMA

### 2.1 Sobre Tarifas y Categorías

| # | Pregunta | Impacto |
|---|----------|---------|
| 1 | ¿Cuántos tipos de tarifa existen además de T1R y T1RE? | Estructura de datos |
| 2 | ¿Qué determina si un cliente es T1R o T1RE? ¿Es solo la condición fiscal? | Reglas de negocio |
| 3 | ¿Existen tarifas comerciales, industriales, rurales? | Alcance del sistema |
| 4 | ¿Cómo se definen los escalones de consumo (0-200, 200-400, 400-500, etc.)? | Cálculo de cargo fijo |
| 5 | ¿Los escalones son iguales para todas las tarifas? | Lógica de cálculo |
| 6 | ¿Con qué frecuencia cambian los valores de tarifas (resoluciones)? | Versionado de tarifas |

### 2.2 Sobre Cargos y Componentes

| # | Pregunta | Impacto |
|---|----------|---------|
| 7 | ¿Cómo se calcula exactamente el **Cargo Fijo**? ¿Depende del escalón de consumo? | Fórmula core |
| 8 | ¿El **Cargo Variable** es siempre kWh × precio unitario? | Fórmula core |
| 9 | ¿Qué es el **CTT (Art 5º Res 2019-189)**? ¿Cómo se calcula? | Componente adicional |
| 10 | ¿Por qué PEREZ tiene CTT ~$9.93/kWh y CRINIGAN ~$4.25/kWh? | Diferencia por tarifa |
| 11 | ¿Cómo se calcula la **"Res. Asamblea 21/10/15"**? Varía mucho entre clientes | Fórmula desconocida |
| 12 | ¿El **Alumbrado Público** es fijo por zona? ¿Cuántas zonas hay? | Configuración |
| 13 | ¿El cargo de **Bomberos** es siempre $960? | Valor fijo |

### 2.3 Sobre Impuestos y Leyes

| # | Pregunta | Impacto |
|---|----------|---------|
| 14 | ¿El IVA siempre es 27% para Monotributistas y 21% para Consumidor Final? | Regla fiscal |
| 15 | ¿Existen exenciones de IVA? ¿Para quiénes? | Casos especiales |
| 16 | ¿Los porcentajes de leyes provinciales (7290, 11769) son fijos o cambian? | Configuración |
| 17 | ¿La base de cálculo de los impuestos es siempre el Subtotal Energía? | Fórmula |

### 2.4 Sobre Subsidios y Segmentación

| # | Pregunta | Impacto |
|---|----------|---------|
| 18 | ¿Qué significa "Segmentación N1"? ¿Hay otros niveles (N2, N3)? | Categorización |
| 19 | ¿Cómo se calcula el **Subsidio Estado Nacional**? | Fórmula de subsidio |
| 20 | ¿El subsidio depende del consumo, la tarifa, o ambos? | Variables del subsidio |
| 21 | ¿Qué es "Sin Ahorro" que aparece en las facturas? | Estado del cliente |

### 2.5 Sobre Clientes/Abonados

| # | Pregunta | Impacto |
|---|----------|---------|
| 22 | ¿Cuántos abonados tiene COEMA aproximadamente? | Volumen de datos |
| 23 | ¿Qué datos del cliente son necesarios para facturar? | Modelo de datos |
| 24 | ¿El número de socio y el código de servicio son lo mismo? | Identificadores |
| 25 | ¿Un cliente puede tener múltiples servicios (medidores)? | Relaciones |

### 2.6 Sobre Lecturas y Medidores

| # | Pregunta | Impacto |
|---|----------|---------|
| 26 | ¿Cada cuánto se toman las lecturas actualmente? | Frecuencia |
| 27 | ¿Qué datos se registran en cada lectura? | Campos necesarios |
| 28 | ¿Cómo manejan las lecturas "estimadas" vs "reales"? | Flag en sistema |
| 29 | ¿Qué pasa si no se puede tomar lectura un mes? | Caso excepcional |

### 2.7 Sobre el Período de Facturación

| # | Pregunta | Impacto |
|---|----------|---------|
| 30 | ¿Los períodos son siempre mensuales? | Lógica temporal |
| 31 | ¿Cómo se maneja cuando el período cruza dos resoluciones tarifarias? | Prorrateo |
| 32 | Ejemplo: Factura con 27 días de Res.1176/25 y 3 días de Res.1176/25 Anexo 72 | Complejidad |

---

## 3. Datos Necesarios para la Demo

### 3.1 Catálogo de Tarifas

```
Necesitamos:
- Lista completa de tipos de tarifa (T1R, T1RE, comercial, etc.)
- Descripción de cada tarifa
- Condiciones de aplicación
- Tipo de IVA aplicable
```

### 3.2 Valores de Tarifas Vigentes

```
Para cada tarifa y resolución:
- Código de resolución (ej: Res.1176/25 Anexo 6)
- Fecha vigencia desde
- Fecha vigencia hasta
- Escalones de consumo (kWh desde - hasta)
- Cargo fijo por escalón
- Cargo variable ($/kWh) por escalón
- Valor CTT
```

**Ejemplo de estructura esperada:**

| Resolución | Tarifa | Escalón | kWh Desde | kWh Hasta | Cargo Fijo | $/kWh |
|------------|--------|---------|-----------|-----------|------------|-------|
| Res.1176/25 Anexo 6 | T1R | 3 | 200 | 400 | 6,895.82 | 165.40 |
| Res.1176/25 Anexo 6 | T1R | 4 | 400 | 500 | 8,846.72 | 173.62 |
| Res.1176/25 Anexo 6 | T1RE | 1 | 0 | 500 | 11,911.11 | 206.64 |

### 3.3 Tabla de Impuestos y Contribuciones

```
Para cada impuesto/contribución:
- Código
- Nombre completo
- Porcentaje o valor fijo
- Base de cálculo (subtotal energía, consumo, fijo)
- Aplicable a qué tarifas
- Fecha vigencia
```

### 3.4 Datos de Clientes de Prueba

```
Mínimo 5-10 clientes con diferentes:
- Tipos de tarifa
- Condiciones fiscales
- Niveles de segmentación
- Rangos de consumo histórico
```

### 3.5 Historial de Consumos

```
Para cada cliente de prueba:
- Últimos 12 meses de consumo
- Lecturas de medidor
- Facturas emitidas (para validar cálculos)
```

---

## 4. Requisitos Funcionales de la Demo

### 4.1 Inputs Mínimos
- Identificador del servicio/abonado
- Consumo en kWh (o lectura actual si tenemos la anterior)

### 4.2 Outputs Esperados
- Desglose completo de la factura
- Subtotales por categoría (Energía, Leyes, Otros)
- Total a pagar
- Gráfico comparativo con períodos anteriores
- Comparativa con promedio de su categoría

### 4.3 Funcionalidades Deseadas
1. **Calculadora de factura** - Input: kWh → Output: Factura detallada
2. **Simulador de consumo** - "¿Cuánto pagaría si consumo X kWh?"
3. **Histórico de cliente** - Ver evolución de consumo y facturación
4. **Comparador de tarifas** - Mostrar diferencias entre T1R y T1RE

---

## 5. Evaluación de Tecnologías

### 5.1 Opción A: Directus + Frontend

**Pros:**
- API REST/GraphQL lista para usar
- Panel de administración incluido
- Sistema de permisos y roles robusto
- Webhooks y Flows para automatizaciones
- Ideal para integración con sistemas externos
- Ya conocido por el equipo

**Contras:**
- Requiere hosting (VPS o cloud)
- Más complejo para una demo simple
- Overhead si solo necesitamos cálculos

**Ideal para:** Solución productiva a largo plazo

---

### 5.2 Opción B: Streamlit (Python)

**Pros:**
- Deploy instantáneo (Streamlit Cloud gratuito)
- Excelente para demos y prototipos
- Gráficos interactivos nativos (Plotly, Altair)
- Código Python puro (fácil de mantener)
- Widgets de input listos (sliders, selectbox, etc.)
- Hot reload durante desarrollo

**Contras:**
- No tiene base de datos integrada (usar SQLite/PostgreSQL)
- No ideal para producción con muchos usuarios
- Sin sistema de autenticación robusto nativo

**Ideal para:** Demo rápida y prototipo funcional

**Ejemplo de código Streamlit:**
```python
import streamlit as st

st.title("🔌 Calculadora de Factura COEMA")

cliente = st.selectbox("Seleccione cliente", ["PEREZ - T1R", "CRINIGAN - T1RE"])
consumo = st.number_input("Consumo (kWh)", min_value=0, max_value=1000, value=422)

if st.button("Calcular Factura"):
    # Lógica de cálculo
    factura = calcular_factura(cliente, consumo)
    st.dataframe(factura)
    st.bar_chart(factura[["Concepto", "Importe"]])
```

---

### 5.3 Opción C: Gradio (Python)

**Pros:**
- Similar a Streamlit, aún más simple
- Deploy en Hugging Face Spaces (gratuito)
- Interfaces generadas automáticamente
- Bueno para demos de "input → output"

**Contras:**
- Menos flexible que Streamlit
- Menos widgets disponibles
- Comunidad más pequeña

**Ideal para:** Demos muy simples tipo calculadora

---

### 5.4 Opción D: FastAPI + React/Vue

**Pros:**
- Máxima flexibilidad
- API documentada automáticamente (OpenAPI/Swagger)
- Frontend totalmente personalizable
- Escalable a producción

**Contras:**
- Mayor tiempo de desarrollo
- Requiere conocimiento de frontend
- Más código que mantener

**Ideal para:** Solución productiva personalizada

---

### 5.5 Opción E: NiceGUI (Python)

**Pros:**
- UI moderna con Python puro
- Basado en Vue.js/Quasar
- Más componentes que Streamlit
- Mejor para aplicaciones complejas

**Contras:**
- Menos popular (comunidad pequeña)
- Documentación limitada

**Ideal para:** Apps Python más elaboradas

---

### 5.6 Matriz de Decisión

| Criterio | Peso | Directus | Streamlit | Gradio | FastAPI+React | NiceGUI |
|----------|------|----------|-----------|--------|---------------|---------|
| Velocidad de desarrollo | 25% | 3 | 5 | 5 | 2 | 4 |
| Facilidad de demo | 20% | 3 | 5 | 5 | 3 | 4 |
| Escalabilidad | 15% | 5 | 2 | 1 | 5 | 3 |
| Integración API | 15% | 5 | 3 | 2 | 5 | 3 |
| Gráficos/Visualización | 10% | 2 | 5 | 4 | 4 | 4 |
| Costo de hosting | 10% | 2 | 5 | 5 | 3 | 4 |
| Mantenibilidad | 5% | 4 | 4 | 3 | 3 | 3 |
| **TOTAL** | 100% | **3.35** | **4.25** | **3.85** | **3.35** | **3.65** |

*(Escala: 1=Malo, 5=Excelente)*

---

### 5.7 Recomendación

#### Para la DEMO inicial: **Streamlit** ⭐

**Razones:**
1. Prototipo funcional en 1-2 días
2. Deploy gratuito en Streamlit Cloud
3. Gráficos interactivos incluidos
4. Fácil de modificar según feedback
5. El cliente puede ver y probar inmediatamente

#### Para PRODUCCIÓN futura: **Directus + Streamlit** o **FastAPI + Frontend**

**Estrategia sugerida:**
1. **Fase 1 (Demo):** Streamlit con datos hardcodeados o SQLite
2. **Fase 2 (Validación):** Conectar Streamlit a Directus como backend
3. **Fase 3 (Producción):** Migrar a arquitectura completa si es necesario

---

## 6. Arquitectura Propuesta para Demo

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT APP                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Input      │  │  Cálculo    │  │  Output     │     │
│  │  - Cliente  │─▶│  - Tarifas  │─▶│  - Factura  │     │
│  │  - kWh      │  │  - Impuestos│  │  - Gráficos │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│                    DATOS (JSON/SQLite)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Clientes   │  │  Tarifas    │  │  Impuestos  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 7. Próximos Pasos

1. [ ] Enviar cuestionario a COEMA (sección 2)
2. [ ] Recibir y procesar datos de tarifas vigentes
3. [ ] Recibir clientes de prueba con historial
4. [ ] Desarrollar demo en Streamlit
5. [ ] Validar cálculos con facturas reales
6. [ ] Presentar demo a COEMA
7. [ ] Iterar según feedback
8. [ ] Definir arquitectura de producción

---

## 8. Anexo: Facturas Analizadas

### Facturas de Referencia

| Documento | Cliente | Tarifa | Período | Consumo | Total |
|-----------|---------|--------|---------|---------|-------|
| A-0002-00098631 | PEREZ DIEGO | T1R | Dic 2025 | 422 kWh | $137,909.74 |
| A-0002-00097256 | PEREZ DIEGO | T1R | Nov 2025 | 296 kWh | $90,713.36 |
| B-0002-01278775 | CRINIGAN MARIA | T1RE | Dic 2025 | 170 kWh | $79,270.15 |
| B-0002-01268771 | CRINIGAN MARIA | T1RE | Nov 2025 | 44 kWh | $37,642.79 |

---

*Documento generado para análisis interno. Pendiente de validación con COEMA.*