# WebSocket Listener

This service connects to the Fyers WebSocket API and mirrors order/position updates into Redis. It also exposes a simple `/healthz` endpoint for Kubernetes probes.

## Setup

1. Install dependencies:

```bash
make install            # production only
make install-dev        # production + testing
```

   This project requires `httpx` version `>=0.24,<0.25`.

2. Create a `.env` file with the following variables (or export them in your environment).
   The `Settings` class in `listener/config.py` uses `pydantic.BaseSettings` to
   load and validate these values. Import `settings` from `listener.config` in
   your code to access them:

```
FYERS_APP_ID=your-app-id
FYERS_SECRET_KEY=your-secret
FYERS_REDIRECT_URI=https://your-app/callback
FYERS_ACCESS_TOKEN=optional-access-token
FYERS_AUTH_CODE=auth-code-from-login
FYERS_REFRESH_TOKEN=optional-refresh-token
FYERS_SUBSCRIPTION_TYPE=OnOrders
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
MAX_RETRIES=5
RETRY_DELAY=1
```

Run `python -m listener.auth` to generate a login URL. After logging in and
authorising the app, copy the `auth_code` from the redirect and set it as
`FYERS_AUTH_CODE` in your environment. You can optionally exchange the code
yourself with:

```bash
python -m listener.auth --auth-code <code> --write-env
```

This prints the resulting access token and writes it to `.env` when
`--write-env` is supplied. Provide `FYERS_REFRESH_TOKEN` alongside the auth code
if refresh support is enabled. When `FYERS_ACCESS_TOKEN` is absent, the service
automatically exchanges `FYERS_AUTH_CODE` for a new token on startup.

3. Run the service:

```bash
make run
```

The health endpoint will be available on `http://localhost:8000/healthz`.

## Makefile

Common tasks are available via `make` commands:

```bash
make install       # install production dependencies
make install-dev   # install production and dev dependencies
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

To include development dependencies in the image pass `--build-arg INSTALL_DEV=true`
to the build command.

## Kubernetes

A sample deployment is provided in `k8s/deployment.yaml`. It expects a secret
named `fyers-secret` containing at least `app_id` and `auth_code` keys (add
`refresh_token` if you use token refresh). Update the image field with your
built image and apply the manifest:

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
