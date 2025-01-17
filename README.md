# GraphAI Research Agent

A fully-functional research agent API built with [GraphAI](https://github.com/aurelio-labs/graphai). Includes everything you'd need from an AI agent API, including:

* **Docker** — the application is wrapped into a docker container, which we run with `docker-compose up`.
* **API** — we use [FastAPI]() to create and serve our API. Exposing two endpoints; `GET /chat?chat_id=...` and `POST /chat?chat_id=...`.
* **Observability features** — logging, metrics, and traces are captured with [OpenTelemetry](https://opentelemetry.io), collected by [Jaeger](https://www.jaegertracing.io), and displayed in a nice monitoring UI with [Prometheus](https://prometheus.io).


## Instructions

1. `git clone` the repo
2. copy the `.env.example` file to a `.env` file and enter your API keys (currently only `OPENAI_API_KEY` is required
3. navigate to the directory and enter `docker-compose up --build` (ensuring Docker is running on your machine)
4. open `localhost:8000/docs`
5. find the `/chat` endpoint, click **Try it out** and enter a query with chat history:

```
{
    "message": "your query",
    "chat_history": [
        {"role": "assistant", "content": "Hello there"}
    ]
}
```

5. execute the query and get a streamed response
