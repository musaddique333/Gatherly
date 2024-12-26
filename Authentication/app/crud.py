from sqlalchemy.orm import Session

from app.models import IndividualUser, IndividualSignUp

# create new user in the db
def create_user(user: IndividualSignUp, hashed_password: str, db: Session):
    """
    Create a new user in the database.

    Args:
        user (IndividualSignUp): User data including username, email, and phone number.
        hashed_password (str): The hashed password for the user.
        db (Session): The database session.

    Returns:
        IndividualUser: The newly created user object after being added to the database.
    """
    db_user = IndividualUser(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()  # Rollback the transaction in case of error
        raise Exception(f"Error creating user: {str(e)}")
    
    return db_user

# get user by email from db
def get_user_by_email(email: str, db: Session):
    """
    Retrieve a user from the database by their email.

    Args:
        email (str): The email of the user to retrieve.
        db (Session): The database session.

    Returns:
        IndividualUser: The user object corresponding to the email, or None if not found.
    """
    return db.query(IndividualUser).filter(IndividualUser.email == email).first()
