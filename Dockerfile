FROM python:3.13-alpine
WORKDIR /app
COPY src ./src
RUN mkdir -p /data && adduser -D app && chown app:app /data
USER app
ENV PORT=8080 DATABASE_PATH=/data/orders.db PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python", "-m", "src.app"]
