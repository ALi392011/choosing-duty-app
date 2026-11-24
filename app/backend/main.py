from contextlib import asynccontextmanager

from fastapi import FastAPI
from database.database import init_db
from database.database import read_students
from database.database import choose_duty
from database.database import add_student
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


class Student(BaseModel):
    id: str
    name: str


app = FastAPI(lifespan=lifespan)


@app.get("/students/")
async def read_item():
    students = await read_students()
    return students


@app.get("/students/duty/")
async def get_duty():
    duty = await choose_duty()
    return duty


@app.post("/add/")
async def add_student(student: Student):
    await add_student(student.id, student.name)
    return student
