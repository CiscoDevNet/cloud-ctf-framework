#!/bin/bash
# Must run these commands from shell manually, running this script won't do anything since it invokes a new shell, set env in that, then is destroyed.
set -o allexport && source .env && set +o allexport
#To unset env vars run below
#unset $(grep -v '^#' .env | sed -E 's/(.*)=.*/\1/' | xargs)