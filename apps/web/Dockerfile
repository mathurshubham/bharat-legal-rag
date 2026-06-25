FROM node:22-alpine AS base
RUN corepack enable pnpm

FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
# Disable minimumReleaseAge policy — rejects packages published < 24h ago (pnpm v10 security feature).
# Safe to bypass here since we control and trust our lockfile.
RUN echo "minimum-release-age=0" > .npmrc && pnpm install --frozen-lockfile

FROM base AS builder
WORKDIR /app
# Build-time arg — NEXT_PUBLIC_* vars are baked into the JS bundle at build time,
# not at runtime. Must be passed as a build arg, not a container env var.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S nextjs && adduser -S nextjs -G nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nextjs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nextjs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
