# KEFA AI

### Orquestador Personal Inteligente para Automatización de Tareas

## Descripción

**KEFA AI** es un proyecto de Inteligencia Artificial desarrollado bajo la metodología de **Aprendizaje Basado en Proyectos (ABP)**.

El objetivo es desarrollar una plataforma capaz de recibir instrucciones en **lenguaje natural**, interpretarlas mediante Inteligencia Artificial y ejecutar acciones automatizadas en diferentes servicios digitales.

Por ejemplo:

> “Agrega una reunión con mi equipo mañana a las 5 de la tarde y crea una tarea para preparar la presentación.”

El sistema analizará la solicitud, identificará las acciones necesarias y utilizará las herramientas autorizadas para ejecutarlas.

---

## Objetivo

Desarrollar un **orquestador inteligente** que utilice Inteligencia Artificial para interpretar solicitudes del usuario, seleccionar las herramientas adecuadas y coordinar diferentes servicios mediante APIs y automatizaciones.

La IA será utilizada como un **componente de interpretación y toma de decisiones**, mientras que la ejecución de las acciones será controlada por el sistema.

---

## Uso de Inteligencia Artificial

La IA permitirá:

* Interpretar instrucciones en lenguaje natural.
* Identificar la intención del usuario.
* Extraer parámetros de las solicitudes.
* Seleccionar herramientas disponibles.
* Generar acciones mediante **Tool Calling**.
* Mantener contexto de las conversaciones.
* Generar respuestas y resúmenes de las acciones realizadas.

La IA **no tendrá acceso directo e ilimitado a los servicios externos**. Todas las acciones serán validadas por el sistema antes de ejecutarse.

---

## Arquitectura general

```text
             Usuario
                │
        ┌───────┴───────┐
        │               │
      React          Telegram
        │               │
        └───────┬───────┘
                │
             Backend
           Django + DRF
                │
       ┌────────┴────────┐
       │                 │
   PostgreSQL       IA + Orquestador
                         │
                    Tool Calling
                         │
                        n8n
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Google Calendar  Google Tasks    Notion
```

## Organización del equipo

El proyecto será dividido en cuatro áreas principales:

| Integrante   | Área                    |
| ------------ | ----------------------- |
| Kevin | Backend + Base de Datos        |
| Fanny | IA + Orquestador Inteligente   |
| Eric | Automatización + Integraciones |
| Alan | Frontend + DevOps              |

Aunque cada integrante tendrá un área principal, **los cuatro participarán en la revisión e implementación de aspectos de seguridad**.

---

## Tecnologías

| Área                    | Tecnología                              | Responsable    |
| ----------------------- | --------------------------------------- |----------------
| Backend                 | Python + Django + Django REST Framework | Kevin |
| Frontend                | React + Vite                            | Alan |
| Base de datos           | PostgreSQL                              | Kevin |
| Inteligencia Artificial | OpenAI API y/o Claude API               | Fanny |
| Automatización          | n8n                                     | Eric |
| Mensajería              | Telegram Bot API                        | Eric |
| Servicios externos      | Google Calendar, Google Tasks, Notion   | Eric |
| Autenticación           | JWT + OAuth 2.0                         | **TODOS** |
| Contenedores            | Docker + Docker Compose                 | Alan |
| Control de versiones    | Git + GitHub                            | **TODOS** |
| Gestión del proyecto    | Trello                                  | **TODOS** |

---

## Estructura del proyecto

```text
kefa-ai/
├── backend/       # Django + API + PostgreSQL
├── frontend/      # React
├── ai/            # IA + prompts + herramientas
├── n8n/           # Workflows y automatizaciones
├── docs/          # Documentación
├── tests/         # Pruebas
├── docker-compose.yml
├── .env.example
└── README.md
```

---

---

## Seguridad

La seguridad será una **responsabilidad compartida por los cuatro integrantes**.

Se contemplarán:

* Autenticación y autorización.
* Validación de entradas.
* Protección de credenciales y tokens.
* Uso de variables de entorno.
* OAuth 2.0 para servicios externos.
* Control de permisos.
* Lista de herramientas autorizadas para la IA.
* Confirmación de acciones sensibles.
* Protección contra **Prompt Injection** y uso indebido del Tool Calling.
* Registro y auditoría de acciones.
* Revisión de seguridad durante el desarrollo.

---

## Alcance inicial (MVP)

El primer prototipo permitirá:

1. Registrar e iniciar sesión.
2. Recibir instrucciones mediante Telegram.
3. Interpretar solicitudes mediante IA.
4. Utilizar Tool Calling.
5. Ejecutar acciones mediante n8n.
6. Crear y consultar eventos de Google Calendar.
7. Crear y gestionar tareas de Google Tasks.
8. Solicitar confirmación para acciones sensibles.
9. Registrar el historial de acciones.
10. Visualizar información mediante un dashboard web.

---

## Metodología

El desarrollo se gestionará mediante **Git/GitHub y Trello**, utilizando tareas, sprints, ramas de desarrollo, revisión de código y pruebas.

El proyecto seguirá un enfoque incremental, priorizando primero un **MVP funcional** y posteriormente agregando funcionalidades adicionales.

---

## 🎓 Propósito académico

KEFA AI busca demostrar la aplicación práctica de conceptos de **Inteligencia Artificial, desarrollo web, APIs, automatización, bases de datos, seguridad e integración de sistemas** en una solución funcional desarrollada mediante trabajo colaborativo.