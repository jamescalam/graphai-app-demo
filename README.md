# GraphAI Research Agent

A fully-functional research agent API built with [GraphAI](https://github.com/aurelio-labs/graphai). Includes everything you'd need from an AI agent API, including:

* **Docker** — the application is wrapped into a docker container, which we run with `docker-compose up`.
* **API** — we use [FastAPI]() to create and serve our API. Exposing two endpoints; `GET /chat?chat_id=...` and `POST /chat?chat_id=...`.
* **Observability features** — logging, metrics, and traces are captured with [OpenTelemetry](https://opentelemetry.io), collected by [Jaeger](https://www.jaegertracing.io), and displayed in a nice monitoring UI with [Prometheus](https://prometheus.io).
