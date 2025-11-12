# Multi-stage build for React frontend
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend container
FROM node:18-slim
WORKDIR /app

# Install backend dependencies
COPY backend/package*.json ./
RUN npm install --production

# Copy backend code
COPY backend/ ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./public

# Initialize database
RUN node database.js

# Expose port
EXPOSE 3001

# Start server
CMD ["node", "server.js"]
