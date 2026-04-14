FROM node:24-bookworm

# System packages
RUN apt-get update && apt-get install -y \
    socat \
    git \
    curl \
    python3 \
    python3-pip \
    jq \
  && rm -rf /var/lib/apt/lists/*

# Bake any additional binaries your skills need at build time.
# Anything installed at runtime will be lost on container restart.
#
# Example: Gmail CLI
# RUN curl -L https://github.com/steipete/gog/releases/latest/download/gog_Linux_x86_64.tar.gz \
#   | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/gog
#
# Example: WhatsApp CLI
# RUN curl -L https://github.com/steipete/wacli/releases/latest/download/wacli_Linux_x86_64.tar.gz \
#   | tar -xz -C /usr/local/bin && chmod +x /usr/local/bin/wacli

WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY ui/package.json ./ui/package.json
COPY scripts ./scripts

RUN corepack enable
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build
RUN pnpm ui:install
RUN pnpm ui:build

ENV NODE_ENV=production

CMD ["node", "dist/index.js"]
