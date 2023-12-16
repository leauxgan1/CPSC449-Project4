import contextlib
import enrollment_service.query_helper as qh
import redis
from enrollment_notification_service.schemas.schemas import Contacts

from fastapi import Depends, HTTPException, APIRouter, Header, status
import boto3
from enrollment_service.database.schemas import Class

router = APIRouter()
dropped = []

FREEZE = False
dynamodb_client = boto3.client('dynamodb', endpoint_url='http://localhost:5500')
r = redis.Redis()

@router.post("/subscriptions/subscribe/{student_id}/{class_id}")
def subscribe_student_to_course(student_id: str, class_id: str, user_data : Contacts):
    # Check if student exists in the database
    student_data = qh.query_student(dynamodb_client, student_id)
    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified student not found")
    
    # Check if class exists in the database
    class_data = qh.check_class_exists(dynamodb_client, class_id)
    if not class_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified class not found")
    
    subscription_key = f"subscription:{student_id}"

    if not r.exists(subscription_key):
        r.rpush(subscription_key, f"c#{class_id}")
        return {"message": "Student added to subscription for class {}".format(class_id)}
    else:
        id = f"c#{class_id}".encode('utf-8')
        if id in r.lrange(subscription_key, 0, -1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student is already subscribed to class {}".format(class_id))
        r.rpush(subscription_key, f"c#{class_id}")


    return {"message": "Studented subscribed to class {}".format(class_id)}

@router.post("/subscriptions/unsubscribe/{student_id}/{class_id}")
def unsubscribe_student_from_course(student_id: str, class_id: str):
    student_data = qh.query_student(dynamodb_client,student_id)
    
    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Specified student not found")
    
    subscription_key = f"subscription:{student_id}"

    if r.exists(subscription_key):
        id = f"c#{class_id}".encode('utf-8')
        if id in r.lrange(subscription_key, 0, -1):
            r.lrem(subscription_key,1, f"c#{class_id}")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student is not subscribed to this class's notifications")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student is not subscribed to any class notifications")
    
    return {"message": "Studented unsubscribed from class {}".format(class_id)}

@router.get("/subscriptions/{student_id}", tags=['Student'])
def get_student_subscriptions(student_id: str):
    # Check if student exists in the database
    student_data = qh.query_student(dynamodb_client, student_id)
    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student found")
    
    subscription_key = f"subscription:{student_id}"
    subscriptions = r.lrange(subscription_key, 0, -1)

    print(type(subscriptions))

    if not subscriptions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscriptions found")

    return {"Subscriptions": subscriptions}
