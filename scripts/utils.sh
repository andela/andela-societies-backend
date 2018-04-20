#!/usr/bin/env bash
DIRECTORY="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

ROOT_DIRECTORY=$(dirname $DIRECTORY)

# colors
red=$(tput setaf 1)
green=$(tput setaf 76)
tan=$(tput setaf 3)

success() {
  printf "${green}===> %s${reset}\n" "$@"
}

error() {
  printf "${red}===> %s${reset}\n" "$@"
}

warning() {
  printf "${tan}===> %s${reset}\n" "$@"
}

function addEnvFile() {
    ENV_FILE=$ROOT_DIRECTORY/src/.env
    SAMPLE_ENV_FILE=$ROOT_DIRECTORY/src/.env.sample
    warning "Adding .env file to flask project directory"
    echo " "

    if [ ! -f "$ENV_FILE" ]; then
        cat $SAMPLE_ENV_FILE > $ENV_FILE
        success "lsEnvironment file has been created successfully"
        return
    fi

    warning "Skipping, Environment file already exist"
}

"$@"
