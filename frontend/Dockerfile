# ---------- Stage 1: Build React app ----------
FROM node:18-alpine AS build

WORKDIR /app

# Install deps
COPY package.json package-lock.json* ./
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# ---------- Stage 2: Serve with nginx ----------
FROM nginx:1.25-alpine

# Copy built assets to nginx html
COPY --from=build /app/build /usr/share/nginx/html

# Provide a basic nginx config suitable for SPA
# (ensures client-side routing works)
RUN printf "server {\n  listen 80;\n  server_name _;\n  root /usr/share/nginx/html;\n  location / {\n    try_files \$uri /index.html;\n  }\n} \n" > /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck (optional)
HEALTHCHECK CMD wget -qO- http://localhost/ || exit 1
