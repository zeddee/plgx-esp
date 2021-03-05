# Stage 1
FROM node:14-alpine as build-step
RUN mkdir -p /app
WORKDIR /app
COPY package.json /app
RUN npm install
COPY . /app
RUN npm run build -- --prod

# Stage 2
FROM nginx:1.17.1-alpine
RUN mkdir -p /app
WORKDIR /app
COPY --from=build-step /app/dist /app
COPY --from=build-step /app/resources /app/downloads
COPY --from=build-step /app/nginx /etc/nginx
EXPOSE 80
