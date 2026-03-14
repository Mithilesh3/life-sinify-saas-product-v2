FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY index.html ./
COPY public ./public
COPY src ./src
COPY eslint.config.js ./
COPY postcss.config.js ./
COPY tailwind.config.js ./
COPY tsconfig.json ./
COPY tsconfig.app.json ./
COPY tsconfig.node.json ./
COPY vite.config.ts ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
