FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --omit=dev
COPY tsconfig.json ./
COPY src ./src
COPY public ./public
RUN npm install typescript && npm run build && npm uninstall typescript
EXPOSE 8787
ENV NODE_ENV=production
CMD ["node", "dist/server.js"]
