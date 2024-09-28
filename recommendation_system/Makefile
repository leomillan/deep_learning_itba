#!make

build:
	docker-compose build

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

shell:
	@container_id=$$(docker ps | grep "web" | awk '{print $$1}'); \
	if [ -n "$$container_id" ]; then \
		docker exec -it $$container_id sh; \
	else \
		echo "No container found for 'web'."; \
	fi

stop:
	docker-compose stop

train:
	@container_id=$$(docker ps | grep "web" | awk '{print $$1}'); \
	if [ -n "$$container_id" ]; then \
		docker exec -it $$container_id bash -c 'cd model && PYTHONPATH=.. python run_train.py'; \
	else \
		echo "No container found for 'web'."; \
	fi

load_sql:
	@container_id=$$(docker ps | grep "web" | awk '{print $$1}'); \
	if [ -n "$$container_id" ]; then \
		docker exec -it $$container_id bash -c 'cd data && PYTHONPATH=.. python load_data.py'; \
	else \
		echo "No container found for 'web'."; \
	fi

load_embeddings:
	@container_id=$$(docker ps | grep "web" | awk '{print $$1}'); \
	if [ -n "$$container_id" ]; then \
		docker exec -it $$container_id bash -c 'cd data && PYTHONPATH=.. python load_embeddings.py'; \
	else \
		echo "No container found for 'web'."; \
	fi
