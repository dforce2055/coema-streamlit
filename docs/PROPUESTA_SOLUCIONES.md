# COEMA - Propuesta de Soluciones

**Fecha:** Marzo 2026
**Actualizado:** Post reunion interna de equipo (Marzo 2026)
**Demo objetivo:** Despues del 23/04/2026

---

## 1. Diagnostico de Situacion

### El problema central
El proveedor del sistema actual tiene a COEMA **cautivo**: sistema monolitico cerrado, sin APIs, sin integraciones, sin voluntad de abrir. El sistema se quedo en el tiempo y ya no da respuesta a las necesidades actuales.

### Consecuencias concretas
- **Perdida de subsidios:** COEMA no puede entregar el informe a CAMMESA en tiempo y forma hace mas de un año. Estan perdiendo plata que podrian cobrar. **Este punto solo puede justificar la inversion.**
- **Facturacion por aproximacion:** El sistema fallo y tuvieron que facturar estimado ("si el mes pasado pagaste 36.000, te debe 37.500"). Quilombo con clientes y municipalidad.
- **Carga manual de tarifas:** 4 dias/persona por resolucion OCEBA, tipeando campo por campo desde PDF. Error humano + horas extra.
- **Jornadas extenuantes:** Dos personas hasta medianoche verificando facturas contra Excel antes de cada tirada.
- **30% de adopcion** en oficina virtual. Eliminacion de factura en papel el 1 de mayo 2026.
- **Reclamos sin respuesta** fuera de horario laboral.

### Decision del equipo
**Solucion integral.** No tiene sentido ofrecer parches chicos que no se van a poder integrar al sistema cerrado. Se reemplaza el sistema de facturacion completo. El gerente general dijo: *"Solucioname facturacion, despues te doy todos los demas problemas."*

---

## 2. Arquitectura Propuesta

### Vision general
Portal unico conectado a SAP Business One y OCEBA, con tres capas:

```
┌─────────────────────────────────────────────────────────┐
│                    PORTAL / PLATAFORMA                   │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────────────┐ │
│  │  OFICINA VIRTUAL  │      │    INTRANET COOPERATIVA   │ │
│  │  (Cliente final)  │      │    (Empleados COEMA)      │ │
│  │                    │      │                            │ │
│  │ - Mi factura       │      │ - Dashboard facturacion    │ │
│  │ - Historial        │      │ - Control pre-facturacion  │ │
│  │ - Simulador        │      │ - Checklist 42 pasos       │ │
│  │ - Reclamos         │      │ - Alertas y reportes       │ │
│  │ - Pagos            │      │ - Gestion de clientes      │ │
│  └────────┬───────────┘      └─────────────┬──────────┘ │
│           │                                 │            │
│  ┌────────┴─────────────────────────────────┴──────────┐ │
│  │              CAPA DE INTEGRACION (APIs)              │ │
│  └──┬──────────┬──────────────┬──────────────┬─────────┘ │
└─────┼──────────┼──────────────┼──────────────┼───────────┘
      │          │              │              │
┌─────┴────┐ ┌──┴───┐  ┌──────┴──────┐  ┌────┴─────┐
│ SAP B1   │ │OCEBA │  │ App Movil   │  │ Canales  │
│ + B1 UP  │ │(PDF/ │  │ Tomaestados │  │ de Pago  │
│ + Print  │ │ API) │  │ (lecturas)  │  │          │
│ Delivery │ │      │  │             │  │          │
└──────────┘ └──────┘  └─────────────┘  └──────────┘
```

### Componentes

#### A. SAP Business One (ERP)
- Facturacion, contabilidad, AFIP
- **B1 UP**: interfaz mejorada, parametrizacion de pantallas, desarrollos rapidos
- **Print Delivery**: impresion masiva automatica, envio de PDFs por mail en lotes, generacion nocturna sin intervencion
- Caracterizacion de socios: grupos de clientes, niveles (N1/N2/N3), condicion IVA, tarifas especiales
- Logica de ordenes de venta → facturacion por lotes (no factura individual)
- Reportes: variacion de consumo, alertas, controles previos

