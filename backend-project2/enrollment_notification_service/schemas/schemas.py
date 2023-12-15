from pydantic import BaseModel

class Contacts(BaseModel):
    webhook: str
    email: str