FROM node:22-alpine AS builder

WORKDIR /app
COPY package.json yarn.lock* ./
RUN yarn install --frozen-lockfile 2>/dev/null || yarn install
COPY . .
RUN yarn build

# 最终镜像：将构建产物复制到共享 volume
FROM alpine:3.20
COPY --from=builder /app/dist /app/dist
VOLUME /app/dist
CMD ["cp", "-r", "/app/dist/.", "/usr/share/nginx/html/"]
