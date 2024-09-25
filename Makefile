crawl-locally:
	docker run --rm -v ${PWD}:/data \
		-w /data --entrypoint bash \
		webis/tira:tira-data-0.0.1 \
		-c 'python3 data/create-static-page.py /dist && mv /dist data/dist'
