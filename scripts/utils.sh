#!/usr/bin/env bash
DIRECTORY="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

ROOT_DIRECTORY=$(dirname $DIRECTORY)

# colors
red=$(tput setaf 1)
green=$(tput setaf 76)
tan=$(tput setaf 3)
white=$(tput setaf 7)

success() {
  printf "${green}===> %s${reset}\n" "$@"
}

error() {
  printf "${red}===> %s${reset}\n" "$@"
}

warning() {
  printf "${tan}===> %s${reset}\n" "$@"
}

reset(){
  printf "${white}"
}

function addEnvFile() {
    ENV_FILE=$ROOT_DIRECTORY/src/.env
    warning "Adding .env file to flask project directory"
    echo " "

    if [ ! -f "$ENV_FILE" ]; then
          cat <<EOF >> ${ROOT_DIRECTORY}/src/.env
PRIVATE_KEY_TEST=${PRIVATE_KEY_TEST}
PUBLIC_KEY_TEST=${PUBLIC_KEY_TEST}
SENDER_CREDS=${SENDER_CREDS}
SLACK_API_TOKEN=${SLACK_API_TOKEN}

EOF
        success "lsEnvironment file has been created successfully"
        return
    fi

    warning "Skipping, Environment file already exist"
    reset
}

"$@"
