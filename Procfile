web: gunicorn myproject.wsgi --log-file -
worker:  python manage.py  celery -A myproject worker --pool=solo -l info
celery_beat: python manage.py  celery -A myproject beat
