Django project example using [Django Ninja](https://django-ninja.dev/)



# Build and run
## Notes:
* Add sudo before each docker command on linux
* Secrets are not handled correctly
* API does not support authentication yet

```sh
docker compose up --build -d --wait
```

If you get `dependency failed to start: container centribal-mariadb-orders is unhealthy`, just run the command again, or run build then up.


## After first run

```sh
docker compose exec app ./manage.py migrate
docker compose exec app ./manage.py createsuperuser
```

## Debugging

```sh
docker compose exec app ./manage.py shell_plus --print-sql
docker compose exec db mariadb centribal_orders_db \
    --user=centribal --password=MYSQL_CENTRIBAL_PASSWORD
```

# Tests
You can optionally run the tests in the application database or on a different container, in both cases you need to install the `requirements-test.txt`.

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

Running the tests can be done by either of
```sh
pytest
# or
docker compose exec app ./manage.py pytest
```


# Cleanup
```sh
docker compose down --remove-orphans
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume prune --all
docker network prune
rm -rf data
```


# Usage:
- Start by adding some article categories, taxes will be applied on the category not the article itself, examples: Services, Basics, Cars...
- Add taxes, Examples: (max, 0.57), (standard, 0.215), (reduced, 0.04)...
- Assign taxes to categories, and setup validity dates:
  - Displayed articles will show currently applicable tax
  - Orders will calculate the tax depending on the Order creation date, so applicable tax should have been valid at the time or order creation, if the tax changed after the creation the new value will be ignored
- Create new items:
  - Items without a price or quantity cannot be added to orders
  - Setting a non-existing category will create it
- Create an order
- Edit the order by adding or removing items using positive or negative quantity_change values.
