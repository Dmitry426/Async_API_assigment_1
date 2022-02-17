#!/bin/sh

set -e

es_host="es01_test"
es_port="9200"
redis_host="redis_server_test"
redis_port="6379"
cmd="$@"

>&2 echo "!!!!!!!! Check elastic status:available !!!!!!!!"

until curl http://"$es_host":"$es_port"; do
  >&2 echo "Elastic container is unavailable - sleeping"
  sleep 1
done

>&2 echo "Es Container is running fine"

>&2 echo "!!!!!!!! Check redis status:available !!!!!!!!"

until redis-cli -h "$redis_host" -p "$redis_port" ; do
  >&2 echo "Redis  container is unavailable - sleeping"
  sleep 1
done

>&2 echo "Redis Container is running fine"


exec  echo "Here is main test command running"