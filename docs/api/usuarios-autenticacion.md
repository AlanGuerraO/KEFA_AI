# KEFA-008 — Usuarios y autenticación

Estado: implementación y pruebas locales completas; pendiente de revisión
cruzada de código, seguridad y revisión humana antes del merge.

## Modelo y registro

Se conserva users.User, basado en AbstractUser, y su migración existente.
El login utiliza username. El registro requiere username, email y password.
El username es único; el email no es único.

La contraseña se valida con los validadores configurados de Django y se
almacena mediante create_user, usando hash. Nunca se devuelve en la respuesta.
Los campos de privilegios enviados al registro no se asignan al usuario.

## Endpoints

| Método | Ruta | Entrada | Resultado |
|---|---|---|---|
| POST | /api/users/register/ | username, email, password | 201: id, username, email |
| POST | /api/users/login/ | username, password | 200: access, refresh |
| POST | /api/users/token/refresh/ | refresh | 200: access |
| POST | /api/users/token/verify/ | token | 200 si es válido; 401 si es inválido o expirado |
| GET | /api/users/me/ | Authorization: Bearer <access> | 200: id, username, email |
| GET | /api/health/ | Sin credenciales | 200: {"status": "ok"} |

Los cuerpos de los POST se envían como JSON.
Registro inválido: 400. Credenciales incorrectas o usuario inactivo: 401.
Me sin token válido de acceso: 401.
Verificar un token no comprueba por sí solo los permisos ni la actividad del usuario.

## Configuración

La API utiliza JWTAuthentication e IsAuthenticated por defecto.
Registro, login y endpoints de tokens permiten acceso público.
Health conserva su configuración explícita de acceso público.
El administrador de Django conserva la autenticación por sesión.

Access: 5 minutos. Refresh: 1 día. Cabecera: Bearer.
La firma utiliza SECRET_KEY, por defecto de SimpleJWT.

## Validación realizada

python backend/manage.py test config users -v 2

Resultado local: 14 pruebas aprobadas (12 de autenticación y 2 de health).
Incluyen hash de contraseña, prevención de asignación de privilegios,
registro inválido, login, usuario inactivo, acceso protegido, renovación
y rechazo de tokens inválidos, expirados o del tipo incorrecto.

## Puntos para revisión de seguridad

- No se ha configurado limitación de intentos de login o registro.
- No se ha configurado una clave de firma JWT independiente.
- No hay logout con revocación, blacklist ni rotación de refresh.
- Revisar el efecto del permiso global sobre otros endpoints del proyecto.
- Confirmar compatibilidad del stack instalado con SimpleJWT.
- CORS configurado y comprobado en local para http://localhost:5173.
La integración del login del frontend con JWT sigue pendiente de verificar.

Estas pruebas no sustituyen la revisión de seguridad ni la revisión humana.
## CORS — validación local

Se agregó django-cors-headers==4.9.0, corsheaders en INSTALLED_APPS
y CorsMiddleware al inicio de MIDDLEWARE.

CORS_ALLOWED_ORIGINS se lee del entorno como una lista separada por comas.
Para desarrollo se permitió http://localhost:5173.

Django local carga backend/.env; Docker Compose recibe el .env de la raíz.

Validación:
- GET /api/health/ con Origin http://localhost:5173 devuelve 200
  y Access-Control-Allow-Origin: http://localhost:5173.
- El dashboard muestra “Backend conectado”.
- Las 14 pruebas de config y users siguen pasando.
- git diff --check sin errores.
- Preflight OPTIONS a /api/users/login/: 200, origen permitido,
- método POST y cabeceras content-type y authorization autorizados.
## Validación de dependencias

Se actualizó PyJWT de 2.14.0 a 2.15.0 tras detectar dos avisos
en pip-audit.

Resultados posteriores:
- pip check: sin conflictos.
- pip-audit: sin vulnerabilidades conocidas.
- 14 pruebas aprobadas con DeprecationWarning tratado como error.
- git diff --check: sin errores.

Pendiente: verificar el soporte declarado de la combinación de versiones.

Docker no se probó: el comando docker no está disponible en este equipo.
La conexión con health no verifica la integración del login con JWT.