#!/usr/bin/env bash

set -a
source .env
set +a

python3  pull_newsletters_and_send.py
