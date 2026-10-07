# Frontend KEFA AI — Vite + React
#
# Versión de Node alineada con el entorno local real (node --version → v24.14.1).

FROM node:24-alpine

WORKDIR /app

# Instalar dependencias primero (cachea esta capa mientras no cambie
# package*.json, evitando reinstalar en cada build)
COPY package*.json ./
RUN npm install

# Código de la app (.dockerignore excluye node_modules, dist y .env reales)
COPY . .

EXPOSE 5173

# --host 0.0.0.0 es obligatorio: por defecto Vite solo escucha en
# localhost DENTRO del contenedor, lo que lo hace inaccesible desde
# el puerto publicado al host. No se tocó vite.config.js (código del
# equipo de Frontend) para no mezclar responsabilidades; se resuelve
# aquí, a nivel de infraestructura.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
