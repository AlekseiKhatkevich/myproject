web: gunicorn myproject.wsgi --log-file -
worker:  celery worker --without-gossip --without-mingle --loglevel=info
beat:  celery beat –loglevel=info
