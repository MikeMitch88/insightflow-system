FROM node:20-alpine AS build

WORKDIR /app

ARG API_URL=https://REPLACE-ME.onrender.com/api
ENV API_URL=$API_URL

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN sed -i "s|https://REPLACE-ME.onrender.com/api|${API_URL}|g" src/environments/environment.ts \
 && npx ng build --configuration=production

FROM nginx:alpine
COPY --from=build /app/dist/kpc-insightflow/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
