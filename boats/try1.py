import subprocess
import os

from boats.utilities import *
from django.conf import settings
"""
process = subprocess.Popen("aws s3 ls s3://boatsprojectdevelopmentbucket", stdout=subprocess.PIPE)
data = process.communicate()
for line in data:
    print(line)
"""
def True_or_False(_tuple):
    return _tuple[0] == _tuple[1]
