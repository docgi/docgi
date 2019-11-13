compose:
	docker-compose up -d

runserver:
	./manage.py runserver 8008

test:
	./manage.py test --keepdb --settings=configs.settings.test

