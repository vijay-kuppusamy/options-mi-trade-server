from base.tasks import sample_task

from celery.result import AsyncResult

def run():
    try:
        print("Test Run")

        AsyncResult('7f7059f3-d4d1-4553-a790-b23b6b905391').revoke(terminate=True)

        print("Test End")
    except Exception as e:
        print(e)    
