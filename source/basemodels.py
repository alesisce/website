from pydantic import BaseModel

class APILogin(BaseModel):
    username: str
    password: str

class ModifyProject(BaseModel):
    progress: int
    status: str
    priority: int
    description: str
    milestones: dict

class CreateProject(BaseModel):
    name: str
    author: str
    description: str
    status: str
    priority: int
    milestones: dict
