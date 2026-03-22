# ── Legal AI Analyzer — Frontend Dockerfile ─────────────────────
FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer caching)
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 5173

# Run dev server on all interfaces so Docker port mapping works
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
