#!/bin/bash -exu
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}/root/"

# Add your configuration here:
# ...

# Tool start:
exec /usr/bin/python3 -m qmenta.sdk.executor "$@"
