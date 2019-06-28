web: gunicorn myproject.wsgi --log-file -; celery -A myproject worker --pool=solo -l info; celery -A myproject beat
