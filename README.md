# CodeReviewAI

Tested on Ollama if you want to use OpenAI, change adapter in src.service.

1. Clone repository
```shell
git clone https://github.com/Dementris/CodeReviewAI.git
cd CodeReviewAI
```
2. Create an env file as in the example.

3. Build and Start Service using Docker compose
```shell
docker-compose up --build
```

Optional for ollama:
```shell
docker exec -it ollama ollama pull qwen2.5-coder:32b
```
