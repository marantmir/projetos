# Dockerfile Frontend - Build Multi-stage
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copia arquivos de dependências
COPY package.json package-lock.json ./

# Instala dependências
RUN npm ci

# Copia código fonte
COPY . .

# Build da aplicação
RUN npm run build

# Stage 2: Servidor Nginx
FROM nginx:alpine

# Instala curl para health check
RUN apk add --no-cache curl

# Copia build do stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expõe porta 80
EXPOSE 80

# Health check com curl
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
