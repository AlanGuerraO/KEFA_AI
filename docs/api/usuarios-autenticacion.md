# Usuarios y autenticación — API

**Ticket:** KEFA-008 "Implementar usuarios y autenticación" → Jira KEFA-63 · **Responsable:** Kevin
**Código:** `backend/users/`, `backend/config/settings.py`
**Última actualización:** 11 de octubre de 2026 (código: `develop` @ `954b34b`)

## Estado

| Aspecto | Estado |
|---|---|
| Implementación | Mergeada en `develop` (PR #12) |
| Pruebas | 12 de autenticación + 2 de health. El equipo las reporta aprobadas en local; **no se ejecutaron en la última revisión** |
| Revisión de seguridad y revisión humana | El documento original las daba como pendientes antes del merge. No hay evidencia en el repositorio de que se completaran (Jira KEFA-71 sigue sin hacer): confirmar en el PR #12 y registrar el resultado |
| Integración con el frontend | **Pendiente.** El login del frontend es simulado y no llama a esta API |
| Configuración de `settings.py` | **Con problema:** tras mezclar KEFA-007 y KEFA-008, `corsheaders` y `CorsMiddleware` quedaron duplicados. Ver `control-de-estado.md`, hallazgo H1 |

---

## 1. Modelo y registro

- Se conserva `users.User`, basado en `AbstractUser`, y su migración `0001_initial`.
- El **login utiliza `username`**. El registro requiere `username`, `email` y `password`.
- El `username` es único; el `email` **no** es único (decisión abierta).
- La contraseña se valida con los validadores configurados de Django y se guarda con hash mediante `create_user`. Nunca se devuelve en la respuesta.
- Los campos de privilegios enviados en el registro (`is_staff`, `is_superuser`, `groups`, `user_permissions`) no se asignan al usuario.

## 2. Endpoints

| Método | Ruta | Acceso | Entrada | Resultado |
|---|---|---|---|---|
| POST | `/api/users/register/` | Público | `username`, `email`, `password` | 201: `id`, `username`, `email` |
| POST | `/api/users/login/` | Público | `username`, `password` | 200: `access`, `refresh` |
| POST | `/api/users/token/refresh/` | Público | `refresh` | 200: `access` |
| POST | `/api/users/token/verify/` | Público | `token` | 200 si es válido; 401 si es inválido o expirado |
| GET | `/api/users/me/` | Bearer JWT | Cabecera `Authorization: Bearer <access>` | 200: `id`, `username`, `email` |
| GET | `/api/health/` | Público | — | 200: `{"status": "ok"}` |

**Códigos de error**

- Registro inválido: 400.
- Credenciales incorrectas o usuario inactivo: 401.
- `me` sin token de acceso válido: 401.

Los cuerpos de los POST se envían como JSON. Verificar un token no comprueba por sí solo los permisos ni si el usuario sigue activo.

## 3. Configuración

**Autenticación**

- `REST_FRAMEWORK`: `JWTAuthentication` y `IsAuthenticated` por defecto.
- Registro, login y los endpoints de tokens permiten acceso público; `health` conserva su acceso público explícito.
- El administrador de Django conserva la autenticación por sesión.

**JWT (`SIMPLE_JWT`)**

| Parámetro | Valor |
|---|---|
| Access token | 5 minutos |
| Refresh token | 1 día |
| Cabecera | `Bearer` |
| Firma | `SECRET_KEY` (valor por defecto de SimpleJWT) |

**CORS**

- Paquete `django-cors-headers==4.9.0`, `corsheaders` en `INSTALLED_APPS` y `CorsMiddleware` al inicio de `MIDDLEWARE`.
- `CORS_ALLOWED_ORIGINS` se lee del entorno como lista separada por comas; en desarrollo, `http://localhost:5173`.
- Django local carga `backend/.env`; Docker Compose recibe el `.env` de la raíz.

> **Corrección pendiente:** en `develop` estas entradas aparecen dos veces en `settings.py`. Debe quedar una sola de cada una.

## 4. Validación reportada por el equipo

Comando indicado en el ticket original:

```bash
python backend/manage.py test config users -v 2
```

**Pruebas:** 14 aprobadas (12 de autenticación y 2 de health). Cubren hash de contraseña, prevención de asignación de privilegios, registro inválido, login, usuario inactivo, acceso protegido, renovación y rechazo de tokens inválidos, expirados o de tipo incorrecto.

**CORS (local):**

- `GET /api/health/` con `Origin: http://localhost:5173` devuelve 200 y `Access-Control-Allow-Origin: http://localhost:5173`.
- El dashboard muestra "Backend conectado".
- Preflight `OPTIONS` a `/api/users/login/`: 200, origen permitido, método `POST` y cabeceras `content-type` y `authorization` autorizados.

**Dependencias:** PyJWT se actualizó de 2.14.0 a 2.15.0 tras dos avisos de `pip-audit`. Resultados reportados: `pip check` sin conflictos, `pip-audit` sin vulnerabilidades conocidas, 14 pruebas aprobadas con `DeprecationWarning` tratado como error y `git diff --check` sin errores.

**Limitaciones de la validación original**

- Docker no se probó (el comando no estaba disponible en el equipo que validó).
- La conexión con `health` no verifica la integración del login con JWT.
- Estas pruebas no sustituyen la revisión de seguridad ni la revisión humana.
- Según el documento original (escrito antes del merge), las pruebas se corrieron antes de que la configuración de CORS quedara duplicada; conviene repetirlas tras corregirla.

## 5. Puntos abiertos de seguridad

| Punto | Estado |
|---|---|
| Limitación de intentos de login y registro (rate limiting) | No configurado (Jira KEFA-168) |
| Clave de firma JWT independiente de `SECRET_KEY` | No configurada (Jira KEFA-156) |
| Logout con revocación, blacklist y rotación de refresh | No existe |
| Efecto del permiso global `IsAuthenticated` sobre otros endpoints | Por revisar |
| Compatibilidad de la combinación de versiones instalada con SimpleJWT | Por verificar |
| Unicidad del email | Decisión abierta |
| Integración del login del frontend con JWT | Pendiente de implementar y verificar |
