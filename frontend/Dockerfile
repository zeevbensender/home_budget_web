FROM node:20-alpine AS build

WORKDIR /app

# Copy only frontend package files
COPY frontend/package*.json ./

RUN npm install

# Copy frontend source
COPY frontend ./

RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
