import subprocess
import os
import inspect
"""
process = subprocess.Popen("aws s3 ls s3://boatsprojectdevelopmentbucket", stdout=subprocess.PIPE)
data = process.communicate()
for line in data:
    print(line)
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings


def invalidate_cached_lookup(**kwargs):
    cache_key = 'BoatListView'
    cache.delete(cache_key)
settings.configure()
invalidate_cached_lookup()
