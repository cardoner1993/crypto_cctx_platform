# COMPOSE EXECUTION
export CURRENT_UID=$(id -u):$(id -g)
compose_up: ## Start the composer
	$(shell mkdir -p grafana influxdb)
ifeq ($(ACTION), build)
	docker-compose -f $(COMPOSE) up --build -d
else
	docker-compose -f $(COMPOSE) up -d
endif

compose_down: ##Push the image to a repository
	docker-compose down
