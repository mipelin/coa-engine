# ESPECIFICACIÓN TÉCNICA COMPLETA  
**Challenge DIANA – Decision Superiority for NATO Warfighters**

**Objetivo del sistema:**  
Desarrollar capacidades digitales (principalmente modelos AI/ML y software) que se integren en la plataforma existente *Maven Smart System NATO* (MSS NATO) para lograr **Decision Superiority** mediante planificación y ejecución operativa mejorada, modelado y simulación, apoyo al targeting y wargaming operacional.

---

## 1. Resumen del Challenge (Challenge Summary)

DIANA busca capacidades digitales, particularmente **modelos AI/ML y soluciones de software**, que mejoren la planificación y ejecución operativa a través de:
- Modelado y simulación mejorados
- Apoyo al targeting
- Wargaming operacional

El foco está en **aumentar y mejorar** las funciones de warfighting realizadas en plataformas digitales habilitadas por IA por parte de **Allied Command Operations (ACO)**, Allied Command Transformation y las naciones aliadas.

---

## 2. Restricciones Actuales (Current Constraints)

La planificación militar actual está limitada por:
- Procesos lineales
- Flujos de trabajo manuales
- Datos que **no se actualizan ni responden dinámicamente** a condiciones operativas cambiantes

Esto reduce la relevancia y utilidad de planes estáticos cuando la realidad diverge de las suposiciones iniciales.

**Solución requerida:**  
Integrar modelos AI/ML y software innovador en plataformas digitales existentes para:
- Aumentar la profundidad analítica
- Añadir dinamismo
- Acelerar la toma de decisiones en entornos operativos con limitaciones de tiempo

---

## 3. Fundación Técnica (Technical Foundation)

ACO (con sede en SHAPE) utiliza la plataforma **Maven Smart System NATO (MSS NATO)**, entre otras herramientas.

**Características clave de MSS NATO:**
- Plataforma de operaciones multi-dominio en tiempo real y geospacialmente contextualizada (digital twin)
- Ingestión, transformación y modelado de fuentes de datos diversas:
  - Inteligencia, Vigilancia y Reconocimiento (ISR) en tiempo real
  - Reportes operativos militares
  - Información logística
  - Especificaciones catalogadas de activos militares
  - Datos históricos sobre comportamiento y capacidades adversarias
  - Datos open-source: redes sociales, datos comerciales, clima, etc.

La plataforma ya tiene varias aplicaciones de warfighting y soporta la creación de flujos de trabajo habilitados por IA. Su arquitectura es **abierta y extensible**, permitiendo la integración de capacidades analíticas avanzadas, modelos AI/ML y otras soluciones innovadoras.

---

## 4. Resultados Funcionales Deseados (Desired Functional Outcomes)

Las soluciones integradas deben:
- Identificar patrones, correlaciones y eventos de cambio en los datos de entrada
- Revelar anomalías o desviaciones del “pattern of life” que indiquen amenazas u oportunidades emergentes
- Habilitar preparación automática de escenarios y contexto para wargaming y planificación (usando datos open-source)
- Realizar análisis rápido de cursos de acción (COA) en un espacio de parámetros de alta dimensión
- Identificar riesgos, efectos de segundo y tercer orden, y dependencias operativas
- Incorporar cálculos de proyección de fuerzas, datos de targeting, reportes operativos, doctrina y contexto multi-dominio
- Reducir la carga cognitiva, mejorar la comprensión situacional y acelerar planificación, targeting y ejecución

**Interfaz adicional deseada:**  
Interfaces de lenguaje natural y soporte a decisiones que permitan a los comandantes interactuar directamente con el entorno operacional y ejecutar comando y control mediante flujos intuitivos.

---

## 5. Escenario Ilustrativo (Illustrative Scenario) – DESCRIPCIÓN COMPLETA

Debido al aumento de actividades en la zona gris y tensiones políticas, se decide fortalecer las defensas aliadas en el Flanco Este de la OTAN:
- Aumento de fuerza naval en el Mar Báltico (protección de transporte marítimo comercial e infraestructura submarina)
- Aumento de tropas terrestres cerca de la frontera
- Sistemas de defensa aérea en alta alerta tras incursiones de drones no identificados

Un radar detecta un UAV pequeño y rápido cerca de un aeropuerto civil en territorio OTAN. Con radar solo no se puede identificar modelo ni si es amigo o enemigo.

Minutos después:
- Una empresa de telecomunicaciones reporta corte de un cable de internet submarino en el Báltico
- Imágenes satelitales detectan dos buques no identificados que cambiaron curso dos veces cerca del corte
- Monitoreo de redes sociales muestra videos de convoyes pequeños de vehículos sin marcas cruzando la frontera en varios puntos

Estos eventos sugieren un ataque inminente o en curso.

**Flujo esperado del sistema (COP = Common Operating Picture):**
- Toda la información militar y civil se integra, transforma y unifica en un único COP
- Análisis automatizados destacan correlaciones y anomalías
- Analistas validan procedencia, fiabilidad y contextualizan la información

