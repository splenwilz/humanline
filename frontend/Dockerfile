# Multi-stage Dockerfile for Next.js frontend
# Build arguments
ARG NODE_ENV=production

# Stage 1: Dependencies and build (only for production)
FROM node:20-alpine AS builder
ARG NODE_ENV

# Install system dependencies
RUN apk add --no-cache libc6-compat

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application only if production
ENV NEXT_TELEMETRY_DISABLED 1
RUN if [ "$NODE_ENV" = "production" ] ; then npm run build ; else echo "Skipping build for development" ; fi

# Stage 2: Runtime (production or development)
FROM node:20-alpine AS runtime
ARG NODE_ENV

# Install system dependencies
RUN apk add --no-cache curl

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Set working directory
WORKDIR /app

# For production: copy built application
# For development: copy source and node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package*.json ./
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules

# Copy source code
COPY --chown=nextjs:nodejs . .

# Create .next directory with proper permissions for development mode
RUN mkdir -p .next && chown -R nextjs:nodejs .next

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Set environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the application based on environment
CMD if [ "$NODE_ENV" = "development" ] ; then npm run dev ; else npm start ; fi
