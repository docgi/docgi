compose:
	docker-compose up -d

runserver:
	./manage.py runserver 8008

test:
	./manage.py test --keepdb --settings=configs.settings.test

static:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --exclude=**/migrations/,configs/settings --statistics

