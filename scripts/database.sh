#!/usr/bin/env bash
set -eu

echo ${CLOUD_SQL_SERVICE_KEY}

echo ${CLOUD_SQL_SERVICE_KEY} | base64 --decode --ignore-garbage > ${HOME}/gcloud-service-key.json

cloud_sql_proxy \
  -instances=${CLOUDSQL_CONNECTION_NAME}=tcp:0.0.0.0:3300 \
  -credential_file=${HOME}/gcloud-service-key.json \
