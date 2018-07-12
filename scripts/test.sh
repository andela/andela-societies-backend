#!/bin/bash

set -o errexit
set -o pipefail

/etc/init.d/rabbitmq-server start 
coverage run -m pytest -v
coverage html
coveralls

exec $@
