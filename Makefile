PROJECT_NAME := andelasocietiesbackend
REPO_NAME ?= soc-backend
ORG_NAME ?= bench-projects
# File names
DOCKER_TEST_COMPOSE_FILE := docker/test/docker-compose.yml
DOCKER_REL_COMPOSE_FILE := docker/release/docker-compose.yml
DOCKER_DB_COMPOSE_FILE := docker/database/docker-compose.yml
DOCKER_DEV_COMPOSE_FILE := docker/dev/docker-compose.yml

# Docker compose project names
DOCKER_TEST_PROJECT := "$(PROJECT_NAME)test"
DOCKER_REL_PROJECT := "$(PROJECT_NAME)rel"
APP_SERVICE_NAME := app
DOCKER_REGISTRY ?= gcr.io

# Repository Filter
ifeq ($(DOCKER_REGISTRY), docker.io)
	REPO_FILTER := $(ORG_NAME)/$(REPO_NAME)
else
	REPO_FILTER := $(DOCKER_REGISTRY)/$(ORG_NAME)/$(REPO_NAME)[^[:space:]|\$$]*
endif

.PHONY: help


## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo "${YELLOW} make ${RESET} ${GREEN}<target> [options]${RESET}"
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
    	message = match(lastLine, /^## (.*)/); \
		if (message) { \
			command = substr($$1, 0, index($$1, ":")-1); \
			message = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW_S}%-$(TARGET_MAX_CHAR_NUM)s${RESET} %s\n", command, message; \
		} \
	} \
    { lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''

## Generate .env file from the provided sample
env_file:
	@ chmod +x scripts/utils.sh && scripts/utils.sh addEnvFile
	@ echo " "

## Start the backend application
start:status
	@ echo "${YELLOW}====> Building the andela societies backend image.${WHITE}"
	@ docker-compose -f $(DOCKER_DEV_COMPOSE_FILE) build --no-cache backend
	@ echo "${GREEN}====> Image built. Image name is \"soc-backend:sandbox\"${WHITE}"
	@ echo "${YELLOW}====> Carrying out healthchecks on the database${WHITE}"
	@ docker-compose -p soc -f $(DOCKER_DEV_COMPOSE_FILE) run --rm backend psql-h database
	@ echo "${GREEN}====> Database is up${WHITE}"
	@ echo "${YELLOW}====> Upgrading the database${WHITE}"
	@ docker-compose -p soc -f $(DOCKER_DEV_COMPOSE_FILE) run --rm backend python manage.py db upgrade -d prod-stag-migrations
	@ echo "${GREEN}====> Database upgraded${WHITE}"
	@ echo "${YELLOW}====> Starting the application${WHITE}"
	@ docker-compose -p soc -f $(DOCKER_DEV_COMPOSE_FILE) up --force-recreate -d backend
	@ echo "${YELLOW}====> Application is running at \"http://api-soc-sandbox.andela.com:4022/\"${WHITE}"
	@ open http://api-soc-sandbox.andela.com:4022/


## Manage the backend host and checking the frontend application
status:
	@ chmod +x scripts/sandbox.sh && scripts/sandbox.sh checkDocker
	@ echo "${YELLOW}====> Checking the frontend containers${WHITE}"
	@ chmod +x scripts/sandbox.sh && scripts/sandbox.sh checkFrontend
	@ echo "${YELLOW}====> End of frontend check${WHITE}"
	@ echo "${YELLOW}====> Managing host for the backend${WHITE}"
	@ chmod +x scripts/sandbox.sh && scripts/sandbox.sh configureHosts

## Stop the backend application
stop:
	@ echo "${YELLOW}====> Stopping backend and database containers if they are running${WHITE}"
	@ docker-compose -p soc -f $(DOCKER_DEV_COMPOSE_FILE) stop
	@ echo "${YELLOW}====> Removing running containers for the backend if stopped containers exist${WHITE}"
	@ docker-compose -p soc -f $(DOCKER_DEV_COMPOSE_FILE) rm -f
	@ echo "${YELLOW}====> Removing image for the backend application${WHITE}"
	@ docker images -q --filter "reference=soc-backend:sandbox" | xargs -I ARGS docker image rm ARGS
	@ echo "${GREEN}====> Container and image removed.${WHITE}"

## Destroy the application together with the network and postgres database image
tear:stop
	@ echo "${YELLOW}====> Removing postgres image${WHITE}"
	@ docker images -q --filter "reference=postgres:latest" | xargs -I ARGS docker image rm ARGS
	@ echo "${GREEN}====> Postgres image removed.${WHITE}"
	@ echo "${YELLOW}====> Delete shared network for the frontend and the backend.${WHITE}"
	@ docker network ls -q --filter "name=soc_soc-network" | xargs -I ARGS docker network rm ARGS
	@ echo "${GREEN}====> Resources destroyed.${WHITE}"


seed:
	@ docker exec -it soc_backend_1 python manage.py seed
	@ docker exec -it soc_backend_1 ./manage.py link_society_cohort_csv_data


## Upgrade the application database
upgrade:
	@ echo "${YELLOW}====> Building the docker images${WHITE}"
	@ docker-compose -f $(DOCKER_DB_COMPOSE_FILE) build
	@ echo "${GREEN}====> Images built${WHITE}"
	@ echo "${YELLOW}====>Running database containers in the background${WHITE}"
	@ docker-compose -f $(DOCKER_DB_COMPOSE_FILE) run -d --name  database database
	@ docker-compose -f $(DOCKER_DB_COMPOSE_FILE) run --name  application application python manage.py db upgrade -d prod-stag-migrations 
	@ echo "${GREEN}====>Application migrated${WHITE}"
	@ docker-compose -f $(DOCKER_DB_COMPOSE_FILE) down -v --rmi all
	@ echo "${GREEN}====>Migration images, containers and networks cleared${WHITE}"

## Destroy services and images built for migration
upgrade-destroy:
	@ echo "${YELLOW}====>Stoping any running container with the name application or database${WHITE}"
	@ docker container ps -q --filter "name=database" --filter "name=application" | xargs -I ARGS docker container stop ARGS
	@ echo "${GREEN}====>Containers with the name application and database stopped"
	@ echo "${YELLOW}====>Deleting containers with the name application or database${WHITE}"
	@ docker container ps -aq --filter "name=database" --filter "name=application" | xargs -I ARGS docker container rm ARGS
	@ echo "${GREEN}====>Containers with the name application or database removed"	
	@ echo "${YELLOW}====>Deleting networks with the name database_migration${WHITE}"
	@ docker network ls --filter "name=database_migration" -q | xargs -I ARGS docker network rm ARGS
	@ echo "${GREEN}====>Networks with the name migration-net deleted${WHITE}"
	@ docker images -f "reference=application:migration" -q | xargs -I ARGS docker image rmi -f ARGS
	@ docker images -f "reference=database:migration" -q | xargs -I ARGS docker image rmi -f ARGS

## Run project test cases
test:env_file
	${INFO} "Creating cache docker volume"
	@ echo " "
	@ docker volume create --name=cache > /dev/null
	${INFO} "Building required docker images for testing"
	@ echo " "
	@ docker-compose -p $(DOCKER_TEST_PROJECT) -f $(DOCKER_TEST_COMPOSE_FILE) build --pull test
	${INFO} "Build Completed successfully"
	@ echo " "
	@ ${INFO} "Running tests in docker container"
	@ docker-compose -p $(DOCKER_TEST_PROJECT) -f $(DOCKER_TEST_COMPOSE_FILE) up test
	${INFO}"Copying test coverage reports"
	@ bash -c 'if [ -d "test-reports" ]; then rm -Rf test-reports; fi'
	@ docker cp $$(docker-compose -p $(DOCKER_TEST_PROJECT) -f $(DOCKER_TEST_COMPOSE_FILE) ps -q test):/application/htmlcov test-reports
	@ ${INFO} "Cleaning workspace after test"
	@ docker-compose -p $(DOCKER_TEST_PROJECT) -f $(DOCKER_TEST_COMPOSE_FILE) down -v

## Build project image
release:env_file
	${INFO} "Building required container image for the application"
	@ echo " "
	@ docker-compose -p $(DOCKER_REL_PROJECT) -f $(DOCKER_REL_COMPOSE_FILE) build app
	@ docker-compose -p $(DOCKER_REL_PROJECT) -f $(DOCKER_REL_COMPOSE_FILE) run -d app

## Tag the project image
tag:
	${INFO} "Tagging release image with tags $(TAG_ARGS)..."
	@ $(foreach tag,$(TAG_ARGS), docker tag $(IMAGE_ID) $(DOCKER_REGISTRY)/$(ORG_NAME)/$(REPO_NAME):$(tag);)
	${SUCCESS} "Tagging complete"

## publish images to GCP or dockerhub.
publish:
	${INFO} "Publishing release image $(IMAGE_ID) to $(DOCKER_REGISTRY)/$(ORG_NAME)/$(REPO_NAME)..."
	@ $(foreach tag,$(shell echo $(REPO_EXPR)), docker push $(tag);)
	${INFO} "Publish complete"

## Destroy test environments
destroy:
	${INFO} "Destroying test environment..."
	@ docker-compose -p $(DOCKER_TEST_PROJECT) -f $(DOCKER_TEST_COMPOSE_FILE) down -v
	${INFO} "Removing dangling images..."
	@ docker images -q -f dangling=true -f label=application=$(REPO_NAME) | xargs -I ARGS docker rmi -f ARGS
	${SUCCESS} "Clean complete"

ifeq (tag,$(firstword $(MAKECMDGOALS)))
  TAG_ARGS := $(word 2, $(MAKECMDGOALS))
  ifeq ($(TAG_ARGS),)
    $(error You must specify a tag)
  endif
  $(eval $(TAG_ARGS):;@:)
endif

  # COLORS
GREEN  := `tput setaf 2`
YELLOW := `tput setaf 3`
WHITE  := `tput setaf 7`
YELLOW_S := $(shell tput -Txterm setaf 3)
NC := "\e[0m"
RESET  := $(shell tput -Txterm sgr0)
# Shell Functions
INFO := @bash -c 'printf $(YELLOW); echo "===> $$1"; printf $(NC)' SOME_VALUE
SUCCESS := @bash -c 'printf $(GREEN); echo "===> $$1"; printf $(NC)' SOME_VALUE

APP_CONTAINER_ID := $$(docker-compose -p $(DOCKER_REL_PROJECT) -f $(DOCKER_REL_COMPOSE_FILE) ps -q $(APP_SERVICE_NAME))

IMAGE_ID := $$(docker inspect -f '{{ .Image }}' $(APP_CONTAINER_ID))

# Introspect repository tags
REPO_EXPR := $$(docker inspect -f '{{range .RepoTags}}{{.}} {{end}}' $(IMAGE_ID) | grep -oh "$(REPO_FILTER)" | xargs)
