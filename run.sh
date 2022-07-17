#!/usr/bin/env bash

set -a
source .env
set +a

python3  pull_newsletters_and_send.py
pushd /tmp/newsletters
$HOME/dev/personal/inbox2remarkable/rmapi mput /Newsletters
rm -r /tmp/newsletters
