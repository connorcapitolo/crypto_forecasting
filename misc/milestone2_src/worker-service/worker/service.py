import os
import traceback
import asyncio
import functools

import datacollector.session as celery_session

# Celery Worker
worker = celery_session.worker
