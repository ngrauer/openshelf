"""
OpenShelf MVP v1 — Courses Router
List courses, get required textbooks, manage enrollments.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.models.models import Course, CourseTextbook, Enrollment, User
from app.schemas.schemas import (
    CourseOut, CourseWithTextbooks, TextbookOut, EnrollmentOut, EnrollmentWithCourse,
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=List[CourseOut])
def list_courses(
    university_id: Optional[int] = Query(None),
    semester: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search by course code or name"),
    db: Session = Depends(get_db),
):
    """List courses, optionally filtered or searched."""
    query = db.query(Course)
    if university_id:
        query = query.filter(Course.university_id == university_id)
    if semester:
        query = query.filter(Course.semester == semester)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(Course.course_code.ilike(pattern), Course.course_name.ilike(pattern))
        )
        return query.order_by(Course.course_code).limit(20).all()
    return query.all()


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a single course by ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{course_id}/textbooks", response_model=CourseWithTextbooks)
def get_course_textbooks(course_id: int, db: Session = Depends(get_db)):
    """Get a course with its required textbooks."""
    course = (
        db.query(Course)
        .options(joinedload(Course.course_textbooks).joinedload(CourseTextbook.textbook))
        .filter(Course.id == course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    textbooks = [ct.textbook for ct in course.course_textbooks]
    return CourseWithTextbooks(
        id=course.id,
        course_code=course.course_code,
        course_name=course.course_name,
        professor=course.professor,
        semester=course.semester,
        university_id=course.university_id,
        textbooks=[TextbookOut.model_validate(t) for t in textbooks],
    )


@router.get("/user/{user_id}/enrollments", response_model=List[EnrollmentWithCourse])
def get_user_enrollments(user_id: int, db: Session = Depends(get_db)):
    """Get all course enrollments for a user."""
    enrollments = (
        db.query(Enrollment)
        .options(joinedload(Enrollment.course))
        .filter(Enrollment.user_id == user_id)
        .all()
    )
    result = []
    for e in enrollments:
        result.append(EnrollmentWithCourse(
            id=e.id,
            user_id=e.user_id,
            course_id=e.course_id,
            semester=e.semester,
            course=CourseOut.model_validate(e.course) if e.course else None,
        ))
    return result
