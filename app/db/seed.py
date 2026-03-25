from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.models import Course, CourseTextbook, Enrollment, Listing, RoleEnum, Textbook, University, User
from app.models.models import ConditionEnum
from app.services.pricing import recommend_price


def seed_if_empty(db: Session) -> None:
    if db.query(University).count() > 0:
        return

    usj = University(name="University of Saint Joseph", domain="usj.edu")
    db.add(usj)
    db.flush()

    users = [
        User(email="noah@usj.edu", hashed_password=hash_password("Password123!"), first_name="Noah", last_name="Grauer", role=RoleEnum.student, university_id=usj.id, is_verified=True),
        User(email="jane@usj.edu", hashed_password=hash_password("Password123!"), first_name="Jane", last_name="Miller", role=RoleEnum.student, university_id=usj.id, is_verified=True),
        User(email="liam@usj.edu", hashed_password=hash_password("Password123!"), first_name="Liam", last_name="Harris", role=RoleEnum.student, university_id=usj.id, is_verified=True),
        User(email="alumni1@usj.edu", hashed_password=hash_password("Password123!"), first_name="Ava", last_name="Clark", role=RoleEnum.alumni, university_id=usj.id, is_verified=True),
    ]
    db.add_all(users)
    db.flush()

    courses = [
        Course(course_code="CS301", course_name="Software Engineering", professor="Dr. Patel", semester="Spring 2026", university_id=usj.id),
        Course(course_code="MATH220", course_name="Discrete Mathematics", professor="Dr. Lin", semester="Spring 2026", university_id=usj.id),
        Course(course_code="BUS210", course_name="Principles of Marketing", professor="Dr. Torres", semester="Spring 2026", university_id=usj.id),
    ]
    db.add_all(courses)
    db.flush()

    textbooks = [
        Textbook(isbn="9780135957059", title="Clean Code", author="Robert C. Martin", edition="1st", publisher="Prentice Hall", retail_price=49.99),
        Textbook(isbn="9780134685991", title="Effective Java", author="Joshua Bloch", edition="3rd", publisher="Addison-Wesley", retail_price=54.99),
        Textbook(isbn="9780073383095", title="Discrete Mathematics and Its Applications", author="Kenneth Rosen", edition="8th", publisher="McGraw-Hill", retail_price=89.99),
        Textbook(isbn="9780134492513", title="Marketing Management", author="Philip Kotler", edition="15th", publisher="Pearson", retail_price=119.99),
    ]
    db.add_all(textbooks)
    db.flush()

    db.add_all(
        [
            CourseTextbook(course_id=courses[0].id, textbook_id=textbooks[0].id, is_required=True),
            CourseTextbook(course_id=courses[0].id, textbook_id=textbooks[1].id, is_required=False),
            CourseTextbook(course_id=courses[1].id, textbook_id=textbooks[2].id, is_required=True),
            CourseTextbook(course_id=courses[2].id, textbook_id=textbooks[3].id, is_required=True),
        ]
    )

    db.add_all(
        [
            Enrollment(user_id=users[0].id, course_id=courses[0].id, semester="Spring 2026"),
            Enrollment(user_id=users[0].id, course_id=courses[1].id, semester="Spring 2026"),
            Enrollment(user_id=users[1].id, course_id=courses[0].id, semester="Spring 2026"),
            Enrollment(user_id=users[2].id, course_id=courses[2].id, semester="Spring 2026"),
        ]
    )

    for seller, textbook, condition, price in [
        (users[1], textbooks[0], ConditionEnum.good, 30.0),
        (users[3], textbooks[2], ConditionEnum.like_new, 58.0),
        (users[2], textbooks[3], ConditionEnum.good, 72.0),
    ]:
        rec, _ = recommend_price(float(textbook.retail_price), condition)
        db.add(
            Listing(
                seller_id=seller.id,
                textbook_id=textbook.id,
                condition=condition,
                price=price,
                ai_recommended_price=rec,
                description="Good campus pickup condition",
            )
        )

    db.commit()