**Acciones específicas que el sistema debe ejecutar:**
- Fusión de datos de radar + video grueso → cálculo de alta probabilidad de que el UAV sea un dron de ataque enemigo → prompt de workflow de C2 solicitando autorización para neutralizar (según ROE)
- Correlación de imágenes satelitales + reportes públicos + datos marítimos → alta probabilidad de que los dos buques cortaron el cable
- Actualización en tiempo real del COP: los buques cambian curso nuevamente hacia un segundo cable submarino
- Modelado y simulación (teniendo en cuenta clima, condiciones del mar, logística y capacidades de activos disponibles) → análisis rápido de COA para interceptar los buques
- Detección de intención hostil de los buques → visible inmediatamente a comandantes terrestres cerca del convoy
- Aumento de interferencia de radio y jamming cerca del convoy → aumento de probabilidad de que los vehículos sean hostiles
- Incorporación de consideraciones de targeting, protección de fuerzas y gestión de escalada → identificación del COA más robusto

Los comandantes siguen la evolución en tiempo real mientras realizan más modelado, simulación y wargaming para optimizar la respuesta.

---

## 6. Requisitos / Efectos Ejemplares (Exemplar Effects) – LISTA OFICIAL 1-10

DIANA busca capacidades digitales que **exactamente** cumplan lo siguiente:

1. **Simular el comportamiento** de entidades Red Team y Blue Force en entornos de wargaming y planificación operativa (unidades, plataformas, activos ISR, actores neutrales como población civil e infraestructura).

2. **Habilitar representaciones agent-based o AI-driven** de fuerzas adversarias y aliadas que interactúen dentro de entornos digitales simulados (experimentación, ensayos y soporte a decisiones operativas).

3. **Habilitar reinforcement learning, modelado probabilístico y técnicas de optimización** para explorar dinámicas operativas complejas y mejorar el soporte de decisiones mediante simulación y análisis repetido.

4. **Soportar análisis de cursos de acción (COA)** basados en exploración sistemática de parámetros complejos y multifacéticos (postura de fuerzas, logística, comportamiento adversario, targeting y condiciones ambientales).

5. **Automatizar elementos de preparación de escenarios y desarrollo de contexto operacional** (condiciones iniciales: ubicación de unidades, niveles de readiness, equipo, etc.; estímulos dinámicos: eventos trigger y reportes de medios sobre eventos externos).

6. **Soportar elementos del ciclo de planificación y evaluación operacional**, incluyendo soporte de decisiones, desarrollo de órdenes, evaluación de operaciones, pronóstico y lecciones aprendidas, integrándose con flujos de trabajo y procesos de planificación existentes.

7. **Soportar flujos de trabajo de targeting**, incluyendo identificación de objetivos, priorización, asignación de activos y soporte a decisiones de engagement dentro de los ciclos de planificación y ejecución operativa.

8. **Extraer insight de feeds ISR crudos** (imágenes satelitales, datos de radar, video de movimiento completo, datos de señales, etc.) mediante computer vision, análisis de sensores, detección de anomalías y fusión multi-fuente.

9. **Habilitar interacción intuitiva** con el entorno digital, incluyendo **interfaces de lenguaje natural** junto con otras modalidades analíticas (pronóstico, optimización y capacidades de percepción).

10. **Aprovechar fuentes de datos comerciales y open-source** (datasets de defensa estructurados, información relevante para targeting, datos marítimos e infraestructura, información pública disponible) para fortalecer la comprensión situacional y los resultados analíticos.

---

## 7. Tabla de Requisitos del Escenario (Desglose Operativo Detallado)

(Extraído de las tablas proporcionadas – este es el comportamiento esperado paso a paso)

| Scenario Requirement          | Descripción (Expected Behaviour) |
|-------------------------------|----------------------------------|
| Location and Force features   | Fortalecimiento Flanco Este, naval Báltico, tropas terrestres, defensa aérea en alerta |
| Detection                     | Radar detecta UAV cerca de aeropuerto civil |
| Event update 1                | Corte de cable submarino + dos buques sospechosos |
| Event update 2                | Videos de convoyes de vehículos sin marcas cruzando frontera |
| Outcome 1                     | Ataque inminente → preparación de respuesta |
| Expected Preprocess from tool | Integración en COP único + análisis automatizado de correlaciones/anomalías |
| Expected Prediction           | UAV identificado como dron enemigo con alta probabilidad |
| Expected Action / decision recommendation | Prompt de C2 solicitando autorización para neutralizar (ROE) |
| Event Update 3                | Buques identificados como responsables del corte |
| Event Update 4                | Buques cambian curso hacia segundo cable |
| Expected Prediction           | Análisis COA rápido para interceptar buques (modelado + simulación) |
| Event Update 5                | Intención hostil observada en buques (visible a comandantes terrestres) |
| Event Update 6                | Aumento de jamming + radio interference cerca del convoy |
| Expected Prediction           | Probabilidad alta de que vehículos sean hostiles + COA más robusto |
| Model train update            | Seguimiento en tiempo real + modelado/simulación/wargaming continuo |

---

**Instrucciones finales para tu agente IA:**

- El sistema **debe integrarse** con MSS NATO (arquitectura abierta).
- Todo el comportamiento descrito en el escenario ilustrativo debe ser **reproducible** por el sistema.
- Los 10 requisitos ejemplares son **obligatorios** (no opcionales).
- Prioridad: dinamismo en tiempo real, reducción de carga cognitiva, interfaces de lenguaje natural, simulación agent-based / reinforcement learning, fusión multi-fuente ISR y soporte a targeting/COA.

Este documento es **la fuente de verdad única**. Usa exactamente esta especificación para generar el código, arquitectura, prompts, flujos de trabajo y modelos.

