
from celery import shared_task
import time


@shared_task
def simple_task(name):
    print(f'Starting task for {name}')
    time.sleep(5)
    print(f'Finished task for {name}')
    
    return f"Task completed for {name}"