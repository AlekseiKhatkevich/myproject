web: gunicorn myproject.wsgi --log-file -
worker: celery -A myproject worker --pool=solo -l info
worker: celery -A myproject beat
