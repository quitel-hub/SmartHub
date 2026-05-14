FROM node:20-slim AS build-stage
WORKDIR /frontend

COPY web/package*.json ./
RUN npm install

COPY web/ ./
RUN npm run build

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ukr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=build-stage /frontend/dist /app/static

EXPOSE 10000

CMD ["python", "main.py"]