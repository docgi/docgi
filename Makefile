start-docker:
	docker-compose -f docker-compose-local.yml up -d

runserver:
	docker-compose -f docker-compose-local.yml up -d
	./manage.py runserver 8008 --settings=configs.settings.local

keepdb_test:
	./manage.py test --keepdb --settings=configs.settings.test

test:
	./manage.py test --settings=configs.settings.test

check-static:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --exclude=**/migrations/,configs/settings --statistics

e_nv:
	/bin/bash source virutal_env/bin/activate;

