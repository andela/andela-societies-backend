#!/bin/bash
 
coverage run manage.py test
coveralls

exec $@
