from contextlib import asynccontextmanager

from fastapi import FastAPI
import database.database as db
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield


class Student(BaseModel):
    id: str
    name: str


app = FastAPI(lifespan=lifespan)


@app.get("/students/")
async def read_item():
    students = await db.read_students()
    return students


@app.get("/students/duty/")
async def get_duty():
    duty = await db.choose_duty()
    return duty


@app.post("/add/")
async def add_student(student: Student):
    await db.add_student(student.id, student.name)
    return student
