# Imagen del frontend en dos etapas. Compose la construye con la carpeta 09_front_back como contexto.

# Etapa 1: construir con Node. Genera los archivos estáticos en /app/dist.
FROM node:24-alpine AS construccion
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2: servirlos con nginx. De la etapa anterior solo se copia dist/: Node no queda en la imagen final.
FROM nginx:stable-alpine
COPY --from=construccion /app/dist /usr/share/nginx/html
