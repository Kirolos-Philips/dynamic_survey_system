.PHONY: build up down logs migrate makemigrations shell createsuperuser seed-surveys test lint bash help

# Default environment
ENV ?= local

ifeq ($(ENV), production)
    COMPOSE_FILE := compose/production.yml
else
    COMPOSE_FILE := compose/local.yml
endif

DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE)
# Use 'exec' for running containers
DJ := $(DOCKER_COMPOSE) exec django

# This magic block allows passing arguments directly to commands
# It treats everything after the command as a target and silences "nothing to be done"
ifeq ($(firstword $(MAKECMDGOALS)),$(filter $(firstword $(MAKECMDGOALS)),build up down logs migrate makemigrations test shell createsuperuser seed-surveys lint bash))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(RUN_ARGS):;@:)
endif

help:
	@echo "Usage: make [target] [ENV=production|local] [arguments...]"
	@echo ""
	@echo "Examples:"
	@echo "  make migrate auth          (runs 'python manage.py migrate auth')"
	@echo "  make test surveys.tests    (runs 'python manage.py test surveys.tests')"
	@echo "  make logs django           (runs 'docker compose logs -f django')"
	@echo ""
	@echo "Targets:"
	@echo "  build            Build or rebuild services"
	@echo "  up               Create and start containers"
	@echo "  down             Stop and remove containers"
	@echo "  logs [service]   View output from containers"
	@echo "  migrate [args]   Run database migrations"
	@echo "  makemigrations   Create new database migrations"
	@echo "  shell            Run a Python interactive interpreter"
	@echo "  createsuperuser  Create a superuser"
	@echo "  test [args]      Run tests"
	@echo "  lint             Run ruff linter"
	@echo "  seed-surveys     Populate DB with example surveys"
	@echo "  bash             Open a bash shell in the django container"

build:
	$(DOCKER_COMPOSE) build $(RUN_ARGS)

rebuild:
	$(DOCKER_COMPOSE) build --no-cache $(RUN_ARGS)

up:
	$(DOCKER_COMPOSE) up -d $(RUN_ARGS)

down:
	$(DOCKER_COMPOSE) down $(RUN_ARGS)

restart:
	$(DOCKER_COMPOSE) restart $(RUN_ARGS)

logs:
	$(DOCKER_COMPOSE) logs -f $(RUN_ARGS)

migrate:
	$(DJ) /entrypoint python manage.py migrate $(RUN_ARGS)

makemigrations:
	$(DJ) /entrypoint python manage.py makemigrations $(RUN_ARGS)

shell:
	$(DJ) /entrypoint python manage.py shell $(RUN_ARGS)

createsuperuser:
	$(DJ) /entrypoint python manage.py createsuperuser

test:
	$(DJ) /entrypoint python manage.py test $(RUN_ARGS)

lint:
	$(DJ) ruff check . $(RUN_ARGS)

seed-surveys:
ifneq ($(ENV), local)
	@printf "\033[0;31mError: seed-surveys can only be run in the local environment.\033[0m\n"
	@exit 1
endif
	$(DJ) /entrypoint python manage.py seed_surveys

bash:
	$(DJ) /bin/bash $(RUN_ARGS)
