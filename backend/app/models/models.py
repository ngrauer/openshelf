"""
OpenShelf MVP v1 — SQLAlchemy ORM Models
Normalized relational schema with primary/foreign keys.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, JSON,
    ForeignKey, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# --------------- Enums ---------------

class UserRole(str, enum.Enum):
    student = "student"
    alumni = "alumni"


class BookCondition(str, enum.Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"
    poor = "poor"


class ListingStatus(str, enum.Enum):
    active = "active"
    pending = "pending"
    sold = "sold"
    removed = "removed"


class NotificationType(str, enum.Enum):
    match = "match"
    offer = "offer"
    message = "message"
    resale_reminder = "resale_reminder"


class ConversationStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


# --------------- Models ---------------

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False, unique=True)  # e.g. "usj.edu"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="university")
    courses = relationship("Course", back_populates="university")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.student)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    university = relationship("University", back_populates="users")
    enrollments = relationship("Enrollment", back_populates="user")
    listings = relationship("Listing", back_populates="seller")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    conversations_as_buyer = relationship("Conversation", back_populates="buyer", foreign_keys="Conversation.buyer_id")
    conversations_as_seller = relationship("Conversation", back_populates="seller", foreign_keys="Conversation.seller_id")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="reviewed_user", foreign_keys="Review.reviewed_user_id")
    notifications = relationship("Notification", back_populates="user")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(20), nullable=False)
    course_name = Column(String(255), nullable=False)
    professor = Column(String(255), nullable=True)
    semester = Column(String(20), nullable=False)  # e.g. "Spring 2026"
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    university = relationship("University", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    course_textbooks = relationship("CourseTextbook", back_populates="course")


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(13), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    edition = Column(String(50), nullable=True)
    publisher = Column(String(255), nullable=True)
    retail_price = Column(Float, nullable=True)  # MSRP for bookstore comparison
    image_url = Column(String(500), nullable=True)  # Cover image URL or uploaded path
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course_textbooks = relationship("CourseTextbook", back_populates="textbook")
    listings = relationship("Listing", back_populates="textbook")


class CourseTextbook(Base):
    __tablename__ = "course_textbooks"
    __table_args__ = (
        UniqueConstraint("course_id", "textbook_id", name="uq_course_textbook"),
    )

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    is_required = Column(Boolean, default=True)

    course = relationship("Course", back_populates="course_textbooks")
    textbook = relationship("Textbook", back_populates="course_textbooks")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "semester", name="uq_enrollment"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(String(20), nullable=False)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=False)
    condition = Column(SAEnum(BookCondition), nullable=False)
    price = Column(Float, nullable=False)
    ai_recommended_price = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # Seller's photo of their copy
    image_urls = Column(JSON, nullable=True, default=list)
    status = Column(SAEnum(ListingStatus), default=ListingStatus.active)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    seller = relationship("User", back_populates="listings")
    textbook = relationship("Textbook", back_populates="listings")
    matches = relationship("Match", back_populates="listing")
    conversations = relationship("Conversation", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("listing_id", "buyer_id", name="uq_match"),
    )

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0–100
    matched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    listing = relationship("Listing", back_populates="matches")
    buyer = relationship("User")


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("listing_id", "buyer_id", "seller_id", name="uq_conversation"),
    )

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SAEnum(ConversationStatus), default=ConversationStatus.pending)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    listing = relationship("Listing", back_populates="conversations")
    buyer = relationship("User", back_populates="conversations_as_buyer", foreign_keys=[buyer_id])
    seller = relationship("User", back_populates="conversations_as_seller", foreign_keys=[seller_id])
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.sent_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_agentic = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("reviewer_id", "listing_id", name="uq_review_per_listing"),
    )

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1–5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reviewer = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])
    reviewed_user = relationship("User", back_populates="reviews_received", foreign_keys=[reviewed_user_id])
    listing = relationship("Listing", back_populates="reviews")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SAEnum(NotificationType), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    reference_id = Column(Integer, nullable=True)  # generic ref to listing/message
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")
