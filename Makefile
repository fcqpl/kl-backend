
ON_BACKEND_EXEC=docker-compose exec kl-backend

reset_db:
	${ON_BACKEND_EXEC} bash -c 'echo "DROP SCHEMA public cascade; CREATE SCHEMA public" | python manage.py dbshell'
	${ON_BACKEND_EXEC} python manage.py migrate
	${ON_BACKEND_EXEC} python manage.py dbseed

clean_env:
	docker-compose down --volumes --rmi all --remove-orphans

