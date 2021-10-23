.PHONY: set-env show-env install
include .env
export

#This doesn't set the env outside of the make process, just use this which will echo the command, then you can copy and run it manually
set-env:
	set -o allexport && source .env && set +o allexport

show-env:
	env |grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY'

install:
	brew install terraform