FROM python:3.11-slim
WORKDIR /app
ARG INSTALL_DEV=false
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        pip install --no-cache-dir -r requirements-dev.txt; \
    fi
COPY . .
ENV LOG_LEVEL=INFO
CMD ["python", "-m", "listener.main"]
