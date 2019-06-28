web: gunicorn myproject.wsgi --log-file -; -A myproject worker --pool=solo -l info; celery -A myproject beat
