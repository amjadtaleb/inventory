# Build and run
sudo docker-compose up --build

## After first run, when necessary
```sh
sudo docker-compose exec app ./manage.py migrate
sudo docker-compose exec app ./manage.py createsuperuser
sudo docker-compose exec app ./manage.py shell_plus --print-sql
sudo docker-compose exec db mariadb centribal_orders_db \
    --user=centribal --password=MYSQL_CENTRIBAL_PASSWORD
```

# Tests

```sh
sudo docker run -d --rm --name test-mariadb \
  --env MARIADB_DATABASE=test_db \
  --env MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1 \
  -p 3309:3306 \
  mariadb:11.5.2-noble
```
wait a couple of seconds till the db is stable then run pytest, then
```sh
sudo docker stop test-mariadb
```


# Cleanup
```sh
sudo docker rm -vf $(sudo docker ps -aq)
sudo docker rmi -f $(sudo docker images -aq)
sudo docker volume prune --all
sudo docker network prune
rm -rf data
```
