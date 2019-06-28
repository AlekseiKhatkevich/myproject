web: gunicorn myproject.wsgi --log-file -
worker:  celery -A myproject worker --pool=solo -l info
beat:  celery -A myproject beat
