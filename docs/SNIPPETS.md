# Docker compose guide
1. Build docker images
```bash
docker build -f .docker/delta.dockerfile -t delta:latest ./
```

```bash
docker build -f .docker/delta-broker.dockerfile -t delta-broker:latest ./
```

```bash
docker build -f .docker/delta-ebest-feeder.dockerfile -t delta-ebest-feeder:latest ./
```

2. Check docker compose configuration
```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
--file .docker/delta.dev.yml \
config
```

3. Start docker compose
```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
--file .docker/delta.dev.yml \
up
```

```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
--file .docker/delta.dev.yml \
down
```

4. Start prefect server
```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
-f .docker/prefect.dev.yml \
--profile server --profile minio --profile agent up
```

```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
-f .docker/prefect.dev.yml \
--profile server --profile minio --profile agent down 
```

```bash
docker compose \
-f .docker/prefect.dev.yml \
--env-file .docker/.docker-compose.dev.env \
--profile cli up 
```

```bash
docker compose \
-f .docker/prefect.dev.yml \
--env-file .docker/.docker-compose.dev.env \
--profile cli down
```

```bash
docker compose \
-f .docker/prefect.dev.yml \
--env-file .docker/.docker-compose.dev.env \
run cli
```

```bash
docker rm $(docker ps -a -q -f status=exited)
```

```bash
docker rmi $(docker images -f "dangling=true" -q)
```

```bash
docker volume prune -a
```

```bash
export PREFECT_API_URL=http://0.0.0.0:4200/api
prefect deploy -n daily
```


# ETL Process configuration Guide
1. Create Deployment configuration file
```bash
prefect deploy delta/etl/ebest/update_master.py:main
```

2. deploy using this deployment configuration with command:
```bash
prefect deploy -n daily
```

3. To execute flow runs from this deployment, start a worker in a separate terminal that pulls work from the 'delta-docker-pool' work pool:
```bash
prefect worker start --pool 'delta-process-pool'
```

4. To schedule a run for this deployment, use the following command:
```bash
prefect deployment run 'Update EBest Master/daily'
```
