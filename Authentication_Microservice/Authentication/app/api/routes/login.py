from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.core.db import get_db
from app.models import IndividualSignUp, UserLogin
from app.crud import create_user, get_user_by_email
from app.utils import *
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

# Configure logger
logger = logging.getLogger(__name__)

# Signup route for individual users
@router.post("/signup")
def signup_individual(
    user: IndividualSignUp, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Handles the signup process for individual users. It validates the phone number, checks password strength, 
    hashes the password, creates a new user in the database, and sends a verification email to the user.

    Args:
        user (IndividualSignUp): The user data including username, email, phone number, and password.
        request (Request): The request object, used for generating the verification link.
        db (Session): The database session dependency.

    Returns:
        dict: A message indicating the success of the user signup and verification email sending.

    Raises:
        HTTPException: If an error occurs during any of the validation, user creation, or email sending processes.
    """
    try:
        # Validate phone number format
        is_valid_phone_number(user.phone_number)

        # Validate password strength
        validate_password_strength(user.password)

        # Hash the password before storing it in the database
        hashed_password = hash_password(user.password)

        # Create new user in the database
        db_user = create_user(user, hashed_password, db)

        # Generate a verification token for email verification
        token = generate_verification_token(user.email)
        verification_link = str(request.url_for("verify-email")) + f"?token={token}"

        # Send verification email to the user
        send_verification_email(user.username, user.email, verification_link)

        # Send SMS verification code (Implement the logic)
        # send_sms(user.phone_number, "Your verification code is: 123456")
        #TODO: message": f"Individual user {user.email} signed up successfully. Verification email and SMS sent!

        return {"message": f"Individual user {user.email} signed up successfully. Verification email sent!"}

    except Exception as e:
        # Log the exception and raise an internal server error
        logger.error(f"Error during user signup for {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while signing up the user.")

@router.post("/resend-verification-email")
def resend_verification_email(
    email: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
    Resends the verification email to the user if they have not yet verified their email address.

    Args:
        email (str): The email address of the user who requested to resend the verification email.
        request (Request): The request object, used for generating the verification link.
        db (Session): The database session dependency.

    Returns:
        dict: A success message indicating that the verification email has been resent.

    Raises:
        HTTPException: If the user does not exist, the email is already verified, or an error occurs while 
                        generating and sending the verification email.
    """
    try:
        # Check if the user exists in the database
        user = get_user_by_email(email, db)

        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User with this email does not exist."
            )

        # If the user is already verified, there's no need to resend the email
        if user.is_email_verified:
            raise HTTPException(
                status_code=400, 
                detail="This email is already verified."
            )

        # Generate a new verification token and email link
        token = generate_verification_token(email)
        verification_link = str(request.url_for("verify-email")) + f"?token={token}"

        # Resend the verification email
        send_verification_email(user.username, user.email, verification_link)

        return {"message": f"Verification email resent to {email}. Please check your inbox."}

    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"Error resending verification email for {email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating verification email.") from e
   # Todo: create sepearte function for verifying phone no later on

# Email verification route for individual users
@router.get("/verify-email", name="verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verifies the user's email using a token.

    Args:
        token (str): The email verification token.
        db (Session): The database session.

    Returns:
        dict: A message confirming the email verification.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    try:
        # Decode the email from the token
        email = decode_verification_token(token)

        # Get user from the database
        user = get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Mark the email as verified
        user.is_email_verified = True

        # Mark the phone number as verified (for now, this is a placeholder)
        user.is_phone_verified = True

        # Commit the changes to the database
        db.commit()

        return {"message": f"Email {email} verified successfully!"}

    except Exception as e:
        # Log the exception or raise it for debugging purposes
        raise HTTPException(status_code=500, detail="Error verifying email.") from e

# Route to validate user by email
@router.get("/validate-user/{email}")
def validate_user(email: str, db: Session = Depends(get_db)):
    """
    Validates the user by checking if their email and phone number are verified.

    Args:
        email (str): The email of the user to validate.
        db (Session): The database session.

    Returns:
        dict: A message indicating if the user is valid and verified.

    Raises:
        HTTPException: If the user does not exist or if the email or phone number is not verified.
    """
    # Retrieve user by email
    user = get_user_by_email(email, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email to proceed.")
    
    # Check if phone number is verified
    if not user.is_phone_verified:
        raise HTTPException(status_code=403, detail="Phone number not verified. Please verify your phone number to proceed.")
    
    return {"message": f"User {email} is valid and verified."}

# Login route for individual users
@router.post("/login")
def login_individual(user: UserLogin, db: Session = Depends(get_db)):
    """
    Logs in an individual user by validating their credentials and issuing a JWT token.

    Args:
        user (UserLogin): User login details (email and password).
        db (Session): The database session.

    Returns:
        dict: An access token and token type if the credentials are valid.

    Raises:
        HTTPException: If the credentials are invalid, or if the email or phone number is not verified.
    """
    # Retrieve user by email
    user_in_db = get_user_by_email(user.email, db)

    # Validate user credentials
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Check if the email is verified
    if not user_in_db.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified.")
    
    # Check if the phone number is verified
    if not user_in_db.is_phone_verified:
        raise HTTPException(status_code=403, detail="Phone number not verified.")
    
    # Generate access token with a 30-minute expiry
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user_in_db.email}, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
