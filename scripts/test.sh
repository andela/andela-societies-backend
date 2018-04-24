#!/bin/bash
 
coverage run -m pytest -v
coverage html
coveralls

exec $@
