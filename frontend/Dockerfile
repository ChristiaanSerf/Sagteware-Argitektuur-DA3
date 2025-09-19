FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm i -g serve
# serve a static folder on port 4173
CMD ["serve","-s",".","-l","4173"]
