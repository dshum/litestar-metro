# litestar-metro

## Local development

Install pdm, nodejs and npm if needed.

Copy and edit .env:

```commandline
cp .env.example .env
```

Install the assets:

```commandline
make install-assets
```

Run the application in development mode:

```commandline
make dev
```

Run the application in prod mode:

```commandline
make run
```

Create a user after the application creates the sqlite file:

```commandline
make create-user
```

### Translations

Extract messages from files:

```commandline
make extract-messages
```

Update files .po:

```
make update-messages
```

Edit files .po and then compile translations:

```commandline
make compile-messages
```

## Deployment

Make sure you have pdm, nodejs and npm installed.

Install python environment:

```commandline
pdm install
```

Compile translations:

```commandline
make compile-messages
```

Build the assets:

```commandline
make build
```

Run docker:

```commandline
docker compose up -d
```

Create a user after the application creates the sqlite file:

```commandline
make create-user
```
