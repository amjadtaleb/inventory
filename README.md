# Build and run
## Notes:
* Add sudo before each docker command on linux
* Secrets are not handled correctly
* API does not support authentication yet

```sh
docker-compose up --build
```

## After first run

```sh
docker-compose exec app ./manage.py migrate
docker-compose exec app ./manage.py createsuperuser
```

## Debugging

```sh
docker-compose exec app ./manage.py shell_plus --print-sql
docker-compose exec db mariadb centribal_orders_db \
    --user=centribal --password=MYSQL_CENTRIBAL_PASSWORD
```

# Tests

```sh
docker run -d --rm --name test-mariadb \
  --env MARIADB_DATABASE=test_db \
  --env MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1 \
  -p 3309:3306 \
  mariadb:11.5.2-noble
```

wait a couple of seconds till the db is stable then run pytest, then stop down the testing DB container. Keep the container running while developing to avoid waiting for the container to run

```sh
docker stop test-mariadb
```


# Cleanup
```sh
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume prune --all
docker network prune
rm -rf data
```