#### B. Motor de Facturacion / Integracion OCEBA
- **Opcion 1:** API de OCEBA (si existe - Nachi menciono que el sistema actual "se esta viendo para conectarse")
- **Opcion 2:** Lector automatico de PDFs de OCEBA (Anexos 6, 14, 104)
- Procesamiento de cuadros tarifarios: carga automatica, validacion, versionado
- Calculo de prorrateo entre resoluciones (2 o 3 por periodo)
- Calculo de subsidios, CTT, leyes, mora
- Generacion de informe CAMMESA para recuperar subsidios
- **Esta pieza alimenta a SAP via Service Layer API**

#### C. App Movil para Tomaestados
- Lectura de medidores desde el telefono
- **Subida remota** al servidor (no volver a la central para descargar)
- Modo offline: guarda localmente si no hay conexion, sincroniza cuando se conecta
- Alertas: consumo cero, variacion >50%, fuera de rango
- Reemplaza el proceso actual de colectoras + descarga en central

#### D. Portal Web (doble cara)

**Cara interna (Intranet COEMA):**
- Dashboard de facturacion con checklist interactivo (los 42 pasos)
- Controles pre-facturacion: alertas automaticas, reportes de variacion
- Gestion de clientes/socios: historial, consumos, reclamos
- Consulta de informacion sin entrar a SAP (divide roles: quien consulta vs quien factura)
- Reportes institucionales: Municipalidad, Fedecoba, OCEBA, CAMMESA

**Cara externa (Oficina Virtual):**
- Acceso por DNI o numero de cliente
- Factura digital, historial de consumo, simulador
- Reclamos online (genera llamada de servicio en SAP)
- Estado de cuenta y pagos
- Eventualmente: pago online integrado

---

## 3. Fases de Implementacion

### Fase 0 - Fundacion (actual → demo 23/04)
| Entregable | Responsable |
|------------|-------------|
| Demo del motor de facturacion (calculo correcto con datos reales) | Diego |
| Esquema grafico punta a punta del circuito | Equipo (Lu + Pablo esquema → Diego detalle) |
| Presentacion SAP B1 adaptada al caso COEMA | Lu |
| Definicion puntos de integracion SAP ↔ Motor facturacion | Lu + Diego |

### Fase 1 - Facturacion (meses 1-6)
**Foco: reemplazar el sistema de facturacion actual. Es el dolor principal.**

| Componente | Detalle |
|------------|---------|
| Motor de facturacion | Calculo completo: tarifas OCEBA, prorrateo, N1/N2/N3, CTT, subsidios, leyes, mora |
| Integracion OCEBA | Lector de PDFs o API. Carga automatica de cuadros tarifarios |
| SAP B1 configuracion | Maestro de socios, caracterizacion (tarifa, nivel, IVA), ordenes de venta, facturacion por lotes |
| Print Delivery | Generacion masiva de PDFs, envio por mail automatico, impresion programada |
| App tomaestados | Lectura movil con subida remota |
| Informe CAMMESA | Recuperar subsidios perdidos |
| Portal interno (MVP) | Dashboard de facturacion + checklist + controles |

### Fase 2 - Integracion y pruebas (meses 5-8, se pisa con Fase 1)
| Componente | Detalle |
|------------|---------|
| Integracion SAP ↔ Motor | Service Layer API, ordenes de venta, facturacion |
| Pruebas con 20 usuarios fijos | Validacion contra facturas reales del sistema viejo |
| Ajustes de caracterizacion | Grupos de clientes, descuentos, tarifas especiales |
| Migracion de datos | Padron de socios, historico de consumos |
| Pruebas de conciliacion | Cobranzas, extractos bancarios, medios de pago |

### Fase 3 - Portal completo + go-live (meses 7-10)
| Componente | Detalle |
|------------|---------|
| Oficina virtual | Acceso cliente, factura digital, reclamos |
| Reportes institucionales | OCEBA, Fedecoba, Municipalidad, CAMMESA |
| Canales de pago | Archivos RIPSA, BANELCO, LINK, Prisma/VISA, Mercado Pago, Boton Macro |
| Go-live | Apagar sistema viejo, prender sistema nuevo. Tiene que estar todo andando |

