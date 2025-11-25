# Syntax=docker/dockerfile:1

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_BASE_URL
ARG VITE_RECAPTCHA_SITE_KEY
ARG VITE_API_HOST

# Create .env file
RUN echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" > .env && \
    echo "VITE_RECAPTCHA_SITE_KEY=${VITE_RECAPTCHA_SITE_KEY}" >> .env && \
    echo "VITE_API_HOST=${VITE_API_HOST}" >> .env

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
