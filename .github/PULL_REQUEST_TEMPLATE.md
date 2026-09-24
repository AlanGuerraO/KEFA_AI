## Ticket
KEFA-000-git-setup

## Objetivo
<!-- Qué se quiere lograr con este PR -->
Dar la documentacion necesaria para que los integrantes del equipo puedan clonar y ejecutar los primeros comandos para ejecutar de manera correcta la configuracion necesaria de este repositorio

## Análisis / Contexto
<!-- Qué existe actualmente y qué cambia -->
Se agrego una guia de pasos para poder clonar de manera eficiente el repositorio y se cambio la version de husky para utilizar el conventional commits

## Cambios realizados
- Creacion de primeros pasos clonar repositorio .md
- Actualizacio de v8 a v9 de husky

## Archivos afectados
-

## Seguridad
<!-- Riesgos identificados y controles aplicados (auth, validación, secretos, etc.) -->

## Cómo probar
1.
2.

## Riesgos
<!-- Qué podría romperse o quedar pendiente -->

## Checklist antes de solicitar revisión
- [ ] El código sigue la arquitectura y convenciones existentes del proyecto
- [ ] No se incluyen secretos, credenciales, tokens ni archivos `.env`
- [ ] Se agregaron o actualizaron pruebas si corresponde
- [ ] La funcionalidad fue probada localmente
- [ ] La documentación fue actualizada si corresponde
- [ ] El commit sigue la convención del proyecto (`tipo(KEFA-XXX): descripción`)
- [ ] El PR referencia el ticket correspondiente en Jira/Trello
- [ ] Si este PR incluye workflows de n8n (`n8n/workflows/`), se verificó que el JSON exportado no contenga credenciales ni tokens embebidos (ver `n8n/README.md`)

## Revisión requerida
Este PR requiere **1 aprobación** antes de poder fusionarse a `develop`.
No se debe hacer merge sin esa aprobación, incluso si el autor tiene permisos de administrador.
