# Primeros pasos al clonar KEFA AI

Guía para cualquier integrante del equipo que clone el repositorio por primera vez. Sigue estos pasos en orden — evita los errores ya detectados durante el setup inicial (Chat 08).

---

## 1. Requisitos previos

Antes de clonar, confirma que tienes instalado:

```bash
git --version
node --version
npm --version
```

**Windows:** instala "Git for Windows" (incluye **Git Bash**). Usa Git Bash para todos los comandos de este documento, **no PowerShell ni CMD** — varios comandos (`chmod`, por ejemplo) no existen ahí.

---

## 2. Clonar el repositorio

```bash
git clone git@github.com:AlanGuerraO/KEFA_AI.git
cd KEFA_AI
```

Verifica en qué rama quedaste por defecto:

```bash
git branch --show-current
```

Normalmente será `main`. Cambia a `develop`, que es donde vive el trabajo activo del equipo:

```bash
git checkout develop
git pull origin develop
```

> `main` se mantiene solo con el README inicial hasta que llegue el momento de subir el MVP. Todo el desarrollo activo ocurre en `develop` y en ramas `feature/*`/`bugfix/*`.

---

## 3. Instalar dependencias y activar el linter de commits

```bash
npm install
```

Esto instala `husky`, `@commitlint/cli` y `@commitlint/config-conventional`, y ejecuta automáticamente el script `prepare` (`husky`), que configura los hooks de Git.

### Verificación obligatoria del hook (no te la saltes)

```bash
git config core.hooksPath
```

Debe apuntar a `.husky`. Si no aparece nada o da error, corre manualmente:

```bash
npm run prepare
```

### Permisos de ejecución del hook

Si estás en **Git Bash / Linux / macOS**:

```bash
chmod +x .husky/commit-msg
```

Si por alguna razón Git no reconoce el permiso al hacer `git status` (aparece como modificado sin que tú lo hayas tocado), fuerza el bit directamente en el índice:

```bash
git update-index --chmod=+x .husky/commit-msg
```

**Windows con `core.autocrlf=true`:** el repo ya incluye un `.gitattributes` que fuerza `LF` en `.husky/*` y `*.sh`, así que no deberías ver el warning de "LF will be replaced by CRLF" en este archivo. Si lo ves, confirma que tu copia local de `.gitattributes` esté actualizada (`git pull`) y vuelve a normalizar:

```bash
git add --renormalize .husky/commit-msg
```

---

## 4. Probar que el hook realmente funciona

```bash
# Debe FALLAR (falta el scope/ticket)
git commit -m "feat: prueba sin scope" --allow-empty

# Debe PASAR
git commit -m "feat(KEFA-XXX): prueba de commitlint" --allow-empty
```

Si el segundo pasó, deshaz ese commit de prueba (era solo para validar, no es trabajo real):

```bash
git reset --soft HEAD~1
```

Si **ninguno de los dos casos se comporta como se espera** (por ejemplo, el commit inválido no falla), el hook no está activo — repite el paso 3 antes de seguir. No sigas trabajando sin esta validación funcionando: es la única barrera automática que impide commits fuera de la convención del proyecto.

---

## 5. Antes de empezar a trabajar en algo

**Nunca trabajes directo sobre `develop` ni sobre `main`** — ambas están protegidas (requieren Pull Request + 1 aprobación, no aceptan push directo).

```bash
git checkout develop
git pull origin develop
git checkout -b feature/KEFA-XXX-descripcion-corta
```

Reemplaza `KEFA-XXX` por el número real del ticket en Jira/Trello. No se crean ramas sin ticket ni por integrante — solo por tarea real.

---

## 6. Al abrir el Pull Request — el error más común que ya tuvimos

Cuando pushees tu rama y GitHub te muestre el link para crear el PR, **antes de dar clic en "Create pull request"**, revisa el selector superior:

```
base: develop  ←  compare: feature/KEFA-XXX-descripcion-corta
```

GitHub selecciona `main` como `base` por defecto (es la rama por defecto del repo). Si no lo cambias manualmente a `develop`, tu PR se va a fusionar en el lugar equivocado — esto ya nos pasó una vez y tomó varios pasos revertirlo.

Con GitHub CLI, evita este error por completo especificando el `--base` explícitamente:

```bash
gh pr create --base develop --head feature/KEFA-XXX-descripcion-corta \
  --title "feat(KEFA-XXX): descripción breve" \
  --body "Ver checklist del PR template."
```

---

## 7. Si el link de comparación de GitHub te da 404

Verifica primero los datos reales de tu repo, no asumas la URL:

```bash
git remote -v
git branch -r
```

Construye el link de comparación con esos valores exactos:

```
https://github.com/<usuario-u-org>/<repo>/compare/develop...feature/KEFA-XXX-descripcion-corta
```

Un 404 casi siempre es un nombre de usuario, repo o rama mal escrito (GitHub distingue mayúsculas/minúsculas).

---

## 8. Después de que tu PR se fusiona

```bash
git checkout develop
git pull origin develop
git branch -d feature/KEFA-XXX-descripcion-corta
```

Antes de borrar cualquier rama (local o remota), confirma que sí está fusionada — no asumas:

```bash
git branch -r --merged origin/develop
```

Si tu rama aparece en esa lista, es seguro borrarla. Si `git branch -d` (minúscula) se niega con "not fully merged" pero ya confirmaste lo anterior con `--merged`, puedes forzar con `-D` mayúscula — pero solo después de esa confirmación, nunca antes.

---

## Resumen de comandos que NO existen fuera de Git Bash (en Windows)

| Comando | Dónde funciona |
|---|---|
| `chmod` | Solo Git Bash / Linux / macOS. En PowerShell usa `git update-index --chmod=+x <archivo>` |
| `ls -l`, `cat`, `grep` | Solo Git Bash / Linux / macOS |

---

## Checklist rápido de esta guía

- [ ] Cloné el repo y cambié a `develop`
- [ ] Corrí `npm install`
- [ ] Confirmé `git config core.hooksPath` → `.husky`
- [ ] Probé un commit inválido (falló) y uno válido (pasó)
- [ ] Nunca trabajo directo sobre `main`/`develop`, siempre en `feature/KEFA-XXX-...`
- [ ] Verifico el `base:` del PR antes de crearlo
- [ ] Confirmo con `--merged` antes de borrar cualquier rama
