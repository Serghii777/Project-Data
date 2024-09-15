import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Column, Boolean, Enum, UUID, BigInteger
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column


class Base(DeclarativeBase):
    pass



class UserCourses(Base):
    __tablename__ = 'user_courses'
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), index=True)


class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    password = Column(String(length=1024), nullable=False)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    avatar = Column(String(100))
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False)
    phone = Column(BigInteger, nullable=False)

    courses = relationship("Course", secondary='user_courses', back_populates="users")

    @hybrid_property
    def fullname(self):
        return self.first_name + " " + self.last_name


class BlackList(Base):
    __tablename__ = 'black_list'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    users = relationship("User", secondary='user_courses', back_populates="courses")
