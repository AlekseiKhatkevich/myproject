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
line  = "60*60*24*7"
result = reduce((lambda x, y: int(x) * int(y)), line.split("*"))
print(result)
print(type(result))
