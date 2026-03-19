# SPEC Tecnico - Ajustes Necesarios en el Codigo

**Archivo principal:** `src/app.py`
**Fecha:** Marzo 2026
**Basado en:**
- Analisis de 4 facturas reales (PEREZ T1R Nov-Dic 2025, CRINIGAN T1RE Nov-Dic 2025)
- Cuadros tarifarios OCEBA Area Atlantica vigentes 01/01/2026 (Anexo 6 N1 + Anexo 14 N2)

---

## 1. Implementar Prorrateo entre Resoluciones [CRITICO]

**Problema:** El codigo usa una sola resolucion. Las facturas reales siempre aplican 2 resoluciones por periodo (la vigente y la siguiente).

**Formula verificada:**
```
dias_total = dias_res1 + dias_res2
kwh_res1 = total_kwh * (dias_res1 / dias_total)
kwh_res2 = total_kwh * (dias_res2 / dias_total)

cargo_fijo = CF_res1 * (dias_res1 / dias_total) + CF_res2 * (dias_res2 / dias_total)
cargo_variable = kwh_res1 * CV_res1 + kwh_res2 * CV_res2
ctt = kwh_res1 * CTT_res1 + kwh_res2 * CTT_res2
```

**Ejemplo verificado (PEREZ Nov 2025, 296 kWh, 29 dias):**
- Res.1118/25 Anexo 6: 25 dias, CF3=6,895.82, CV=165.4024, CTT=3.9940
- Res.1118/25 Anexo 72: 4 dias, CF3=7,118.98, CV=167.0336, CTT=4.2020
- CF = 6,895.82*(25/29) + 7,118.98*(4/29) = 6,926.60 (factura: 6,926.60)
- CV = 255.17*165.4024 + 40.83*167.0336 = 49,025.70 (factura: 49,025.70)

**Cambios necesarios:**
- Refactorizar `calcular_factura()` para recibir lista de resoluciones con dias
- Agregar parametros `dias_res1`, `dias_res2` al calculo
- Actualizar la UI para permitir configurar dias por resolucion

---

## 2. Agregar Resolucion 1118/25 (Noviembre 2025) [CRITICO]

**Problema:** Solo esta cargada Res.1176/25. Las facturas de Nov usan Res.1118/25.

**Datos confirmados de facturas:**

### Res. 1118/25 Anexo 6 (Nov 2025)
| Tarifa | Escalon | Rango kWh | Cargo Fijo | CV $/kWh | CTT $/kWh |
|--------|---------|-----------|------------|----------|-----------|
| T1R | 3 | 200-400 | 6,895.82 | 165.4024 | 3.9940 |
| T1RE | 1 | 0-500 | 11,540.95 | 203.5041 | 3.9940 |

### Res. 1118/25 Anexo 72 (transicion Nov->Dic)
| Tarifa | Escalon | Rango kWh | Cargo Fijo | CV $/kWh | CTT $/kWh |
|--------|---------|-----------|------------|----------|-----------|
| T1R | 3 | 200-400 | 7,118.98 | 167.0336 | 4.2020 |
| T1RE | 1 | 0-500 | 11,911.11 | 204.1013 | 4.2020 |

### Res. 1176/25 Anexo 6 (Dic 2025) - ya cargada parcialmente
| Tarifa | Escalon | Rango kWh | Cargo Fijo | CV $/kWh | CTT $/kWh |
|--------|---------|-----------|------------|----------|-----------|
| T1R | 4 | 400-500 | 8,846.72 | 173.6190 | 9.8780 |
| T1RE | 1 | 0-500 | 11,911.11 | 206.6378 | 4.2020 |

### Res. 1176/25 Anexo 72 (transicion Dic->Ene)
| Tarifa | Escalon | Rango kWh | Cargo Fijo | CV $/kWh | CTT $/kWh |
|--------|---------|-----------|------------|----------|-----------|
| T1R | 4 | 400-500 | 8,982.79 | 174.5212 | 10.3920 |
| T1RE | 1 | 0-500 | 12,090.65 | 206.9445 | 4.4210 |

**Cambios necesarios:**
- Reestructurar `RESOLUCIONES` para incluir Anexo 6 y Anexo 72 como sub-resoluciones
- Agregar Res.1118/25 completa
- Corregir valores de Res.1176/25 Anexo 6 (escalones 1,2,5,6 de T1R estan inventados, eliminar o marcar como no confirmados)

