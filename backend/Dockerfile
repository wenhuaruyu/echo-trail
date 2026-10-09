FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_ENV=production \
    PUBLIC_BASE_URL=https://echo-trail-api-325485-12-1502718593.sh.run.tcloudbase.com \
    CORS_ORIGINS=https://wenhuaruyu-d5gptrfx6908a5cc6-1502718593.tcloudbaseapp.com

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
