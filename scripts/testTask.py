from base.tasks import sample_task

from celery.result import AsyncResult

def run():
    try:
        print("Test Run")
        
        result = sample_task.delay({"time": "12:00", "id":"3"})
        print(result.id)

        print("Test End")
    except Exception as e:
        print(e)    
