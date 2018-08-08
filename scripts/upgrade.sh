#!/bin/bash
set -o errexit
set -o pipefail

set_variables(){
    if [ "$CIRCLE_BRANCH" == 'master' ]; then
        APP_SETTINGS="Production"
        CLOUDSQL_CONNECTION_NAME=${PRODUCTION_CLOUD_SQL_CONNECTION_NAME}
        DATABASE_URL=${PRODUCTION_DATABASE_URL}
    else
        APP_SETTINGS="Staging"
        CLOUDSQL_CONNECTION_NAME=${STAGING_CLOUD_SQL_CONNECTION_NAME}
        DATABASE_URL=${STAGING_DATABASE_URL}
    fi
}

authorize_docker() {
    echo "====> Store Sand authenticate with service account"
    echo $GCLOUD_SERVICE_KEY | base64 --decode > ${HOME}/gcloud-service-key.json

    echo "====> Login to docker registry"


    docker login -u _json_key -p "$(cat ${HOME}/gcloud-service-key.json)" https://gcr.io
}

main() {
    set_variables
    authorize_docker
    make upgrade APP_SETTINGS="${APP_SETTINGS}" CLOUDSQL_CONNECTION_NAME="${CLOUDSQL_CONNECTION_NAME}" DATABASE_URL="${DATABASE_URL}"
}

main "$@"
