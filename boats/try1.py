import subprocess
from django.conf import settings
import os
from myproject.development_settings import BASE_DIR
from functools import reduce
"""
process = subprocess.Popen("aws s3 ls s3://boatsprojectdevelopmentbucket", stdout=subprocess.PIPE)
data = process.communicate()
for line in data:
    print(line)
"""
line  = "-/boats/?ordering=boat_length&mark=descending"
a = line.split("=")
del a[0]
a[0] = a[0][ : -5]
print(a)
#  ['boat_length', 'descending']
