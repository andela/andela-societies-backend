#!/bin/bash

set -o errexit
set -o pipefail
 
coverage run -m pytest -v
coverage html
coveralls

exec $@
