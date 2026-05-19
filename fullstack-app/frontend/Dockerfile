FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY . .

ENV PORT=3000

CMD ["sh", "-c", "serve -s . -l $PORT"]