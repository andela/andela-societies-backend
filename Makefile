PROJECT_NAME := andelasocietiesbackend
REPO_NAME ?= soc-backend
ORG_NAME ?= bench-projects
# File names
DOCKER_TEST_COMPOSE_FILE := docker/test/docker-compose.yml
DOCKER_REL_COMPOSE_FILE := docker/release/docker-compose.yml

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
	@echo '${YELLOW} make ${RESET} ${GREEN}<target> [options]${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
    	message = match(lastLine, /^## (.*)/); \
		if (message) { \
			command = substr($$1, 0, index($$1, ":")-1); \
			message = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} %s\n", command, message; \
		} \
	} \
    { lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''
    
## Generate .env file from the provided sample
env_file:
	@ chmod +x scripts/utils.sh && scripts/utils.sh addEnvFile
	@ echo " "

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
	${INFO} "Clean complete"

ifeq (tag,$(firstword $(MAKECMDGOALS)))
  TAG_ARGS := $(word 2, $(MAKECMDGOALS))
  ifeq ($(TAG_ARGS),)
    $(error You must specify a tag)
  endif
  $(eval $(TAG_ARGS):;@:)
endif

  # COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
NC := "\e[0m"
RESET  := $(shell tput -Txterm sgr0)
# Shell Functions
INFO := @bash -c 'printf $(YELLOW); echo "===> $$1"; printf $(NC)' SOME_VALUE
SUCCESS := @bash -c 'printf $(GREEN); echo "===> $$1"; printf $(NC)' SOME_VALUE

APP_CONTAINER_ID := $$(docker-compose -p $(DOCKER_REL_PROJECT) -f $(DOCKER_REL_COMPOSE_FILE) ps -q $(APP_SERVICE_NAME))

IMAGE_ID := $$(docker inspect -f '{{ .Image }}' $(APP_CONTAINER_ID))

# Introspect repository tags
REPO_EXPR := $$(docker inspect -f '{{range .RepoTags}}{{.}} {{end}}' $(IMAGE_ID) | grep -oh "$(REPO_FILTER)" | xargs)
