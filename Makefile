ADMIN_EMAIL ?= admin@tinga.io
ADMIN_USERNAME ?= admin
ADMIN_PASSWORD ?= abram.space

serve: migrate
	./manage.py runserver

prepare: 
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "setup is done. Run '. venv/bin/activate' to enter the virtual environment"

migrate:
	./manage.py makemigrations
	./manage.py migrate

initdb: 
	psql postgres < resetdb.sql

superuser:
	DJANGO_SUPERUSER_PASSWORD=$(ADMIN_PASSWORD) ./manage.py createsuperuser \
		 --username $(ADMIN_USERNAME) \
		 --email $(ADMIN_EMAIL) --noinput

reset-migrations:
	rm -vfr registry/migrations/00*.py

reset: initdb reset-migrations migrate superuser serve

requirements:
	pip freeze > requirements.txt
