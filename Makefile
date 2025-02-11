include .env

APP_PORT := $(or $(APP_PORT), 8000)

# application
install-assets:
	pdm run litestar --app=app.main:app assets install
dev:
	pdm run litestar --app=app.main:app run --port=$(APP_PORT) --reload
run:
	make build && APP_DEBUG=False VITE_DEV_MODE=False pdm run litestar --app=app.main:app run --port=$(APP_PORT)
build:
	pdm run litestar --app=app.main:app assets build

# console commands
flush:
	pdm run litestar --app=app.main:app metro flush
create:
	pdm run litestar --app=app.main:app metro create
create-user:
	pdm run litestar --app=app.main:app users create

# translations
init-messages:
	pdm run pybabel init -i messages.pot -d app/translations -l ru
extract-messages:
	pdm run pybabel extract -F babel.cfg -o messages.pot .
update-messages:
	pdm run pybabel update -i messages.pot -d app/translations
compile-messages:
	pdm run pybabel compile -d app/translations