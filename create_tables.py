from database import db
from models import Class, Employer, Shift


def create_tables():
    with db:
        db.create_tables([Class, Employer, Shift])
        print("Tables created successfully!")


if __name__ == "__main__":
    create_tables()

