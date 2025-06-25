# WebSocket Listener

This service connects to the Fyers WebSocket API and mirrors order/position updates into Redis. It also exposes a simple `/healthz` endpoint for Kubernetes probes.

## Setup

1. Install dependencies:

```bash
make install
```

   This project requires `httpx` version `>=0.24,<0.25`.

2. Create a `.env` file with the following variables (or export them in your environment).
   The `Settings` class in `listener/config.py` uses `pydantic.BaseSettings` to
   load and validate these values. Import `settings` from `listener.config` in
   your code to access them:

```
FYERS_APP_ID=your-app-id
FYERS_ACCESS_TOKEN=access-token
FYERS_SUBSCRIPTION_TYPE=OnOrders
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
MAX_RETRIES=5
RETRY_DELAY=1
```

3. Run the service:

```bash
make run
```

The health endpoint will be available on `http://localhost:8000/healthz`.

## Makefile

Common tasks are available via `make` commands:

```bash
make install       # install dependencies
make run           # start the service
make test          # run unit tests
make docker-build  # build the Docker image
make docker-run    # run the Docker container
```

## Docker

Build and run the image:

```bash
docker build -t websocket-listener .
docker run -p 8000:8000 websocket-listener
```

## Kubernetes

A sample deployment is provided in `k8s/deployment.yaml`. It expects secrets `fyers-secret` containing `app_id` and `access_token` keys. Update the image field with your built image and apply the manifest:

```bash
kubectl apply -f k8s/deployment.yaml
```

## Tests

Run unit tests with:

```bash
make test
```

## Integration with Webhook Service

This listener stores updates in Redis under keys prefixed with `fyers:`. The existing webhook service can read these keys to keep trade status in sync.

## License

This project is licensed under the [MIT License](LICENSE).
