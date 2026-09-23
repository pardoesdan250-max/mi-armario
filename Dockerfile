FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt requirements-hosting.txt ./
RUN pip install --no-cache-dir -r requirements-hosting.txt && useradd --uid 10001 --create-home armario && mkdir /data && chown armario:armario /data
COPY --chown=armario:armario . .
USER armario
ENV ARMARIO_DATA_DIR=/data PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "90", "--limit-request-line", "4094", "wsgi:application"]