### Fases futuras (post go-live)
- CRM / Gestion de reclamos con Salesforce Service Cloud
- Bot WhatsApp 24/7
- Modulo de cobranzas y conciliacion bancaria avanzada
- Energia inyectada (paneles solares)
- Gestion de stock (medidores, cables, materiales)
- Replicar solucion para otras cooperativas OCEBA

---

## 4. Estimacion de Tiempos

| Escenario | Plazo total |
|-----------|-------------|
| Optimista | 8 meses |
| Realista | 10 meses |
| Con colchon por imprevistos | 12 meses |

**Consideraciones:**
- SAP B1 + Print Delivery: ~2 semanas de configuracion base, pero la caracterizacion especifica del negocio electrico va a requerir relevamiento adicional
- Integraciones: minimo 2 meses de pruebas (SAP ↔ Motor ↔ OCEBA ↔ App). "Las primeras citas nos van a llevar tiempo"
- Van a aparecer casuisticas no contempladas. Siempre aparecen
- El go-live es critico: se apaga uno y se prende el otro, tiene que estar todo funcionando

---

## 5. Argumento de Valor / ROI

### Recupero directo
- **Subsidios CAMMESA:** COEMA no puede entregar el informe hace mas de un año. El sistema nuevo lo genera automaticamente. El dinero recuperado puede cubrir parte o todo el costo del proyecto.

### Ahorro operativo
- **Carga de tarifas:** De 4 dias a minutos (automatico desde OCEBA)
- **Verificacion de facturas:** De jornada completa manual a controles automaticos con alertas
- **Envio de facturas por mail:** De 2-3 dias semi-manual a envio nocturno automatico (Print Delivery)
- **Lecturas:** Subida remota desde campo, no hay que volver a la central

### Reduccion de riesgo
- Eliminacion de facturacion por aproximacion
- Eliminacion de errores de tipeo en carga de tarifas
- Controles previos automaticos antes de facturar
- Reportes consistentes (facturacion = contabilidad = AFIP)

### Escalabilidad
- La solucion OCEBA (lector PDF / API) sirve para cualquier cooperativa del Area Atlantica
- Potencial de replicar para otras cooperativas (ej: Villa, otras que usen OCEBA)

---

## 6. Investigacion OCEBA: API vs PDF (Marzo 2026)

### Resultado: NO hay API publica para cuadros tarifarios. Hay que ir por lector de PDF.

#### Lo que encontramos

OCEBA tiene un **simulador de facturacion** en `https://www.oceba.gba.gov.ar/simulador/` que usa una API REST interna con 4 endpoints:

| Endpoint | Metodo | URL |
|----------|--------|-----|
| Categorias por empresa | GET | `/simulador/empresa/categorias/{id}` |
| Tarifas por categoria | GET | `/simulador/empresa/categoria/tarifas/{id}` |
| Subtarifas por tarifa | GET | `/simulador/empresa/categoria/tarifa/subtarifas/{id}` |
| Calcular factura | POST | `/simulador/calcular` |

**Empresas disponibles:** Solo 4 (las distribuidoras principales)
- ID 1 = EDELAP (Rio de la Plata)
- ID 2 = EDEA (Area Atlantica) ← **esta es la de COEMA**
- ID 3 = EDEN (Norte)
- ID 4 = EDES (Sur)

**Ejemplo de respuesta** (`POST /calcular` con empresa=2, subtarifa=R, 296 kWh, 29 dias):
```json
{
  "total": 36054.98,
  "tabla": [
    {"nombre": "CARGO FIJO R3", "unidad": "$/mes", "valor": 5000.75, "total": 4754.81},
    {"nombre": "CARGO VARIABLE R3 (200 < kWH-Mes ≤ 400)", "unidad": "$/kWh", "valor": 105.7438, "total": 31300.16}
  ]
}
```

#### Limitaciones criticas (por que NO sirve para carga de tarifas)

