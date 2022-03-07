clean: stop remove-files

all: clean pull build start

pull:
	docker-compose pull

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

remove-files:
	docker system prune -a
	docker volume prune

logs:
	watch docker-compose logs


