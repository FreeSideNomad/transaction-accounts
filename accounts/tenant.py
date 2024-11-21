from pydantic import BaseModel

class Tenant(BaseModel):
    name: str
    label: str
    parent: str = None
    is_active: bool = True
