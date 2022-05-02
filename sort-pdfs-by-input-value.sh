#!/bin/bash

docker run -v ${PWD}:/data -w /data -u $(id -u) sort_pdf "$@"