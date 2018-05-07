#!/bin/bash
set -o errexit
set -o pipefail

tag_branch() {
    COMMIT_HASH=$(git rev-parse --short HEAD)

    if [ "$CIRCLE_BRANCH" == 'master' ]; then
        IMAGE_TAG=$COMMIT_HASH
    else
        IMAGE_TAG="${CIRCLE_BRANCH}-${COMMIT_HASH}"
    fi
}

authorize_docker() {
    echo "====> Store Sand authenticate with service account"
    echo $GCLOUD_SERVICE_KEY | base64 --decode > ${HOME}/gcloud-service-key.json

    echo "====> Login to docker registry"


    docker login -u _json_key -p "$(cat ${HOME}/gcloud-service-key.json)" https://gcr.io
}

deploy_image() {
    make release

    make tag $IMAGE_TAG

    make publish
}

main() {
    tag_branch
    authorize_docker
    deploy_image
}

main "$@"
