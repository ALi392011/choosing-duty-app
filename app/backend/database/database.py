from __future__ import annotations

import os
from dotenv import load_dotenv

from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import text


load_dotenv()
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_user = os.getenv('POSTGRES_USER')

engine = create_async_engine(
    f"postgresql+asyncpg://{postgres_user}:{postgres_password}@db:5432/students_db",
    echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = "students"

    id = mapped_column(String, primary_key=True)
    name = mapped_column(String)

    duty_choosing = relationship("DutyChoosing", back_populates="student", uselist=False)


class DutyChoosing(Base):
    __tablename__ = "duty_choosing"

    student_id = mapped_column(String, ForeignKey("students.id"), primary_key=True)
    duty_point_counter = mapped_column(Integer, index=True, default=0)

    student = relationship("Student", back_populates="duty_choosing")


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def read_students() -> dict:
    async with async_session.begin() as session:    
        result = await session.execute(select(Student))
        return result.scalars().all()


async def add_student(id, name) -> None:
    async with async_session.begin() as session:
        name = Student(id=id, name=name)
        name.duty_choosing = DutyChoosing()
        session.add(name)


async def choose_duty() -> dict:
    async with engine.begin() as conn:
        stmt_select_name = text("""
            select name from students 
            where id in 
            (select student_id from duty_choosing 
            order by duty_point_counter desc, student_id asc 
            limit 2)
        """)

        stmt_select_id = text("""
            select student_id from duty_choosing 
            order by duty_point_counter desc, student_id asc 
            limit 2
        """)

        result_names = await conn.execute(stmt_select_name)

        result_ids = await conn.execute(stmt_select_id)
        raw_values = result_ids.mappings().all()

        values = [row["student_id"] for row in raw_values]


        stmt_update_points = text("""
            update duty_choosing 
            set duty_point_counter = case
                when student_id = any(:ids) then 0
                else duty_point_counter + 1
            end
        """)

        await conn.execute(stmt_update_points, {"ids": values})


        return result_names.mappings().all()
