python3 /home/docker/code/app/manage.py makemigrations
python3 /home/docker/code/app/manage.py migrate

python3 /home/docker/code/app/manage.py rabbit_receive &
exec "$@"