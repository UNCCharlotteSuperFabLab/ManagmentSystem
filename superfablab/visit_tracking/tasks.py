from .models import Visit

from celery import shared_task

import os
from typing import List, Dict

@shared_task()
def add(x, y):
    return x + y
    