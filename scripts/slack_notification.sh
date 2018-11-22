#!/usr/bin/env bash

set -o errexit
set -o pipefail


deploy_env_variables() {
    MESSAGE_COLOR="$1"

    if [ "$MESSAGE_COLOR" == "good" ]; then
      MESSAGE_TEXT="The $CIRCLE_BRANCH branch has been deployed to the $ENVIRONMENT environment"
    elif [ "$MESSAGE_COLOR" == "danger" ]; then
      MESSAGE_TEXT="Deployment to $ENVIRONMENT failed!!!"
    else
      echo "Warning!: $MESSAGE_COLOR is not a color that was expected to be provided"
    fi

}


upgrade_env_variables() {
    MESSAGE_COLOR="$1"

    if [ "$MESSAGE_COLOR" == "good" ]; then
      MESSAGE_TEXT="$ENVIRONMENT database was upgraded successfully"
    elif [ "$MESSAGE_COLOR" == "danger" ]; then
      MESSAGE_TEXT="$ENVIRONMENT database upgrade failed!!!"
    else
      echo "Warning!: $MESSAGE_COLOR is not a color that was expected to be provided"
    fi
}


declare_env_variables() {

  # Declaring environment variables
  #
  # Some environment variables assigned externally are:
  # SLACK_CHANNEL_HOOK : This is the webhook for the Slack App where notifications will be sent from
  # DEPLOYMENT_CHANNEL : This is the channel on which the Slack notifications will be posted
  # Some template for the Slack message

  if [ "$CIRCLE_BRANCH" == "master" ]; then
      ENVIRONMENT="Production"
  else
      ENVIRONMENT="Staging"
  fi

  if [ "$CIRCLE_JOB" == "upgrade-database" ]; then
    upgrade_env_variables "$@"
  fi

  if [ "$CIRCLE_JOB" == "deploy" ]; then
    deploy_env_variables "$@"
  fi

  COMMIT_LINK="https://github.com/${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}/commit/${CIRCLE_SHA1}"
  IMG_TAG="$(git rev-parse --short HEAD)"
  CIRCLE_WORKFLOW_URL="https://circleci.com/workflow-run/${CIRCLE_WORKFLOW_ID}"
  SLACK_TEXT_TITLE="CircleCI Build #$CIRCLE_BUILD_NUM"
  SLACK_DEPLOYMENT_TEXT="Executed Git Commit <$COMMIT_LINK|${IMG_TAG}>: ${MESSAGE_TEXT}"
}

send_notification() {

  # Sending the Slack notification

  curl -X POST --data-urlencode \
  "payload={
      \"channel\": \"${DEPLOYMENT_CHANNEL}\",
      \"username\": \"JobNotification\",
      \"attachments\": [{
          \"fallback\": \"CircleCI job notification\",
          \"color\": \"${MESSAGE_COLOR}\",
          \"author_name\": \"Branch: $CIRCLE_BRANCH by ${CIRCLE_USERNAME}\",
          \"author_link\": \"https://github.com/AndelaOSP/andela-societies-backend/tree/${CIRCLE_BRANCH}\",
          \"title\": \"${SLACK_TEXT_TITLE}\",
          \"title_link\": \"$CIRCLE_WORKFLOW_URL\",
          \"text\": \"${SLACK_DEPLOYMENT_TEXT}\"
      }]
  }" \
  "${SLACK_CHANNEL_HOOK}"
}

main() {
  echo "Declaring environment variables"
  declare_env_variables "$@"

  echo "Sending notification"
  send_notification
}

main "$@"
