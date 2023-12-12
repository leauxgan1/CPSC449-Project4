import contextlib
import enrollment_service.query_helper as qh
import redis

from fastapi import Depends, HTTPException, APIRouter, Header, status
import boto3
from enrollment_service.database.schemas import Class

router = APIRouter()
dropped = []

FREEZE = False
MAX_WAITLIST = 3
database = "enrollment_service/database/database.db"
dynamodb_client = boto3.client('dynamodb', endpoint_url='http://localhost:5500')
table_name = 'TitanOnlineEnrollment'
r = redis.Redis()

@router.post("/subscribe/{student_id}/classes/{class_id}")
def subscribe_student_to_course(student_id: str, class_id: str):
    # Check if student exists in the database
    student_data = qh.query_student(dynamodb_client, student_id)
    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student found")
    
    # Check if class exists in the database
    class_data = qh.check_class_exists(dynamodb_client, class_id)
    if not class_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No class found")
    
    subscription_key = f"subscription:{student_id}"

    if not r.exists(subscription_key):
        r.rpush(subscription_key, f"c#{class_id}")
        return {"message": "Student added to subscription"}
    else:
        id = f"s#{student_id}".encode('uft-8')
        if id in r.lrange(subscription_key, 0, -1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student is already subscribed")
        r.rpush(subscription_key, f"c#{class_id}")

    return {"message": "Studented subscribed to class"}

# DONE: GET currently enrolled classes for a student
@router.get("/students/{student_id}/subscriptions", tags=['Student'])
def get_student_subscriptions(student_id: str):
    # Check if student exists in the database
    student_data = qh.query_student(dynamodb_client, student_id)
    if not student_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student found")
    
    subscription_key = f"s#{student_id}"
    subscriptions = r.lrange(subscription_key, 0, -1)

    if not subscriptions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No subscriptions found")

    return {"Subscriptions": subscriptions}
