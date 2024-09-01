#!make

build-docker:
	docker build -t flask-app .

run:
	docker-compose up -d

logs:
	@container_id=$$(docker ps | grep "web" | awk '{print $$1}'); \
	if [ -n "$$container_id" ]; then \
		echo "Attaching to logs of container $$container_id..."; \
		docker logs $$container_id --follow; \
	else \
		echo "No container found for 'web'."; \
	fi

stop:
	docker-compose stop
