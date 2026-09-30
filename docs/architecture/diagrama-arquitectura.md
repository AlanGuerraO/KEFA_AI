# Diagrama de arquitectura

```mermaid
flowchart TD
    U[Usuario] --> TG[Telegram]
    U --> WEB[Web]
    TG --> BACK[Backend Django + DRF]
    WEB --> BACK

    BACK --> DB[(PostgreSQL)]
    BACK --> IA[IA / LLM]
    BACK --> SEG[Seguridad<br/>JWT / OAuth2]

    IA --> TC[Tool Calling]
    TC --> VAL{Validación y<br/>Autorización}
    VAL -->|Acción sensible| CONF[Confirmación del usuario]
    VAL -->|Autorizado| N8N[n8n]
    CONF --> N8N

    N8N --> CAL[Google Calendar]
    N8N --> TASKS[Google Tasks]
    N8N --> NOTION[Notion]

    CAL --> RES[Resultado]
    TASKS --> RES
    NOTION --> RES
    RES --> LOG[Registro / Historial]
    LOG --> U
```

Este diagrama combina el diagrama de arquitectura de la sección 7 con el flujo de validación/confirmación descrito en las secciones 6 y 12. No agrega componentes fuera de lo ya decidido en la Biblia. 