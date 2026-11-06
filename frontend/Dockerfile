# Build stage
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json ./
RUN npm install --frozen-lockfile
COPY . .
RUN npm run build

# Production stage — serve with Nginx
FROM nginx:1.25-alpine AS production

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/app.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
