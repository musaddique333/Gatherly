from sqlalchemy.orm import Session
from app.models import IndividualUser, IndividualSignUp

# create new user in the db
def create_user(user: IndividualSignUp, hashed_password: str, db: Session):
    db_user = IndividualUser(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get user by email from db
def get_user_by_email(email: str, db: Session):
    return db.query(IndividualUser).filter(IndividualUser.email == email).first()