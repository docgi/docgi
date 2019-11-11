compose:
	docker-compose up -d

runserver:
	./manage.py runserver

test:
	./manage.py test --keepdb --settings=configs.settings.test

