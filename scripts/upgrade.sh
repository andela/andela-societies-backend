#!/bin/bash
set -o errexit
set -o pipefail

set_variables(){
    case "$CIRCLE_BRANCH" in
        master)
            APP_SETTINGS="Production"
            VERSION=""
            CLOUDSQL_CONNECTION_NAME=${PRODUCTION_CLOUD_SQL_CONNECTION_NAME}
            DATABASE_URL=${PRODUCTION_DATABASE_URL}
            INSTANCE_NAME=${PRODUCTION_INSTANCE_NAME}
            DATABASE_NAME=${PRODUCTION_DATABASE_NAME}
            ;;
        develop)
            APP_SETTINGS="Staging"
            VERSION=""
            CLOUDSQL_CONNECTION_NAME=${STAGING_CLOUD_SQL_CONNECTION_NAME}
            DATABASE_URL=${STAGING_DATABASE_URL}
            INSTANCE_NAME=${STAGING_INSTANCE_NAME}
            DATABASE_NAME=${STAGING_DATABASE_NAME}
            ;;
        develop-V2)
            APP_SETTINGS="Staging"
            VERSION="-v2"
            CLOUDSQL_CONNECTION_NAME=${STAGING_CLOUD_SQL_CONNECTION_NAME}
            DATABASE_URL=${STAGING_DATABASE_URL}
            INSTANCE_NAME=${STAGING_INSTANCE_NAME}
            DATABASE_NAME=${STAGING_V2_DATABASE_NAME}
            ;;
        *)
            echo "Err: This branch should not deploy."
            exit 1
            ;;
    esac
}

install_google_cloud_sdk(){
    echo "====> Installing google cloud sdk"
    echo "deb http://packages.cloud.google.com/apt cloud-sdk-jessie main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    sudo apt-get update && sudo apt-get install kubectl google-cloud-sdk
}

authenticate_google_cloud() {
    echo "====> Store Sand authenticate with service account"
    echo $GCLOUD_SERVICE_KEY | base64 --decode > ${HOME}/gcloud-service-key.json
    echo "Configuring Google Cloud Sdk"
    gcloud auth activate-service-account --key-file=${HOME}/gcloud-service-key.json
    gcloud --quiet config set project ${GOOGLE_PROJECT_ID}
}

export_data() {
    DUMP_NAME=$(echo "${APP_SETTINGS}" | tr '[:upper:]' '[:lower:]')${VERSION}-sqldumpfile-$(date '+%Y-%m-%d-%H-%M-%S').gz
    gcloud sql export sql ${INSTANCE_NAME} gs://${SOCIETIES_GCP_BUCKET}/${DUMP_NAME} \
                            --database=${DATABASE_NAME}
}


authorize_docker() {
    echo "====> Store Sand authenticate with service account"
    echo $GCLOUD_SERVICE_KEY | base64 --decode > ${HOME}/gcloud-service-key.json

    echo "====> Login to docker registry"


    docker login -u _json_key -p "$(cat ${HOME}/gcloud-service-key.json)" https://gcr.io
}

logout_docker_google_cloud() {
    gcloud auth revoke --all
}

main() {
    set_variables
    install_google_cloud_sdk
    authenticate_google_cloud
    export_data
    authorize_docker
    make upgrade APP_SETTINGS="${APP_SETTINGS}" CLOUDSQL_CONNECTION_NAME="${CLOUDSQL_CONNECTION_NAME}" DATABASE_URL="${DATABASE_URL}"
    logout_docker_google_cloud
}

main "$@"
