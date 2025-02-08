include .env

APP_PORT := $(or $(APP_PORT), 8000)

dev:
	pdm run litestar --app=app.main:app run --port=$(APP_PORT) --reload

run:
	make build && APP_DEBUG=False VITE_DEV_MODE=False pdm run litestar --app=app.main:app run --port=$(APP_PORT)

build:
	pdm run litestar --app=app.main:app assets build

flush:
	pdm run litestar --app=app.main:app metro flush

create:
	pdm run litestar --app=app.main:app metro create

create-user:
	pdm run litestar --app=app.main:app users create