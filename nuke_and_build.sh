#!/usr/bin/env bash

rm -rf hotdoc-private static/html && \
	hotdoc --output static/html run --conf-file ~/devel/test_hotdoc/hotdoc.json && \
	python hotdoc_server.py run --conf-file ~/devel/test_hotdoc/hotdoc.json