| Limitacion | Impacto |
|------------|---------|
| Solo devuelve **totales calculados**, no la tabla tarifaria completa (todos los escalones con rangos, CF, CV) | No podemos extraer el cuadro tarifario |
| Solo cubre **T1R y T1G** (subtarifas "R" y "G"). Faltan T1RE, T2, T3, T4R, T4NR, T5, T6, T1GE, T1AP | Cobertura parcial |
| Solo devuelve valores **N2** (subsidiado). El parametro `tipo` no cambia nada. Sin N1 ni N3 | No sirve para todos los niveles |
| **Sin selector de fecha/resolucion** - usa la resolucion vigente del momento | No sirve para prorrateo ni historico |
| No incluye CTT, subsidio Estado Nacional, leyes, ni Res. Asamblea | Solo calcula energia basica |
| No hay 401/auth pero tampoco documentacion publica - puede cambiar sin aviso | Riesgo de estabilidad |

#### Para que SI sirve

La API del simulador es util como **herramienta de validacion cruzada**:
- Podemos enviar un consumo y comparar nuestro calculo vs el de OCEBA
- Sirve para verificar que nuestro lector de PDF cargo bien los valores
- Es un "segundo par de ojos" automatico

#### Decision: Lector de PDF

Los cuadros tarifarios se publican en `https://oceba.gba.gov.ar/nueva_web/s.php?i=17` como **PDFs individuales** organizados por fecha de vigencia, distribuidor y categoria. No hay CSV, JSON, XML ni datos abiertos.

**Estrategia de implementacion:**
1. **Scraping de la pagina de tarifas** para detectar nuevas resoluciones automaticamente
2. **Parser de PDF** (con tabula-py, camelot, o similar) para extraer las tablas de los Anexos
3. **Validacion cruzada** contra la API del simulador (para los valores que cubre: T1R y T1G N2)
4. **Versionado** de cada resolucion con fecha de vigencia

**Nota:** Nachi menciono que el sistema actual "se esta viendo para conectarse" con OCEBA. Puede ser que exista un canal privado (SFTP, web service interno) entre OCEBA y las cooperativas que no es publico. **Preguntar a COEMA si reciben archivos de OCEBA por algun medio digital ademas del PDF.**

---

## 7. Preguntas Abiertas

| # | Tema | Estado |
|---|------|--------|
| 1 | ~~OCEBA: tiene API o solo PDFs?~~ | ✅ Investigado: NO hay API de tarifas. Solo simulador limitado + PDFs. Ver seccion 6 |
| 2 | Informe CAMMESA: formato exacto requerido, que datos necesitan, hace cuanto no lo entregan | Preguntar a COEMA |
| 3 | Extractos bancarios: que banco usan? Galicia/Santander dan datos, Provincia/Nacion no | Preguntar a COEMA |
| 4 | Conciliacion de cobranzas: como machean pagos con facturas hoy? | Relevar |
| 5 | Oficina virtual actual: es del proveedor o de un tercero? | Preguntar a COEMA |
| 6 | Formulas pendientes: Res. Asamblea, CTT por tarifa, tasa subsidio, alumbrado publico | Preguntar a Nachi |
| 7 | Los 20 usuarios de prueba + Excel "Control facturacion" | Pedir a Nachi |

---

## 7. Proximos Pasos

- [ ] Esquema grafico del circuito punta a punta (equipo, esta semana)
- [ ] Definir puntos de integracion SAP ↔ Motor facturacion (Lu + Diego, viernes)
- [ ] Preparar demo del motor de facturacion para despues del 23/04
- [ ] Investigar si OCEBA tiene API disponible
- [ ] Preparar presentacion SAP B1 adaptada al caso COEMA
- [ ] Contactar cooperativa de Villa (segundo cliente potencial)
- [ ] Armar estimacion de costos para tener lista para la demo

---

*Documento actualizado Marzo 2026. Basado en reuniones con equipo operativo COEMA (Enero y Marzo 2026), analisis de requisitos (REQUISITOS_V2.md) y reunion interna de equipo (Marzo 2026).*