---

## 3. Corregir Formula de Res. Asamblea [CRITICO]

**Problema actual:** El codigo usa `subtotal_energia * 0.1346` (13.46%).

**Hallazgo:** La formula real parece ser ~15.3% del **cargo variable** (no del subtotal energia).

| Factura | Cargo Variable | Res. Asam | % del CV |
|---------|---------------|-----------|----------|
| PEREZ Nov | 49,025.70 | 7,532.46 | 15.36% |
| PEREZ Dic | 73,305.29 | 11,624.32 | 15.86% |
| CRINIGAN Nov | 8,960.96 | 1,370.86 | 15.30% |
| CRINIGAN Dic | 35,140.59 | 5,379.54 | 15.31% |

CRINIGAN es muy consistente (~15.30%). PEREZ Dic varia (15.86%), posiblemente por prorrateo.

**Cambio necesario:**
```python
# ANTES (incorrecto):
res_asamblea = subtotal_energia * 0.1346

# DESPUES (hipotesis, PENDIENTE confirmacion COEMA):
res_asamblea = cargo_variable * 0.1531
```

**NOTA:** Esta formula necesita confirmacion de COEMA antes de implementar.

---

## 4. Agregar Calculo de Subsidio Estado Nacional [ALTO]

**Problema:** El codigo no calcula el subsidio. Solo se muestra como dato informativo en las facturas.

**Formula descubierta:** Tarifa plana por kWh, igual para todas las tarifas en el mismo periodo.
- Nov 2025: ~$9.008/kWh
- Dic 2025: ~$6.778/kWh

**Verificacion:**
- PEREZ Nov: 296 * 9.008 = 2,666.37 (factura: 2,666.45, diff por prorrateo)
- CRINIGAN Nov: 44 * 9.008 = 396.35 (factura: 396.36)
- PEREZ Dic: 422 * 6.778 = 2,860.12 (factura: 2,860.22)
- CRINIGAN Dic: 170 * 6.778 = 1,152.26 (factura: 1,152.22)

**Cambio necesario:**
- Agregar campo `subsidio_por_kwh` a cada resolucion
- Calcular: `subsidio = kwh * subsidio_por_kwh` (o con prorrateo si las tasas difieren entre resoluciones)
- Mostrar en la UI como informacion separada

---

## 5. Agregar Calculo de Mora [MEDIO]

**Problema:** No hay calculo de mora.

**Formula verificada:** 0.22% por dia sobre deuda vencida.
- PEREZ Dic: $670.75 sobre deuda de $43,614.77 = 1.538% = ~7 dias

**Cambio necesario:**
- Agregar campo opcional de deuda anterior y dias de mora
- `mora = deuda_anterior * 0.0022 * dias_mora`
- Incluir en Subtotal Otros Conceptos

---

## 6. Cargar Cuadro Tarifario OCEBA Completo [CRITICO - NUEVO]

**Problema:** El codigo tiene 6 escalones inventados para T1R y 2 para T1RE. Ahora tenemos los datos oficiales.

**Datos OCEBA Anexo 6 (N1) vigentes 01/01/2026:**

T1R - 7 escalones:
```python
"T1R": {
    "nombre": "Tarifa 1 Residencial",
    "escalones": [
        {"num": 1, "codigo": "R1", "desde": 0, "hasta": 100, "cargo_fijo": 3441.98, "cv_n1": 160.2894, "cv_n2": 87.6492},
        {"num": 2, "codigo": "R2", "desde": 100, "hasta": 200, "cargo_fijo": 5289.07, "cv_n1": 167.5662, "cv_n2": 96.6652},
        {"num": 3, "codigo": "R3", "desde": 200, "hasta": 400, "cargo_fijo": 7228.34, "cv_n1": 173.2144, "cv_n2": 103.4864},
        {"num": 4, "codigo": "R4", "desde": 400, "hasta": 500, "cargo_fijo": 8982.79, "cv_n1": 177.3591, "cv_n2": 108.8936},
        {"num": 5, "codigo": "R5", "desde": 500, "hasta": 700, "cargo_fijo": 14430.89, "cv_n1": 185.8580, "cv_n2": 117.3991},
        {"num": 6, "codigo": "R6", "desde": 700, "hasta": 1400, "cargo_fijo": 23387.74, "cv_n1": 194.8457, "cv_n2": 126.3923},
        {"num": 7, "codigo": "R7", "desde": 1400, "hasta": 99999, "cargo_fijo": 28558.89, "cv_n1": 209.5357, "cv_n2": 141.1247},
    ]
}
```

