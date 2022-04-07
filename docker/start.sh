#!/bin/bash

set -e

./m makemigrations --merge  --no-input --traceback
./m migrate  --no-input --traceback
./m collectstatic --no-input --traceback

