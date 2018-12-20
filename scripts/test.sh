#!/bin/bash

set -x
set -o errexit
set -o pipefail

coverage run -m pytest -v
coverage html
COVERALLS_REPO_TOKEN=${COVERALLS_REPO_TOKEN} coveralls

exec "$@"