T1RE - 4 escalones:
```python
"T1RE": {
    "nombre": "Tarifa 1 Residencial Estacional",  # NO "Exento"!
    "escalones": [
        {"num": 1, "codigo": "RE1", "desde": 0, "hasta": 500, "cargo_fijo": 12090.65, "cv_n1": 209.7823, "cv_n2": 94.2759},
        {"num": 2, "codigo": "RE2", "desde": 500, "hasta": 700, "cargo_fijo": 13937.53, "cv_n1": 213.9465, "cv_n2": 102.2110},
        {"num": 3, "codigo": "RE3", "desde": 700, "hasta": 1400, "cargo_fijo": 15876.60, "cv_n1": 211.7129, "cv_n2": 106.5967},
        {"num": 4, "codigo": "RE4", "desde": 1400, "hasta": 99999, "cargo_fijo": 17630.77, "cv_n1": 246.7837, "cv_n2": 127.5219},
    ]
}
```

**Cambios necesarios:**
- Reemplazar escalones hardcodeados con datos OCEBA oficiales
- Agregar campo `nivel` (N1/N2) al cliente para seleccionar CV correcto
- Corregir nombre T1RE: "Residencial Estacional" (no "Exento")
- Agregar tarifas T1G, T1GE, T1AP, T4R, T4NR (ver REQUISITOS_V2.md seccion 3)

---

## 7. Reestructurar Modelo de Datos de Resoluciones [MEDIO]

**Estructura propuesta:**
```python
RESOLUCIONES = {
    "Res.1118/25": {
        "anexos": {
            "Anexo 6": {
                "vigencia_desde": "2025-11-01",
                "vigencia_hasta": "2025-11-30",
                "tarifas": {
                    "T1R": {
                        "escalones": [...],
                        "ctt_por_kwh": 3.9940,
                        "subsidio_por_kwh": 9.008,
                    },
                    "T1RE": {...}
                }
            },
            "Anexo 72": {
                "vigencia_desde": "2025-12-01",
                "vigencia_hasta": None,
                "tarifas": {...}
            }
        }
    },
    "Res.1176/25": {
        "anexos": {
            "Anexo 6": {...},
            "Anexo 72": {...}
        }
    }
}
```

---

## 8. Alumbrado Publico Dinamico [BAJO]

**Datos confirmados:**
- Zona 1, Nov 2025: $9,284.00
- Zona 1, Dic 2025: $14,000.00

**Cambio:** Asociar valores de alumbrado a la resolucion/periodo, no hardcodear por mes.

---

## Orden de Implementacion Sugerido

1. **Cargar cuadro tarifario OCEBA completo** (T1R 7 esc, T1RE 4 esc, T1G, etc.) con soporte N1/N2
2. **Corregir T1RE** de "Exento" a "Estacional" en toda la app
3. **Reestructurar modelo de resoluciones** para soportar Anexo 6 + Anexo 72
4. **Implementar prorrateo** en `calcular_factura()`
5. **Cargar Res.1118/25** (Nov 2025) con datos confirmados de facturas
6. **Agregar selector de nivel** (N1/N2) en la UI
7. **Agregar calculo de subsidio** ($/kWh plano por periodo)
8. **Corregir formula Res. Asamblea** (despues de confirmacion COEMA)
9. **Agregar calculo de mora**
10. **Alumbrado publico dinamico**

---

## Datos Pendientes de COEMA para Completar

- [x] ~~Cuadro tarifario completo~~ - OBTENIDO: Anexo 6 (N1) y Anexo 14 (N2) OCEBA
- [ ] Formula exacta de Res. Asamblea 21/10/15
- [ ] CTT por tarifa y resolucion (no aparece en cuadros OCEBA)
- [ ] Tasa de subsidio por periodo (donde se publica?)
- [ ] Valores de alumbrado publico por zona y periodo
- [ ] Variable de gas natural (como se relaciona con N2 y el limite de 350 kWh)
- [ ] Cuadro N3 (si existe)
- [ ] Variable Invierno/Verano
- [ ] Juego de datos de prueba (20-50 clientes)
