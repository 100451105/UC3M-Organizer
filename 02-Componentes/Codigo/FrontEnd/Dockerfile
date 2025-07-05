FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
RUN npx tailwindcss init -p
CMD ["npm", "run", "dev", "--", "--host"]