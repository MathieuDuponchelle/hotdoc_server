#!/usr/bin/env bash

rm -rf hotdoc-private static/html && \
	hotdoc --output static/html --editing-server http://dev.example.com:5055 run --conf-file $1 && \
	python hotdoc_server.py --output static/html --editing-server http://dev.example.com:5055 run --conf-file $1
