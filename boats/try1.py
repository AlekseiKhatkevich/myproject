import subprocess

import os
from myproject.development_settings import BASE_DIR
from functools import reduce
from django.utils.text import slugify
"""
process = subprocess.Popen("aws s3 ls s3://boatsprojectdevelopmentbucket", stdout=subprocess.PIPE)
data = process.communicate()
for line in data:
    print(line)
"""

print(slugify("Najad/Aphrodite 33"))
