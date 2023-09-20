# delta
Data-driven Evaluation and Live Trading Algorithm

# Docker compose guide
1. Build docker images
```bash
 docker build -f .docker/delta.dockerfile -t delta
:latest .
```

2. Check docker compose configuration
```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
--file .docker/docker-compose.dev.yml \
config
```

3. Start docker compose
```bash
docker compose \
--env-file .docker/.docker-compose.dev.env \
--file .docker/docker-compose.dev.yml \
up
```

# ETL Process configuration Guide
1. Create Deployment configuration file
```bash
prefect deploy delta/etl/flow/update_master.py:main
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