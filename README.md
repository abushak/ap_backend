# Autoparts
## TOC
* [Requirements](#requirements)
* [Setup](#setup)
* [Services](#services)
* [Notes](#notes)

## Requirements
* Docker: 19.03
* Docker compose:  1.27
	
## Setup
**Create `.env` file**
```
$ cp ./envs/.env.example ./envs/.env
```
___
**Build services**
```
$ docker-compose build
```
___
**Run project**
```
$ docker-compose up -d
```
___
**Create superuser**
```
$ docker-compose exec app ./manage.py createsuperuser
```
___
**Create eBay credential**
```
$ docker-compose exec app ./manage.py ebay_create_credential APP_ID
```
___
**Create Google Service Account & GCS**

Create Google Service Account with Google Cloud Storage permissions.
Export GSA JSON and put into project's folder. Add `GOOGLE_SERVICE_ACCOUNT_FILEPATH` to `.env`.
Create Google Storage Bucket and add the name of bucket to `GS_BUCKET_NAME` into `.env`.

## Services
* [App](http://127.0.0.1:8000/admin)
    * Username & password that you've created with `createsuperuser` command
* [pgAdmin](http://127.0.0.1:5050)
    * email: `autoparts@localhost`
    * password: `autoparts`
* [Hasura GraphQL Engine](http://127.0.0.1:8080)
    * admin secret: `password`
* [Flower](http://127.0.0.1:8888)

## Sentry
Application supports Sentry. Just add `SENTRY_DSN` variable with DSN provided by Sentry on installation step.

## Notes
Migrations and management commands

`migrate` and `collectstatic` triggered from [entrypoint](./app/entrypoint.sh). For manual usage - run management commands via `docker-compose exec app`\
*Example: `docker-compose exec app ./manage.py makemigrations`*
