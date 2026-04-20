"""
OpenShelf MVP v2 — Database Seed Script
Populates SQLite with realistic mock data for demo.

Run: cd backend && python seed.py
"""
from app.database import engine, SessionLocal, Base
from app.models.models import (
    University, User, Course, Textbook, CourseTextbook,
    Enrollment, Listing, Match, Conversation, Message, Review, Notification,
    UserRole, BookCondition, ListingStatus, NotificationType, ConversationStatus,
)
from app.services.auth_service import hash_password
from datetime import datetime, timezone, timedelta
import random

# All mock users share this password for demo convenience
DEMO_PASSWORD = "openshelf123"


def _cover(isbn):
    """Open Library cover URL from ISBN."""
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"


def seed():
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # =============================================================
        #  UNIVERSITIES
        # =============================================================
        usj = University(name="University of Saint Joseph", domain="usj.edu")
        db.add(usj)
        db.flush()

        print(f"  University created: {usj.name} (id={usj.id})")

        # =============================================================
        #  USERS (18 students + 4 alumni = 22 users)
        # =============================================================
        users_data = [
            # Students currently enrolled
            ("noah.grauer@usj.edu", "Noah", "Grauer", UserRole.student),
            ("emily.chen@usj.edu", "Emily", "Chen", UserRole.student),
            ("marcus.johnson@usj.edu", "Marcus", "Johnson", UserRole.student),
            ("sofia.rodriguez@usj.edu", "Sofia", "Rodriguez", UserRole.student),
            ("james.patel@usj.edu", "James", "Patel", UserRole.student),
            ("olivia.thompson@usj.edu", "Olivia", "Thompson", UserRole.student),
            ("daniel.kim@usj.edu", "Daniel", "Kim", UserRole.student),
            ("aisha.williams@usj.edu", "Aisha", "Williams", UserRole.student),
            ("liam.murphy@usj.edu", "Liam", "Murphy", UserRole.student),
            ("grace.taylor@usj.edu", "Grace", "Taylor", UserRole.student),
            ("ethan.wright@usj.edu", "Ethan", "Wright", UserRole.student),
            ("chloe.davis@usj.edu", "Chloe", "Davis", UserRole.student),
            ("ryan.foster@usj.edu", "Ryan", "Foster", UserRole.student),
            ("mia.gonzalez@usj.edu", "Mia", "Gonzalez", UserRole.student),
            ("tyler.brooks@usj.edu", "Tyler", "Brooks", UserRole.student),
            ("hannah.lee@usj.edu", "Hannah", "Lee", UserRole.student),
            ("jackson.clark@usj.edu", "Jackson", "Clark", UserRole.student),
            ("natalie.white@usj.edu", "Natalie", "White", UserRole.student),
            # Alumni sellers
            ("alex.martinez@usj.edu", "Alex", "Martinez", UserRole.alumni),
            ("rachel.nguyen@usj.edu", "Rachel", "Nguyen", UserRole.alumni),
            ("chris.baker@usj.edu", "Chris", "Baker", UserRole.alumni),
            ("jessica.hall@usj.edu", "Jessica", "Hall", UserRole.alumni),
        ]

        users = []
        hashed = hash_password(DEMO_PASSWORD)
        for email, first, last, role in users_data:
            u = User(
                email=email,
                hashed_password=hashed,
                first_name=first,
                last_name=last,
                role=role,
                university_id=usj.id,
                is_verified=True,
            )
            db.add(u)
            users.append(u)
        db.flush()

        print(f"  {len(users)} users created (password for all: '{DEMO_PASSWORD}')")

        # Quick references
        (noah, emily, marcus, sofia, james, olivia, daniel, aisha,
         liam, grace, ethan, chloe, ryan, mia, tyler, hannah, jackson, natalie,
         alex, rachel, chris, jessica) = users

        # =============================================================
        #  COURSES (16 courses across departments)
        # =============================================================
        courses_data = [
            ("CS 301", "Data Structures & Algorithms", "Dr. Robert Smith", "Spring 2026"),
            ("CS 420", "Artificial Intelligence", "Dr. Sarah Davis", "Spring 2026"),
            ("BIO 201", "Cellular Biology", "Dr. Jennifer Lee", "Spring 2026"),
            ("CHEM 201", "Organic Chemistry I", "Dr. Maria Garcia", "Spring 2026"),
            ("ECON 101", "Principles of Economics", "Dr. James Wilson", "Spring 2026"),
            ("MATH 220", "Discrete Mathematics", "Dr. Michael Dana", "Spring 2026"),
            ("ENG 102", "College Writing II", "Dr. Patricia Brown", "Spring 2026"),
            ("PSY 101", "Intro to Psychology", "Dr. Elizabeth Taylor", "Spring 2026"),
            ("HIST 101", "Western Civilization I", "Dr. Thomas Anderson", "Spring 2026"),
            ("PHYS 201", "General Physics I", "Dr. Richard Feynman", "Spring 2026"),
            ("ACCT 201", "Financial Accounting", "Dr. Linda Chen", "Spring 2026"),
            ("NURS 301", "Pathophysiology", "Dr. Karen Mitchell", "Spring 2026"),
            ("CS 210", "Intro to Software Engineering", "Dr. Robert Smith", "Spring 2026"),
            ("MATH 101", "Calculus I", "Dr. Alan Turing", "Spring 2026"),
            ("SOC 101", "Intro to Sociology", "Dr. Angela Davis", "Spring 2026"),
            ("PHIL 101", "Intro to Philosophy", "Dr. Marcus Aurelius", "Spring 2026"),
        ]

        courses = []
        for code, name, prof, sem in courses_data:
            c = Course(
                course_code=code,
                course_name=name,
                professor=prof,
                semester=sem,
                university_id=usj.id,
            )
            db.add(c)
            courses.append(c)
        db.flush()

        print(f"  {len(courses)} courses created")

        (cs301, cs420, bio201, chem201, econ101, math220, eng102, psy101,
         hist101, phys201, acct201, nurs301, cs210, math101, soc101, phil101) = courses

        # =============================================================
        #  TEXTBOOKS (30 textbooks with Open Library cover URLs)
        # =============================================================
        textbooks_data = [
            # CS
            ("9780262033848", "Introduction to Algorithms", "Thomas H. Cormen", "4th", "MIT Press", 95.00),
            ("9780134444321", "Data Structures and Abstractions", "Frank M. Carrano", "5th", "Pearson", 120.00),
            ("9780134610993", "Artificial Intelligence: A Modern Approach", "Stuart Russell", "4th", "Pearson", 175.00),
            ("9781292401133", "Machine Learning", "Tom Mitchell", "1st", "McGraw-Hill", 85.00),
            ("9780132350884", "Clean Code", "Robert C. Martin", "1st", "Prentice Hall", 45.00),
            ("9780201633610", "Design Patterns", "Erich Gamma", "1st", "Addison-Wesley", 55.00),
            # Bio
            ("9780321775849", "Molecular Biology of the Cell", "Bruce Alberts", "7th", "Garland Science", 145.00),
            ("9780805395693", "Campbell Biology", "Lisa Urry", "12th", "Pearson", 160.00),
            # Chem
            ("9781260565843", "Organic Chemistry", "David Klein", "4th", "Wiley", 155.00),
            # Econ
            ("9780134472140", "Principles of Economics", "N. Gregory Mankiw", "9th", "Cengage", 130.00),
            ("9780073383095", "Microeconomics", "Robert Pindyck", "9th", "Pearson", 110.00),
            # Math
            ("9780367549893", "Discrete Mathematics and Its Applications", "Kenneth Rosen", "8th", "McGraw-Hill", 140.00),
            ("9780134689517", "Discrete Mathematics with Applications", "Susanna Epp", "5th", "Cengage", 125.00),
            ("9780131103627", "Calculus: Early Transcendentals", "James Stewart", "8th", "Cengage", 150.00),
            # English
            ("9781319056278", "They Say / I Say", "Gerald Graff", "5th", "W.W. Norton", 35.00),
            ("9780134641010", "The Bedford Handbook", "Diana Hacker", "11th", "Bedford/St. Martin's", 65.00),
            # Psychology
            ("9781319132101", "Psychology", "David Myers", "13th", "Worth Publishers", 150.00),
            ("9780134240831", "Psychology: Themes and Variations", "Wayne Weiten", "11th", "Cengage", 135.00),
            # History
            ("9780077504083", "Western Civilizations", "Joshua Cole", "19th", "W.W. Norton", 95.00),
            ("9780393614886", "The Western Heritage", "Donald Kagan", "11th", "Pearson", 120.00),
            # Physics
            ("9780321856562", "University Physics", "Hugh Young", "14th", "Pearson", 170.00),
            ("9780471320579", "Fundamentals of Physics", "David Halliday", "12th", "Wiley", 165.00),
            # Accounting
            ("9781260247909", "Financial Accounting", "Robert Libby", "11th", "McGraw-Hill", 140.00),
            ("9780134725987", "Intermediate Accounting", "Donald Kieso", "17th", "Wiley", 180.00),
            # Nursing
            ("9780323354813", "Pathophysiology", "Kathryn McCance", "8th", "Elsevier", 125.00),
            # Sociology
            ("9780393639407", "Essentials of Sociology", "Anthony Giddens", "7th", "W.W. Norton", 85.00),
            # Philosophy
            ("9780199812998", "The Problems of Philosophy", "Bertrand Russell", "1st", "Oxford", 15.00),
            ("9780872201200", "Republic", "Plato", "Reeves", "Hackett", 12.00),
            # Extra popular CS books
            ("9780596007126", "Head First Design Patterns", "Eric Freeman", "2nd", "O'Reilly", 50.00),
            ("9780137081073", "The Clean Coder", "Robert C. Martin", "1st", "Prentice Hall", 40.00),
        ]

        textbooks = []
        for isbn, title, author, edition, publisher, retail in textbooks_data:
            t = Textbook(
                isbn=isbn,
                title=title,
                author=author,
                edition=edition,
                publisher=publisher,
                retail_price=retail,
                image_url=_cover(isbn),
            )
            db.add(t)
            textbooks.append(t)
        db.flush()

        print(f"  {len(textbooks)} textbooks created (with Open Library covers)")

        # Name references
        (intro_algo, ds_abstractions, ai_modern, ml_mitchell, clean_code, design_patterns,
         mol_bio, campbell_bio, org_chem, prin_econ, micro_econ,
         discrete_rosen, discrete_epp, calculus_stewart,
         they_say, bedford, psych_myers, psych_weiten,
         western_civ, western_heritage, univ_physics, fund_physics,
         fin_accounting, inter_accounting, pathophysiology,
         essentials_soc, problems_phil, republic,
         head_first_dp, clean_coder) = textbooks

        # =============================================================
        #  COURSE -> TEXTBOOK MAPPINGS
        # =============================================================
        course_textbook_map = [
            (cs301, intro_algo, True),
            (cs301, ds_abstractions, False),
            (cs420, ai_modern, True),
            (cs420, ml_mitchell, False),
            (cs210, clean_code, True),
            (cs210, design_patterns, False),
            (cs210, head_first_dp, False),
            (bio201, mol_bio, True),
            (bio201, campbell_bio, False),
            (chem201, org_chem, True),
            (econ101, prin_econ, True),
            (econ101, micro_econ, False),
            (math220, discrete_rosen, True),
            (math220, discrete_epp, False),
            (math101, calculus_stewart, True),
            (eng102, they_say, True),
            (eng102, bedford, True),
            (psy101, psych_myers, True),
            (psy101, psych_weiten, False),
            (hist101, western_civ, True),
            (hist101, western_heritage, False),
            (phys201, univ_physics, True),
            (phys201, fund_physics, False),
            (acct201, fin_accounting, True),
            (acct201, inter_accounting, False),
            (nurs301, pathophysiology, True),
            (soc101, essentials_soc, True),
            (phil101, problems_phil, True),
            (phil101, republic, True),
        ]

        for course, textbook, required in course_textbook_map:
            ct = CourseTextbook(
                course_id=course.id,
                textbook_id=textbook.id,
                is_required=required,
            )
            db.add(ct)
        db.flush()

        print(f"  {len(course_textbook_map)} course-textbook mappings created")

        # =============================================================
        #  ENROLLMENTS
        # =============================================================
        enrollment_map = [
            # Noah — primary buyer persona
            (noah, cs301), (noah, cs420), (noah, math220), (noah, eng102),
            # Emily
            (emily, cs301), (emily, bio201), (emily, eng102),
            # Marcus
            (marcus, econ101), (marcus, psy101), (marcus, eng102),
            # Sofia
            (sofia, cs420), (sofia, math220), (sofia, chem201),
            # James
            (james, bio201), (james, chem201), (james, psy101),
            # Olivia
            (olivia, econ101), (olivia, eng102), (olivia, psy101),
            # Daniel
            (daniel, cs301), (daniel, math220), (daniel, econ101),
            # Aisha
            (aisha, bio201), (aisha, psy101), (aisha, eng102),
            # Liam
            (liam, cs210), (liam, cs301), (liam, math101),
            # Grace
            (grace, hist101), (grace, eng102), (grace, phil101),
            # Ethan
            (ethan, phys201), (ethan, math101), (ethan, cs210),
            # Chloe
            (chloe, nurs301), (chloe, bio201), (chloe, psy101),
            # Ryan
            (ryan, acct201), (ryan, econ101), (ryan, math101),
            # Mia
            (mia, soc101), (mia, psy101), (mia, phil101),
            # Tyler
            (tyler, phys201), (tyler, math220), (tyler, cs301),
            # Hannah
            (hannah, hist101), (hannah, soc101), (hannah, eng102),
            # Jackson
            (jackson, cs420), (jackson, cs210), (jackson, math220),
            # Natalie
            (natalie, nurs301), (natalie, chem201), (natalie, bio201),
        ]

        for user, course in enrollment_map:
            e = Enrollment(
                user_id=user.id,
                course_id=course.id,
                semester="Spring 2026",
            )
            db.add(e)
        db.flush()

        print(f"  {len(enrollment_map)} enrollments created")

        # =============================================================
        #  LISTINGS (40 listings from various sellers)
        # =============================================================
        from app.services.matching_engine import CONDITION_MULTIPLIERS

        listings_data = [
            # Alumni Alex
            (alex, intro_algo, BookCondition.good, 42.00, "Minor highlighting in chapters 3-5. Spine intact."),
            (alex, ai_modern, BookCondition.fair, 55.00, "Some wear on cover. All pages intact."),
            (alex, discrete_rosen, BookCondition.like_new, 75.00, "Barely used. No marks or highlights."),
            (alex, prin_econ, BookCondition.good, 50.00, "Used for one semester. Clean condition overall."),
            (alex, clean_code, BookCondition.good, 22.00, "Great programming reference. Minor wear."),
            (alex, calculus_stewart, BookCondition.fair, 45.00, "Some highlighting. Complete and functional."),
            # Alumni Rachel
            (rachel, mol_bio, BookCondition.good, 60.00, "Highlighted in first 8 chapters. Good shape."),
            (rachel, org_chem, BookCondition.fair, 45.00, "Well used but complete. Some page folding."),
            (rachel, campbell_bio, BookCondition.like_new, 85.00, "Purchased but barely opened."),
            (rachel, psych_myers, BookCondition.good, 65.00, "Light pencil notes. Easily erasable."),
            (rachel, pathophysiology, BookCondition.good, 55.00, "Used for NURS 301. Good condition."),
            # Alumni Chris
            (chris, univ_physics, BookCondition.good, 72.00, "Standard wear. Practice problems untouched."),
            (chris, fin_accounting, BookCondition.like_new, 78.00, "Like new. Switched majors early."),
            (chris, western_civ, BookCondition.fair, 30.00, "Moderate use. Some annotations in margins."),
            (chris, design_patterns, BookCondition.good, 28.00, "Classic CS book. Good condition."),
            # Alumni Jessica
            (jessica, essentials_soc, BookCondition.like_new, 45.00, "Barely read. Pristine condition."),
            (jessica, problems_phil, BookCondition.good, 8.00, "Small book, great condition."),
            (jessica, republic, BookCondition.good, 6.00, "Annotated lightly in pencil."),
            (jessica, psych_weiten, BookCondition.fair, 42.00, "Used but functional. All pages intact."),
            # Emily selling
            (emily, they_say, BookCondition.good, 15.00, "Great condition. Required for ENG 102."),
            (emily, bedford, BookCondition.fair, 20.00, "Some tab markers inside. Functional."),
            # Marcus selling
            (marcus, psych_weiten, BookCondition.good, 55.00, "Clean copy. Used one semester."),
            (marcus, micro_econ, BookCondition.new, 90.00, "Never opened. Wrong edition for my class."),
            # Sofia selling
            (sofia, ml_mitchell, BookCondition.good, 38.00, "Good condition. A few dog-eared pages."),
            (sofia, discrete_epp, BookCondition.like_new, 68.00, "Barely used. Preferred the Rosen text."),
            # Daniel selling
            (daniel, ds_abstractions, BookCondition.fair, 35.00, "Functional copy. Highlighting throughout."),
            (daniel, intro_algo, BookCondition.new, 78.00, "Brand new. Ordered two by mistake."),
            # Olivia selling
            (olivia, prin_econ, BookCondition.like_new, 72.00, "Excellent condition. No markings."),
            (olivia, they_say, BookCondition.good, 12.00, "Slightly worn cover. Clean inside."),
            # James selling
            (james, campbell_bio, BookCondition.fair, 50.00, "Moderate use. All content readable."),
            # Aisha selling
            (aisha, psych_myers, BookCondition.like_new, 80.00, "Almost new. Used digital version instead."),
            # Liam selling
            (liam, head_first_dp, BookCondition.good, 25.00, "Fun read. Good condition."),
            (liam, clean_coder, BookCondition.like_new, 22.00, "Read once. Like new."),
            # Grace selling
            (grace, western_heritage, BookCondition.good, 48.00, "Used for HIST 101. Good shape."),
            # Ethan selling
            (ethan, fund_physics, BookCondition.fair, 55.00, "Moderate wear. All problems readable."),
            (ethan, calculus_stewart, BookCondition.good, 65.00, "Clean copy with minimal marks."),
            # Ryan selling
            (ryan, inter_accounting, BookCondition.like_new, 95.00, "Barely touched. Excellent condition."),
            # Tyler selling
            (tyler, univ_physics, BookCondition.like_new, 88.00, "Near perfect condition."),
            # Hannah selling
            (hannah, essentials_soc, BookCondition.fair, 30.00, "Some highlighting. Fully functional."),
            # Natalie selling
            (natalie, pathophysiology, BookCondition.new, 90.00, "Brand new, got a digital copy instead."),
        ]

        listings = []
        for seller, textbook, condition, price, desc in listings_data:
            ai_price = round(textbook.retail_price * CONDITION_MULTIPLIERS[condition], 2)
            l = Listing(
                seller_id=seller.id,
                textbook_id=textbook.id,
                condition=condition,
                price=price,
                ai_recommended_price=ai_price,
                description=desc,
                status=ListingStatus.active,
            )
            db.add(l)
            listings.append(l)
        db.flush()

        print(f"  {len(listings)} listings created")

        # =============================================================
        #  CONVERSATIONS + MESSAGES
        # =============================================================
        now = datetime.now(timezone.utc)

        conversations_data = [
            (
                noah, alex, listings[0], ConversationStatus.active,
                [
                    (noah, "Hi Alex! I'm interested in your copy of Introduction to Algorithms for CS 301. Is it still available?", True, now - timedelta(hours=5), True),
                    (alex, "Hey Noah! Yes it's still available. The highlighting is mostly in the sorting chapters. Want to meet up on campus?", False, now - timedelta(hours=4), True),
                    (noah, "That works! I'm usually in the library after 2pm. Would Wednesday work?", False, now - timedelta(hours=3), True),
                    (alex, "Wednesday at 2:30 in the library lobby works for me. See you then!", False, now - timedelta(hours=2), False),
                ],
            ),
            (
                james, rachel, listings[6], ConversationStatus.active,
                [
                    (james, "Hi! Is your Molecular Biology textbook still available? I need it for BIO 201.", True, now - timedelta(hours=8), True),
                    (rachel, "Yes! I can meet on campus tomorrow if that works.", False, now - timedelta(hours=7), True),
                ],
            ),
            (
                noah, sofia, listings[23], ConversationStatus.pending,
                [
                    (noah, "Hey Sofia, is the Machine Learning textbook by Mitchell still available?", True, now - timedelta(hours=1), False),
                ],
            ),
            (
                liam, alex, listings[4], ConversationStatus.active,
                [
                    (liam, "Hi, I need Clean Code for CS 210. Is your copy in good shape?", True, now - timedelta(hours=6), True),
                    (alex, "Yes! Minor wear on the spine but all pages perfect. $22 firm.", False, now - timedelta(hours=5), True),
                    (liam, "Sounds good. Can we meet at the student center Thursday?", False, now - timedelta(hours=4), False),
                ],
            ),
            (
                ethan, chris, listings[11], ConversationStatus.active,
                [
                    (ethan, "Interested in the University Physics book. Could you do $65?", True, now - timedelta(hours=3), True),
                    (chris, "I'd take $68 since it's in great shape. Deal?", False, now - timedelta(hours=2), False),
                ],
            ),
            (
                grace, jessica, listings[17], ConversationStatus.completed,
                [
                    (grace, "Is the Republic still available? I need it for PHIL 101.", True, now - timedelta(days=2), True),
                    (jessica, "Yes! It's in good shape. $6 is a steal for Plato!", False, now - timedelta(days=2) + timedelta(hours=1), True),
                    (grace, "Perfect! I'll take it. Library today at 3?", False, now - timedelta(days=2) + timedelta(hours=2), True),
                    (jessica, "Done! See you there.", False, now - timedelta(days=2) + timedelta(hours=3), True),
                ],
            ),
            (
                ryan, chris, listings[12], ConversationStatus.active,
                [
                    (ryan, "Hey Chris, is the Financial Accounting textbook still available?", True, now - timedelta(hours=10), True),
                    (chris, "Yep! Like new condition. $78.", False, now - timedelta(hours=9), False),
                ],
            ),
        ]

        total_messages = 0
        for buyer, seller, listing, conv_status, thread in conversations_data:
            conv = Conversation(
                listing_id=listing.id,
                buyer_id=buyer.id,
                seller_id=seller.id,
                status=conv_status,
                created_at=thread[0][3],
            )
            db.add(conv)
            db.flush()

            for sender, content, is_agentic, sent_at, read in thread:
                m = Message(
                    conversation_id=conv.id,
                    sender_id=sender.id,
                    content=content,
                    is_agentic=is_agentic,
                    read_at=sent_at + timedelta(minutes=15) if read else None,
                    sent_at=sent_at,
                )
                db.add(m)
                total_messages += 1
        db.flush()

        print(f"  {len(conversations_data)} conversations with {total_messages} messages created")

        # =============================================================
        #  REVIEWS
        # =============================================================
        reviews_data = [
            (james, rachel, listings[6], 5, "Great seller! Book was exactly as described. Quick meetup."),
            (emily, alex, listings[3], 4, "Good condition book. Slightly more worn than expected but fair price."),
            (marcus, olivia, listings[27], 5, "Perfect transaction. Book was in excellent shape."),
            (daniel, alex, listings[0], 5, "Alex is reliable. Book arrived as described."),
            (grace, jessica, listings[17], 5, "Super easy transaction. Jessica was really friendly!"),
            (liam, alex, listings[4], 4, "Good book, minor wear as described. Quick meetup."),
            (noah, rachel, listings[9], 5, "Rachel's books are always in great condition. Highly recommend!"),
            (ethan, chris, listings[11], 4, "Physics book was in good shape. Fair price."),
            (ryan, jessica, listings[15], 5, "Perfect condition sociology book. Great price too."),
            (mia, jessica, listings[16], 5, "Philosophy book arrived exactly as described. Thank you!"),
        ]

        for reviewer, reviewed, listing, rating, comment in reviews_data:
            r = Review(
                reviewer_id=reviewer.id,
                reviewed_user_id=reviewed.id,
                listing_id=listing.id,
                rating=rating,
                comment=comment,
            )
            db.add(r)
        db.flush()

        print(f"  {len(reviews_data)} reviews created")

        # =============================================================
        #  NOTIFICATIONS
        # =============================================================
        notifications_data = [
            (noah, NotificationType.match, "3 textbooks for your courses are available on OpenShelf!", None, False),
            (noah, NotificationType.message, "New message from Alex Martinez about Introduction to Algorithms", listings[0].id, False),
            (noah, NotificationType.message, "New message from Sofia Rodriguez about Machine Learning", listings[23].id, False),
            (alex, NotificationType.offer, "Noah Grauer is interested in your listing: Introduction to Algorithms", listings[0].id, True),
            (alex, NotificationType.offer, "Liam Murphy is interested in your listing: Clean Code", listings[4].id, True),
            (rachel, NotificationType.offer, "James Patel is interested in your listing: Molecular Biology of the Cell", listings[6].id, True),
            (noah, NotificationType.resale_reminder, "Semester is ending soon! List your textbooks on OpenShelf to earn money.", None, False),
            (liam, NotificationType.match, "5 textbooks for your CS courses are available!", None, False),
            (ethan, NotificationType.match, "New physics and math textbooks available for your courses!", None, False),
            (grace, NotificationType.match, "History and philosophy books for your courses are listed!", None, False),
            (chloe, NotificationType.match, "Nursing and biology textbooks available for your courses!", None, False),
            (ryan, NotificationType.match, "Accounting and economics textbooks available for your courses!", None, False),
            (chris, NotificationType.offer, "Ryan Foster is interested in your listing: Financial Accounting", listings[12].id, False),
            (jessica, NotificationType.offer, "Grace Taylor is interested in your listing: Republic", listings[17].id, True),
        ]

        for user, ntype, content, ref_id, is_read in notifications_data:
            n = Notification(
                user_id=user.id,
                type=ntype,
                content=content,
                reference_id=ref_id,
                is_read=is_read,
            )
            db.add(n)
        db.flush()

        print(f"  {len(notifications_data)} notifications created")

        db.commit()

        # =============================================================
        #  SUMMARY
        # =============================================================
        n_students = sum(1 for u in users if u.role == UserRole.student)
        n_alumni = sum(1 for u in users if u.role == UserRole.alumni)
        print("\n" + "=" * 60)
        print("  OpenShelf MVP v2 — Database Seeded Successfully")
        print("=" * 60)
        print(f"  Database: openshelf.db (SQLite)")
        print(f"  University: {usj.name}")
        print(f"  Users: {len(users)} ({n_students} students, {n_alumni} alumni)")
        print(f"  Courses: {len(courses)}")
        print(f"  Textbooks: {len(textbooks)}")
        print(f"  Listings: {len(listings)}")
        print(f"  Conversations: {len(conversations_data)}")
        print(f"  Messages: {total_messages}")
        print(f"  Reviews: {len(reviews_data)}")
        print(f"  Notifications: {len(notifications_data)}")
        print(f"")
        print(f"  Demo login credentials:")
        print(f"  -------------------------------------------")
        print(f"  Buyer persona:  noah.grauer@usj.edu")
        print(f"  Seller persona: alex.martinez@usj.edu")
        print(f"  Password (all):  {DEMO_PASSWORD}")
        print(f"")
        print(f"  Start the server:  cd backend && python main.py")
        print(f"  Swagger UI:        http://localhost:8000/docs")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"  Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
