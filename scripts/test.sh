#!/bin/bash

set -o errexit
set -o pipefail

rabbitmq-server &
coverage run -m pytest -v
coverage html
coveralls

exec $@
