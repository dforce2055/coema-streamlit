# COEMA - Analisis de Requisitos Actualizado
## Historico de Reuniones con Equipo Operativo

**Reunion 1:** Enero 2026
**Participantes COEMA:**
- Lucia - Contable, administracion, bancos, conciliaciones, pagos, reportes
- Nachi - Facturacion
- Maxi - Atencion al cliente (lider)
- Rosita - Asistente atencion al cliente

**Reunion 2:** Marzo 2026 - Reunion con area de Facturacion (Nachi + ayudante)
**Resultado:** Proceso completo documentado, hallazgos clave incorporados abajo

**Fuente de tarifas:** [OCEBA Cuadros Tarifarios](https://www.oceba.gba.gov.ar/nueva_web/s.php?i=17) - **Area Atlantica**
**Cuadros descargados:** `docs/cuadros-tarifarios/`
- `IF-2026-01658521-GDEBA-GMOCEBA.pdf` - Anexo 6: N1 y Resto (vigente desde 01/01/2026)
- `IF-2026-01666577-GDEBA-GMOCEBA.pdf` - Anexo 14: N2 hasta 350 kWh/mes
- `IF-2025-45079914-GDEBA-GMOCEBA.pdf` - Anexo 104: N3 Tarifa Social hasta 250 kWh/mes (Res. 1176/25)

---

## 1. Contexto del Sistema Actual

### 1.1 Sistema Integrado Existente
COEMA utiliza un sistema integral que maneja:
- ✅ Facturación
- ✅ Cobros (presencial + online: Pago Fácil, Link, transferencias)
- ✅ Compras y pagos a proveedores
- ✅ Contabilidad
- ✅ Gestión de socios
- ✅ Atención al cliente
- ✅ Almacén
- ✅ Oficina Virtual (~30% de usuarios adheridos, ~3,600 usuarios)

### 1.2 Problemas Detectados

| Problema | Descripcion | Prioridad |
|----------|-------------|-----------|
| **Carga de cuadros tarifarios** | Muy complejo, 15+ tarifas, 7+ rangos, cambios frecuentes por resolucion OCEBA | Alta |
| **Reportes inconsistentes** | Discrepancias entre facturacion vs contabilidad vs AFIP, perdida de subsidios | Alta |
| **Conciliacion automatica con errores** | Facturas no visibles para algunos usuarios | Alta |
| **Desfasaje en pagos** | Pago online se refleja al dia siguiente (proceso manual), genera reclamos | Media |
| **Sistema de reclamos** | No pueden reportar cortes fuera de horario, quieren WhatsApp bot 24/7 | Media |
| **Envio de facturas por mail** | Problemas de velocidad con ~10,000 usuarios | Media |

---

## 2. Información Obtenida ✅

### 2.1 Estructura de Tarifas (ACTUALIZADO con cuadros OCEBA)

| Variable | Valor/Detalle | Estado |
|----------|---------------|--------|
| Cantidad de tarifas | 11 tarifas principales (T1R, T1RE, T1G BC, T1G AC, T1GE, T1AP, T2BT, T2MT, T3BT, T3MT, T4R, T4NR, T5, T6) | COMPLETO |
| Fuente oficial | OCEBA - Area Atlantica | COMPLETO |
| Escalones T1R | 7: R1(0-100), R2(100-200), R3(200-400), R4(400-500), R5(500-700), R6(700-1400), R7(>1400) | COMPLETO |
| Escalones T1RE | 4: RE1(0-500), RE2(500-700), RE3(700-1400), RE4(>1400) | COMPLETO |
| Prorrateo | Si el periodo cruza 2 o hasta **3 resoluciones**, se aplican multiples cuadros | Verificado + Reunion |
| Niveles tarifarios | Anexo 6 = N1 y Resto, Anexo 14 = N2 (hasta 350 kWh/mes), Anexo 104 = N3 Tarifa Social (hasta 250 kWh/mes) | COMPLETO |
| Diferencia N1 vs N2 vs N3 | N1/N2: mismo CF, distinto CV. N3: CF mas bajo, CV mas bajo, + bonificaciones fijas por escalon | COMPLETO |

**NOTA IMPORTANTE:** T1RE = Residencial **Estacional** (NO "Exento" como teniamos antes)

### 2.2 Estructura de Clientes

| Variable | Valor/Detalle | Estado |
|----------|---------------|--------|
| Total abonados | ~10,000 servicios | ✅ Confirmado |
| Niveles de segmentación | N1, N2, N3 (por ingresos) | ✅ Confirmado |
| Relación socio-servicio | 1 socio puede tener múltiples servicios | ✅ Confirmado |
| Condición IVA | Consumidor Final (21%), Monotributista (27%) | ✅ Confirmado |

### 2.3 Cargos e Impuestos

| Concepto | Valor/Detalle | Estado |
|----------|---------------|--------|
| Mora | 0.22% por día, igual para todos | ✅ Confirmado |
| IVA Consumidor Final | 21% | ✅ Confirmado |
| IVA Monotributista | 27% | ✅ Confirmado |
| Leyes provinciales | Ley 7290, Ley 11769, etc. | ✅ En facturas |

### 2.4 Variables Especiales

| Variable | Descripcion | Estado |
|----------|-------------|--------|
| **Gas natural** | Si pasa la red de gas, rango de consumo menor (ej: hasta 350 kWh vs 700 kWh sin gas). Esto determina si aplica N2 (Anexo 14) | Confirmado |
| **Bonificaciones** | Violencia de genero, entidades sin fines de lucro, bomberos | Confirmado |
| **Subsidios N1 vs N2** | N2 paga CV mas bajo. Ej T1R R1: N1=$160.29/kWh vs N2=$87.65/kWh (subsidio = la diferencia) | NUEVO |
| **Invierno/Verano** | Mencionado en reunion, afecta tarifas (pendiente detalle) | Pendiente |
| **2 o 3 tramos por mes** | Puede haber hasta 3 resoluciones en un periodo (confirmado en reunion) | Verificado + Reunion |

### 2.5 Proceso de Lectura

| Etapa | Descripción | Estado |
|-------|-------------|--------|
| Colectoras | Teléfonos que descargan lecturas al sistema | ✅ Confirmado |
| Toras | Personas que van casa por casa | ✅ Confirmado |
| Alertas | Consumo cero, variación >50% | ✅ Confirmado |
| Validación | Excel manual antes de facturar masivo | ✅ Confirmado |

### 2.6 Proceso de Facturacion Completo (Reunion Marzo 2026)

#### Paso 1: Carga de cuadros tarifarios (~4 dias)
- Se baja el PDF de OCEBA y se carga **manualmente** al sistema, campo por campo
- **3 dias** de carga (7 hs/dia, 1 persona) + **1 dia** de control por oposicion ("cantada": uno lee el PDF, otro verifica en sistema)
- Puede haber hasta **3 cuadros tarifarios** en una misma factura (si OCEBA publica retroactivamente)
- Se cargan: cuadro comun (Anexo 6 N1), cuadro subsidiado (Anexo 14 N2), tarifa social (Anexo 104 N3), entidades de bien publico, CTT, energia inyectada

#### Paso 2: Actualizacion de padrones y condiciones
- Segmentacion (N1/N2/N3): se baja padron de OCEBA y se procesa automaticamente en el sistema, no se puede modificar manualmente
- **Padron ARBA:** se carga para cada periodo a facturar
- **Padron Subsidio RASE:** se cargan **2 archivos** por periodo
- **Sincronizar Perfil Tarifa Social:** proceso especifico en el facturador (Procesos previos > Actualizar perf TIS)
- Condicion frente a IVA: el sistema se conecta con AFIP automaticamente
- Tasa de interes por mora: se actualiza mensualmente desde OCEBA
- **Tasa alumbrado publico:** se carga por separado en el facturador

#### Paso 2b: Division/Ajuste de consumos
- Los consumos descargados de **SgiMovil** se dividen/ajustan para el periodo leido
- El sistema genera un **nuevo periodo** al ejecutar la division (esto es el prorrateo entre resoluciones)
- **Multas:** se cargan por archivo (actualmente **suspendidas temporalmente**)
- **Intereses:** se generan entre el **15 y 18 de cada mes**

#### Paso 3: Controles previos a facturar
- Ejecutar proceso de **pre-facturacion**
- Reportes de variacion de consumo (configurable, usan 50%)
- Reportes: **usuarios activos y no activos con lectura**, **lecturas fuera de fecha**
- Verificacion de historial de consumo caso por caso
- Reportes: activos sin consumo, no activos con consumo, cambios de medidor, cambios de ruta
- Ejecutar **validador Pre-Facturacion** (paso formal del sistema)
- Si un consumo es dudoso, se manda a re-verificar en campo

#### Paso 4: Facturacion de prueba (20 usuarios fijos)
- Se eligen 20 usuarios fijos que cubren todos los tipos: T1R, T1RE, T2, T5, con inyeccion, alto consumo, etc.
- Se generan comprobantes provisorios (FX) identicos a la factura pero no definitivos
- Se imprimen y se verifican manualmente contra Excel ("Control facturacion")
- **Dos personas** trabajan juntas, jornada completa sin parar (hasta medianoche)
- Si todo OK, se procede a la tirada definitiva

#### Paso 5: Facturacion definitiva (ruta por ruta)
- Cargar **CESP** (debe ser el mismo para rutas e impresion de facturas)
- Se usa plantilla, se cambian fechas/periodo/vencimientos
- Se procesa ruta por ruta (29-30 rutas, 300-500 usuarios c/u)
- **Punto de venta 1:** Energia - GENERAR, CONTROLAR Y CERRAR proceso
- **Punto de venta 2:** Otros servicios (Res. Asamblea + Bomberos) - GENERAR, CONTROLAR cant. usuarios = ruta de luz, Y CERRAR
- Se integran ambos puntos de venta en un **cupon de pago unico**
- Ejecutar **validador POST-Facturacion**

#### Paso 6: Conciliacion y QR
- **Conciliacion tipo 1:** 1 Recibo + 1 Factura (pagos a cuenta / saldos a favor)
- **Conciliacion tipo 2:** 1 Factura Negativa + 1 Factura (ajustes/notas de credito)
- Se calcula mora de periodos anteriores
- Generacion de **Cupones**
- Generacion de **QR de Cupones** (2 pasos: Solicitar, luego Obtener) + codigo de barra

#### Paso 7: Impresion y distribucion
- **Impresion en papel** por numero de pagina, sale por nro punto de cobranza (PTO VTA 2) - **se elimina el 1 de mayo 2026**
- Impresion masiva en **PDF**
- Publicacion de PDF en **Oficina Virtual** (solo proceso nocturno o desde servidor)
- Envio de PDF por **mail** en lotes de 300 (tarda 2-3 dias, proceso semi-manual)

#### Paso 8: Envios y reportes post-facturacion

**Canales de pago (6 archivos de envio):**
| Canal | Detalle |
|-------|---------|
| RIPSA | Archivo de cobro |
| BANELCO | Archivo de cobro |
| LINK | Archivo de cobro |
| Debitos VISA | Prisma NET, Cartera 1. **OJO fecha: entre el 24 y 29 de cada mes** |
| Mercado Pago | Archivo de cobro |
| Boton Macro | Archivo de cobro |

**Reportes institucionales:**
| Destino | Reporte | Detalle |
|---------|---------|---------|
| Municipalidad | Facturas + nota cobranza alumbrado publico | Envio con nota |
| Fedecoba | Facturas dependencias cultura, educacion, policia | Reg. Civil 3920-3932-3204. OJO: CSV vacio, todo "B" |
| OCEBA | Facturas Bomberos en PDF (sum 11183703) | Desde web OCEBA + enviar semestrales |
| CAMMESA | Consumo Coto por Mr. Dims | Mail: martinarriete@cammesa / consumogume@cammesa.com.ar |
| OCEBA | **Protocolo A** - 1ra facturacion | **1er dia de cada mes** posterior al periodo facturado |
| OCEBA | **Agregado tarifario** (cant. usuarios por tarifa) | **1er dia de cada mes** posterior a la facturacion. Manual |
| OCEBA | Archivo **violencia de genero** | Acceso ppal Google con mail tecnica@... |
| OCEBA | **Entidades de bien publico** | Envio periodico |

#### Energia Inyectada (paneles solares)
- Algunos usuarios inyectan energia a la red (instalacion sincronizada especifica)
- Lo inyectado se paga/descuenta de la factura
- Tiene cuadro tarifario propio
- Ejemplo: fabrica de helados Mayolo inyecta ~14,000 kWh, usuario residencial rural ~900 kWh

#### Rutas
- **29-30 rutas** en General Madariaga
- Incluye 1 ruta de camaras de seguridad (~200 camaras, estimadas a **14 kWh/mes** c/u, sin medidor)
- ~10,000 servicios totales

### 2.8 Checklist Oficial de Facturacion Masiva (42 pasos)

**Fuente:** `docs/cuadros-tarifarios/Procedimiento Facturacion Masiva Energia Electrica.xlsx`
Checklist mensual que COEMA usa internamente. Columnas Ene-Dic para marcar cumplimiento.

#### Preparacion de datos (pasos 1-10)
| # | Paso |
|---|------|
| 1 | Descarga de consumos tomados con **SgiMovil** (ano y cuota leidos) |
| 2 | **Division/Ajuste de consumos** del periodo leido → sistema genera nuevo periodo |
| 3 | Cargar **Cuadro Tarifario** |
| 4 | Cargar **tasa interes OCEBA** en el facturador |
| 5 | Cargar **Padron ARBA** para el periodo |
| 6 | Cargar **tasa alumbrado publico** |
| 7 | Cargar 2 archivos del **Padron Subsidio RASE** para el periodo |
| 8 | Sincronizar **Perfil Tarifa Social** (Facturador > Procesos previos > Actualizar perf TIS) |
| 9 | **Generar Intereses** para el periodo (entre el 15 y 18 del mes) |
| 10 | Cargar archivo **Multas** (suspendidas temporalmente) |

#### Facturacion (pasos 11-22)
| # | Paso |
|---|------|
| 11 | Realizar proceso **pre-facturacion** |
| 12 | Reportes usuarios activos y no activos con lectura |
| 13 | Reportes lecturas fuera de fecha |
| 14 | Ejecutar **validador Pre-Facturacion** |
| 15 | Cargar **CESP** (mismo CESP para rutas e impresion) |
| 16 | **GENERAR, CONTROLAR Y CERRAR** proceso facturacion de **ENERGIA** |
| 17 | **GENERAR** proceso de **OTROS SERVICIOS** |
| 18 | Controlar que cant. usuarios facturados = ruta de luz |
| 19 | **Cerrar** proceso de OTROS SERVICIOS |
| 20 | Ejecutar **validador POST-Facturacion** |
| 21 | Conciliacion: 1 Recibo + 1 Factura |
| 22 | Conciliacion: 1 Factura Negativa + 1 Factura |

#### Generacion de comprobantes (pasos 23-27)
| # | Paso |
|---|------|
| 23 | Generacion de **Cupones** |
| 24 | Generacion de **QR de Cupones** (2 pasos: Solicitar → Obtener) + codigo de barra |
| 25 | **Impresion masiva en papel** por nro pagina, sale por nro pta cobranza (PTO VTA 2) |
| 26 | Impresion masiva en **PDF** |
| 27 | Publicacion de PDF en **Oficina Virtual** (proceso nocturno o desde servidor) |

#### Distribucion y envios (pasos 28-42)
| # | Paso |
|---|------|
| 28 | Envio de PDF por **mail** |
| 29 | Envio archivos **RIPSA** |
| 30 | Envio archivos **BANELCO** |
| 31 | Envio archivos **LINK** |
| 32 | Envio archivos **Debitos VISA** (Prisma NET, Cartera 1, fecha 24-29 c/mes) |
| 33 | Envio archivos **Mercado Pago** |
| 34 | Envio archivos **Boton Macro** |
| 35 | Envio facturas a **Municipalidad** + nota cobranza alumbrado publico |
| 36 | Envio facturas a **Fedecoba** (cultura, educacion, policia; Reg.Civil 3920-3932-3204) |
| 37 | Envio facturas **OCEBA Bomberos** en PDF (sum 11183703, desde web OCEBA + semestrales) |
| 38 | Envio consumo **Coto** para **CAMMESA** por Mr. Dims |
| 39 | Envio **OCEBA Protocolo A** - 1ra facturacion (1er dia del mes posterior al periodo) |
| 40 | **Agregado tarifario** (1er dia del mes posterior a la facturacion) |
| 41 | Envio OCEBA archivo **violencia de genero** (acceso Google con mail tecnica@...) |
| 42 | Envio OCEBA **entidades de bien publico** |

### 2.7 CTT - Costo de Transicion Tarifaria (Reunion Marzo 2026)
- **Proposito:** Compensar cuando OCEBA publica aumento retroactivo para un periodo ya facturado
- Ejemplo: OCEBA dice "aumento 2% en enero, 2% en febrero, 2% en marzo" pero lo publica a fines de marzo. Enero y febrero ya se facturaron al precio viejo
- El CTT compensa esa diferencia, se cobra sobre el consumo segun categoria
- **Fuente:** OCEBA publica que porcentaje va para cada cooperativa
- Antes se llamaba "aumento de cuadro tarifario", ahora es CTT por normativa

---

## 3. Cuadros Tarifarios OCEBA - Area Atlantica (Vigentes desde 01/01/2026)

### 3.1 T1R - Residencial (7 escalones)

| Escalon | Rango kWh | Cargo Fijo ($/mes) | CV N1 ($/kWh) | CV N2 ($/kWh) | Subsidio impl. |
|---------|-----------|-------------------|---------------|---------------|----------------|
| R1 | 0-100 | 3,441.98 | 160.2894 | 87.6492 | 72.64 |
| R2 | 100-200 | 5,289.07 | 167.5662 | 96.6652 | 70.90 |
| R3 | 200-400 | 7,228.34 | 173.2144 | 103.4864 | 69.73 |
| R4 | 400-500 | 8,982.79 | 177.3591 | 108.8936 | 68.47 |
| R5 | 500-700 | 14,430.89 | 185.8580 | 117.3991 | 68.46 |
| R6 | 700-1400 | 23,387.74 | 194.8457 | 126.3923 | 68.45 |
| R7 | >1400 | 28,558.89 | 209.5357 | 141.1247 | 68.41 |

### 3.2 T1RE - Residencial Estacional (4 escalones)

| Escalon | Rango kWh | Cargo Fijo ($/mes) | CV N1 ($/kWh) | CV N2 ($/kWh) | Subsidio impl. |
|---------|-----------|-------------------|---------------|---------------|----------------|
| RE1 | 0-500 | 12,090.65 | 209.7823 | 94.2759 | 115.51 |
| RE2 | 500-700 | 13,937.53 | 213.9465 | 102.2110 | 111.74 |
| RE3 | 700-1400 | 15,876.60 | 211.7129 | 106.5967 | 105.12 |
| RE4 | >1400 | 17,630.77 | 246.7837 | 127.5219 | 119.26 |

### 3.3 T1G - Servicio General

**Bajos Consumos (hasta 1000 kWh):**
| CF ($/mes) | CV ($/kWh) |
|-----------|-----------|
| 12,532.82 | 210.1189 |

**Altos Consumos:**
| Escalon | Rango kWh | CF ($/mes) | CV ($/kWh) |
|---------|-----------|-----------|-----------|
| GAC1 | 1000-2000 | 62,663.22 | 176.4542 |
| GAC2 | >=2000 | 82,424.52 | 176.9680 |

### 3.4 T1GE - Servicio General Estacional

| Escalon | Rango kWh | CF ($/mes) | CV ($/kWh) |
|---------|-----------|-----------|-----------|
| GE1 | 0-2000 | 21,044.96 | 213.7384 |
| GE2 | >=2000 | 50,040.36 | 214.3149 |

### 3.5 T1AP - Alumbrado Publico
| CF ($/factura) | CV ($/kWh) |
|---------------|-----------|
| 6,017.24 | 161.7366 |

### 3.6 T4R - Pequeñas Demandas Rurales Residenciales

| Escalon | Rango kWh | CF ($/mes) | CV N1 ($/kWh) | CV N2 ($/kWh) |
|---------|-----------|-----------|---------------|---------------|
| T4R1 | 0-500 | 16,813.64 | 169.3233 | 97.1622 |
| T4R2 | 500-700 | 21,708.19 | 176.9909 | 104.8299 |
| T4R3 | 700-1400 | 26,552.93 | 184.7070 | 112.5459 |
| T4R4 | >1400 | 30,018.71 | 196.3259 | 124.1648 |

### 3.7 T4NR - Pequeñas Demandas Rurales No Residenciales

| Escalon | Rango kWh | CF ($/mes) | CV ($/kWh) |
|---------|-----------|-----------|-----------|
| T4NR1 | 0-500 | 16,813.64 | 163.8815 |
| T4NR2 | 500-700 | 21,708.19 | 172.8304 |
| T4NR3 | 700-1400 | 26,552.93 | 181.8102 |
| T4NR4 | >1400 | 30,018.71 | 195.6768 |

### 3.8 T2/T3 - Medianas y Grandes Demandas (resumen)
Estas tarifas usan cargo por potencia (pico/fuera pico) + cargo variable por energia. Ver PDF completo.
- **T2BT:** CF $36,044.67/mes + Potencia Pico $12,563.33/kW + CV Pico $85.90/kWh
- **T2MT:** CF $54,613.08/mes + Potencia Pico $9,835.20/kW + CV Pico $84.14/kWh
- **T3BT/T3MT:** Similares con distintas tarifas para Usuarios Finales vs Distribuidores Municipales

### 3.9 Cuadro Tarifario N3 - Tarifa Social (Anexo 104, Res. 1176/25)

**Aplica a:** T1R, T3, T4R, T5 (NO incluye T1RE ni T1G/T1GE)
**Limite:** Hasta 250 kWh/mes (500 kWh/mes en Zona Fria)

**NOTA:** N3 tiene CF mas bajo que N1/N2, CV mas bajo, y ademas bonificaciones fijas. Es el nivel mas subsidiado.

#### T1R N3 - Residencial (sub-rangos dentro de escalones)

| Escalon | Rango kWh | Cargo Fijo ($/mes) | CV N3 ($/kWh) | CV N1 ref. | Subsidio impl. |
|---------|-----------|-------------------|---------------|------------|----------------|
| R1 | 0-100 | 1,737.10 | 86.9831 | 160.29 | 73.31 |
| R2 | 100-150 | 2,718.24 | 91.0164 | 167.57 | 76.55 |
| R2 | 150-200 | 5,289.07 | 111.5563 | 167.57 | 56.01 |
| R3 | 200-250 | 7,228.34 | 118.1067 | 173.21 | 55.10 |
| R3 | 250-300 | 7,228.34 | 170.3765 | 173.21 | 2.83 |
| R3 | 300-400 | 7,228.34 | 170.3765 | 173.21 | 2.83 |
| R4 | 400-500 | 8,982.79 | 174.5212 | 177.36 | 2.84 |
| R5 | 500-700 | 14,430.89 | 183.0201 | 185.86 | 2.84 |
| R6 | 700-1400 | 23,387.74 | 192.0079 | 194.85 | 2.84 |
| R7 | >1400 | 28,558.89 | 206.6978 | 209.54 | 2.84 |

**Observacion:** El subsidio fuerte de N3 se concentra en los primeros 250 kWh. A partir de 250 kWh el CV N3 se acerca mucho al N1.

#### T4R N3 - Rural Residencial

| Escalon | Rango kWh | Cargo Fijo ($/mes) | CV N3 ($/kWh) |
|---------|-----------|-------------------|---------------|
| T4R1 | 0-150 | 8,061.84 | 92.2032 |
| T4R1 | 150-250 | 16,813.64 | 112.4915 |
| T4R1 | 250-300 | 16,813.64 | 166.7704 |
| T4R1 | 300-500 | 16,813.64 | 166.7704 |
| T4R2 | 500-700 | 21,708.19 | 174.4381 |
| T4R3 | 700-1400 | 26,552.93 | 182.1542 |
| T4R4 | >1400 | 30,018.71 | 193.7731 |

#### Bonificaciones N3 (descuento fijo adicional por escalon)

| Escalon T1R | Rango kWh | Bonificacion ($/mes) |
|-------------|-----------|---------------------|
| R1 | 0-100 | 1,000 |
| R2 | 100-150 | 3,600 |
| R2 | 150-200 | 4,400 |
| R3 | 200-350 | 8,000 |
| R3 | 350-400 | 8,000 |
| R4 | 400-500 | 11,200 |
| R5 | 500-700 | 16,800 |
| R6 | 700-1400 | 16,800 |
| R7 | >1400 | 16,800 |

Mismas bonificaciones aplican a T4R.

### 3.10 Otros Cargos del Cuadro Tarifario
- **Servicio de Rehabilitacion (corte por falta de pago):** T1R=$4,541.11, T1RE=$6,805.62
- **Cargo por Conexion Aerea Monofasica:** T1R=$36,135.61, T1RE=$38,436.44
- **Recargo bajo coseno fi:** $24.5906/kvarh
- **CENS (Energia No Suministrada):** T1=$1,602.89/kWh, T2-T3=$3,786.33/kWh

---

## NOTA: Informacion aun Faltante

### Formulas no incluidas en cuadros OCEBA (preguntar a COEMA)
| # | Item | Estado |
|---|------|--------|
| 1 | **Formula de Res. Asamblea 21/10/15** | Hipotesis: ~15.3% del CV |
| 2 | **CTT (Art 5 Res 2019-189)** - valores por tarifa y resolucion | Solo tenemos valores de facturas |
| 3 | **Subsidio Estado Nacional** - tasa por kWh por periodo | Descubrimos ~$9/kWh Nov, ~$6.8/kWh Dic |
| 4 | **Alumbrado Publico** - valores por zona y periodo | Solo Zona 1: $9,284 (Nov), $14,000 (Dic) |
| 5 | **Variable gas natural** - como afecta rangos y nivel N2 | Pendiente |
| 6 | **Que significa "Sin Ahorro"** en las facturas | Pendiente |
| 7 | **Invierno/Verano** - como afecta las tarifas | Mencionado en reunion, pendiente detalle |
| 8 | ~~**Cuadro tarifario N3**~~ | ✅ Descargado: Anexo 104 (IF-2025-45079914) |
| 9 | **Juego de datos de prueba** - 20-50 clientes | Pendiente |

---

## 4. Hallazgos del Analisis de Facturas Reales

### 4.1 Formulas Verificadas (4 facturas: PEREZ T1R + CRINIGAN T1RE, Nov-Dic 2025)

#### Prorrateo entre Resoluciones
Cada periodo puede cruzar 2 o hasta 3 resoluciones. Los kWh se dividen proporcionalmente por dias:
```
kwh_res1 = total_kwh * (dias_res1 / dias_total)
kwh_res2 = total_kwh * (dias_res2 / dias_total)
cargo_fijo = CF_res1 * (dias_res1 / dias_total) + CF_res2 * (dias_res2 / dias_total)
cargo_variable = kwh_res1 * CV_res1 + kwh_res2 * CV_res2
```
**Verificado al centavo** en las 4 facturas.

#### Impuestos y Leyes (base = Subtotal Energia)
| Concepto | Porcentaje | Estado |
|----------|-----------|--------|
| IVA Monotributista (T1R) | 27% | Verificado |
| IVA Consumidor Final (T1RE) | 21% | Verificado |
| Ley Provincial 7290 | 4% | Verificado |
| Ley 11769 Art 75 (Ex.9226) | 6% | Verificado |
| Ley 11769 Art 72 Bis | 0.001% | Verificado |
| Ley 11769 Fondo Compensador | 5.5% | Verificado |
| Bomberos | $960 fijo | Verificado |

#### Subsidio Estado Nacional
Tarifa plana por kWh, **igual para todas las tarifas** en el mismo periodo:
- Nov 2025: ~$9.008/kWh
- Dic 2025: ~$6.778/kWh

#### Res. Asamblea 21/10/15 (hipotesis, NO confirmado)
Parece ser ~15.3% del **cargo variable** (no del subtotal energia):
- CRINIGAN Nov: 15.30%, Dic: 15.31% (muy consistente)
- PEREZ Nov: 15.36%, Dic: 15.86% (varia, posiblemente por prorrateo)

### 4.2 Resoluciones Tarifarias Identificadas
- **Nov 2025:** Res. 1118/25 (Anexo 6 = vigente, Anexo 72 = actualizacion)
- **Dic 2025:** Res. 1176/25 (Anexo 6 = vigente, Anexo 72 = actualizacion)
- El CTT subio de $3.99/kWh (Nov) a $9.88/kWh (Dic) para T1R

### 4.3 Estructura de Totales en la Factura
```
Total Liq. Serv. Publicos = Subtotal Energia + Subtotal Leyes + Alumbrado + Mora
Otros Conceptos (seccion separada) = Res. Asamblea + Bomberos
Cupon pago TOTAL = Total Liq + Otros Conceptos - Conciliaciones
```

### 4.4 Hallazgos de la Comparacion COEMA vs CAMUZZI
*(Ver docs/ANALISIS_COEMA_VS_CAMUZZI.md para detalle completo)*

Resumen: COEMA tiene herramientas de analisis superiores (simulador, comparador), pero Camuzzi gana en presentacion de info critica (cuanto debo, cuando vence, variacion vs ano anterior). Recomendacion: combinar lo mejor de ambos.

---

## 5. Alcance Propuesto para la Solución

### 5.1 Fase 1 - Demo de Facturación (Actual)
**Objetivo:** Demostrar cálculo correcto de facturas

| Funcionalidad | Estado |
|---------------|--------|
| Calculadora de factura | ✅ Implementado |
| Simulador de consumo | ✅ Implementado |
| Historial de cliente | ✅ Implementado |
| Comparador de tarifas | ✅ Implementado |

**Pendiente para validar:**
- [ ] Obtener datos reales para ajustar cálculos
- [ ] Validar fórmulas de CTT, Res. Asamblea, Subsidios
- [ ] Incorporar variable de gas natural
- [ ] Agregar todas las tarifas (actualmente solo T1R y T1RE)

### 5.2 Fase 2 - Generación Automática de Tarifas
**Problema a resolver:** "La carga de cuadros tarifarios es lo más complicado"

| Funcionalidad | Descripción |
|---------------|-------------|
| Importador OCEBA | Leer cuadros de la web de OCEBA automáticamente |
| Versionado de tarifas | Historial de resoluciones con fechas de vigencia |
| Validador | Comparar tarifa calculada vs sistema actual |

### 5.3 Fase 3 - Integración con Sistema Actual
**Problema a resolver:** "Desfasaje en pagos, reportes inconsistentes"

| Funcionalidad | Descripción |
|---------------|-------------|
| API de consulta | Sistema externo consulta variables de tarifa |
| Webhook de pagos | Actualización en tiempo real de pagos |
| Exportador de reportes | Formato compatible con AFIP y requerimientos |

### 5.4 Fase 4 - Oficina Virtual Mejorada
**Problema a resolver:** "Notificaciones, avisos de deuda"

| Funcionalidad | Descripción |
|---------------|-------------|
| Notificaciones push | Avisos de vencimiento, corte, etc. |
| Integración WhatsApp | Bot para reclamos y consultas 24/7 |
| Confirmación de lectura | Saber si el usuario recibió el aviso |

### 5.5 Fase 5 - IoT Lecturas Remotas (Futuro)
**Problema a resolver:** "Lecturas aproximadas, no reales"

| Funcionalidad | Descripción |
|---------------|-------------|
| Medidores inteligentes | Lectura remota automática |
| Dashboard en tiempo real | Consumo actual del usuario |
| Alertas automáticas | Consumo anormal, posible fraude |

---

## 6. Preguntas para Reunion con Facturacion (Marzo 2026)

### 6.1 CRITICAS - Sin esto no podemos calcular correctamente

| # | Pregunta | Contexto |
|---|----------|----------|
| 1 | **Formula exacta de Res. Asamblea 21/10/15** | Analizamos 4 facturas y vemos ~15.3% del cargo variable. Es correcto? O tiene otra formula? |
| 2 | ~~**CTT: de donde salen los valores?**~~ | ✅ Reunion: OCEBA lo publica, compensa cambios retroactivos. Porcentaje por cooperativa. Falta obtener tabla exacta de valores por tarifa/periodo |
| 3 | ~~**Prorrateo: siempre son 2 resoluciones?**~~ | ✅ Reunion: Pueden ser 2 o hasta **3** resoluciones en un periodo |
| 4 | **Cuadro N2: el limite de 350 kWh/mes es por gas natural?** | El Anexo 14 dice "N2 hasta 350 kWh/mes". Ese limite es por tener gas, por ingresos, o ambos? |

### 6.2 ALTAS - Necesarias para demo completa

| # | Pregunta | Contexto |
|---|----------|----------|
| 5 | **Subsidio Estado Nacional: donde se publica la tasa?** | Descubrimos que es $/kWh plano ($9.01 Nov, $6.78 Dic). Pero donde se consulta? |
| 6 | **Alumbrado Publico: cuantas zonas hay?** | Zona 1: Nov=$9,284 -> Dic=$14,000. Que zonas existen? Donde se publican los valores? |
| 7 | **"Sin Ahorro" que aparece en las facturas** - que significa? | Aparece en las 4 facturas. Es un estado del cliente? Afecta el calculo? |
| 8 | **Invierno/Verano: como afecta las tarifas?** | Mencionado en reunion anterior. Los cuadros OCEBA tienen tarifas distintas por estacion? |
| 9 | **Bonificaciones: que % de descuento y sobre que base?** | Violencia de genero, bomberos voluntarios, entidades sin fines de lucro |
| 10 | ~~**Cuadro N3**~~ | ✅ Resuelto: Anexo 104, Tarifa Social N3 hasta 250 kWh/mes |

### 6.3 OPERATIVAS - Para entender problematicas y oportunidades

| # | Pregunta | Contexto |
|---|----------|----------|
| 11 | ~~**Carga de cuadros tarifarios: paso a paso**~~ | ✅ Reunion: PDF manual, 3 dias carga + 1 dia control, 2 personas. Ver seccion 2.6 |
| 12 | ~~**Cuanto tardan en cargar nueva resolucion?**~~ | ✅ Reunion: ~4-5 dias. Automatizar = quick win enorme |
| 13 | **Reportes inconsistentes: ejemplo concreto** | No se pregunto en reunion. Pendiente |
| 14 | ~~**Conciliacion automatica: que es?**~~ | ✅ Reunion: Pagos a cuenta / saldos a favor se concilian antes de generar cupon. Se descuenta de factura |
| 15 | **Cuantas resoluciones nuevas salen por ano?** | No se pregunto directamente. Pero "todos los meses algo nuevo" |

### 6.4 Solicitar a COEMA

```
YA TENEMOS (no pedir):
- Cuadro tarifario N1 (Anexo 6), N2 (Anexo 14) y N3 (Anexo 104)
- 4 facturas reales analizadas (PEREZ T1R + CRINIGAN T1RE, Nov-Dic 2025)
- Proceso completo documentado (reunion Marzo 2026)
- CTT explicado (compensacion retroactiva, viene de OCEBA)
- Conciliacion explicada (pagos a cuenta / saldos a favor)
- Prorrateo: puede ser 2 o 3 resoluciones

AUN NECESITAMOS:
1. FORMULAS FALTANTES
   - Res. Asamblea 21/10/15 (formula exacta)
   - CTT: tabla de valores por tarifa y periodo (sabemos que viene de OCEBA pero no los valores exactos)
   - Tasa de subsidio por periodo (fuente?)

2. LOS 20 USUARIOS DE PRUEBA QUE YA USAN
   - Ellos ya tienen 20 usuarios fijos para testing (uno por tipo de tarifa)
   - Pedir: la lista con sus datos y las FX de prueba generadas
   - Campos: ID, Tarifa, Nivel, Condicion IVA, Consumo

3. FACTURAS DE VALIDACION
   - 5-10 facturas de tarifas que no tenemos (T1G, T4R, T2, energia inyectada)

4. ~~CHECKLIST DE FACTURACION~~ ✅ OBTENIDO
   - Procedimiento completo de 42 pasos en `docs/cuadros-tarifarios/Procedimiento Facturacion Masiva Energia Electrica.xlsx`
   - Incorporado como seccion 2.8 del presente documento

5. EXCEL "CONTROL FACTURACION"
   - La planilla Excel que usan para verificar las FX de prueba
```

### 6.5 Siguientes Pasos Tecnicos
- [ ] Cargar cuadro tarifario OCEBA completo (Anexo 6 + Anexo 14 + Anexo 104) en el codigo
- [ ] Implementar prorrateo entre 2 o 3 resoluciones
- [ ] Agregar soporte para N1/N2/N3 (CF y CV distintos para N3)
- [ ] Corregir T1RE de "Exento" a "Estacional" en toda la app
- [ ] Agregar los 7 escalones de T1R y 4 de T1RE
- [ ] Agregar T1G, T1GE, T4R, T4NR al sistema
- [ ] Implementar calculo de subsidio
- [ ] Implementar bonificaciones N3 (tarifa social)
- [ ] Corregir formula Res. Asamblea (post-confirmacion COEMA)
- [ ] Evaluar scraping/lectura automatica de PDFs de OCEBA para carga de tarifas
- [ ] Considerar modulo de energia inyectada (paneles solares)
- [ ] Obtener los 20 usuarios de prueba + Excel "Control facturacion" de Nachi
- [ ] Dos puntos de venta: energia vs otros servicios (Res. Asamblea + Bomberos)

---

## 7. Resumen Ejecutivo

### Lo que tenemos COMPLETO
- **Cuadro tarifario OCEBA** N1 (Anexo 6), N2 (Anexo 14) y N3 Tarifa Social (Anexo 104) - Area Atlantica
- **11 tarifas principales** con todos los escalones: T1R(7), T1RE(4), T1G BC, T1G AC, T1GE, T1AP, T2, T3, T4R(4), T4NR(4), T5, T6
- **Formulas de leyes/impuestos** verificadas al centavo: IVA 21%/27%, Ley 7290 4%, Art75 6%, Art72Bis 0.001%, Fondo 5.5%
- **Formula de prorrateo** entre resoluciones verificada (pueden ser 2 o 3)
- **Mecanismo de subsidio N1 vs N2 vs N3**: N1/N2 mismo CF distinto CV; N3 CF mas bajo + CV mas bajo + bonificaciones
- **4 facturas reales** analizadas con desglose completo
- **Proceso completo de facturacion** documentado paso a paso (reunion Marzo 2026) + **checklist oficial de 42 pasos**
- **CTT explicado**: compensacion retroactiva, valores de OCEBA por cooperativa
- **Conciliacion**: pagos a cuenta / saldos a favor se descuentan antes de generar cupon
- **Energia inyectada**: usuarios con paneles solares, cuadro tarifario propio
- **6 canales de pago:** RIPSA, BANELCO, LINK, Debitos VISA/Prisma, Mercado Pago, Boton Macro
- ~10,000 servicios, 29-30 rutas, 3 niveles (N1, N2, N3), mora 0.22%/dia

### Lo que falta (pedir a Nachi)
- Formula exacta de **Res. Asamblea 21/10/15** (hipotesis: ~15.3% del CV)
- Tabla de **CTT por tarifa/periodo** (valores exactos, sabemos que vienen de OCEBA)
- Tasa de **Subsidio Estado Nacional** por periodo (fuente?)
- Valores de **Alumbrado Publico** por zona
- Variable **Invierno/Verano** y **gas natural** (como interactuan)
- **Los 20 usuarios de prueba** que ya usan + sus FX de ejemplo
- ~~**Excel "Control facturacion"**~~ que usan para verificar
- ~~**Checklist de facturacion**~~ ✅ Obtenido (42 pasos, ver seccion 2.8)

### Descubrimiento clave del analisis de cuadros OCEBA
**T1RE = Residencial ESTACIONAL** (no "Exento"). Esto explica por que tiene menos escalones y cargos distintos: es para clientes estacionales (ej: casas de veraneo en la costa). El nombre en el codigo estaba mal.

**N2 = subsidio implicito via cargo variable mas bajo.** El cargo fijo es identico entre N1 y N2. La diferencia esta en el CV. Ejemplo T1R R1: N1 paga $160.29/kWh vs N2 paga $87.65/kWh. La diferencia ($72.64/kWh) es el subsidio.

**N3 = Tarifa Social (Anexo 104), el nivel mas subsidiado.** Tiene CF mas bajo, CV mas bajo (concentrado en primeros 250 kWh), y bonificaciones fijas adicionales. Ej T1R R1: N3 CF=$1,737 (vs $3,442 N1/N2), CV=$86.98. Solo aplica a T1R, T3, T4R, T5 (no T1RE).

### Riesgo principal
La diferencia de ~$956 en la factura de PEREZ se explica por la falta de prorrateo en el codigo.
Con prorrateo implementado + cuadro tarifario completo, los calculos deberian cuadrar exacto.
Solo quedan las formulas de CTT y Res. Asamblea para tener el 100%.

---

*Documento actualizado Marzo 2026. Cuadros tarifarios OCEBA (N1+N2+N3) incorporados. Reunion con facturacion completada. Checklist oficial de 42 pasos incorporado (seccion 2.8). Pendiente: formulas faltantes y datos de prueba de Nachi.*