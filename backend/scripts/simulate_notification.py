"""
Simulate a "new book available" notification for the demo user (Noah).

Run from the backend directory:
    cd backend && python scripts/simulate_notification.py
"""
import sys
import os

# Add backend root to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.models import Notification, NotificationType, User, Listing, Textbook, ListingStatus


def main():
    db = SessionLocal()
    try:
        # Find Noah (demo buyer persona)
        noah = db.query(User).filter(User.email == "noah.grauer@usj.edu").first()
        if not noah:
            print("Error: Noah user not found. Run seed.py first.")
            return

        # Pick a random active listing to reference
        listing = (
            db.query(Listing)
            .join(Textbook)
            .filter(
                Listing.status == ListingStatus.active,
                Listing.seller_id != noah.id,
            )
            .first()
        )

        if listing:
            textbook = db.query(Textbook).filter(Textbook.id == listing.textbook_id).first()
            content = (
                f"A new listing for '{textbook.title}' is now available "
                f"for ${listing.price:.2f}! Check it out in the Shopping tab."
            )
            ref_id = listing.id
        else:
            content = "New textbooks matching your courses have been listed on OpenShelf!"
            ref_id = None

        notification = Notification(
            user_id=noah.id,
            type=NotificationType.match,
            content=content,
            reference_id=ref_id,
            is_read=False,
        )
        db.add(notification)
        db.commit()

        print(f"Notification sent to {noah.first_name} {noah.last_name}:")
        print(f"  Type: {notification.type.value}")
        print(f"  Content: {content}")
        if ref_id:
            print(f"  Listing ID: {ref_id}")
        print(f"  Notification ID: {notification.id}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
