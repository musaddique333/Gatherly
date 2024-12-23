from fastapi import Depends, HTTPException, APIRouter, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import IndividualSignUp, UserLogin
from app.crud import create_user, get_user_by_email
from app.utils import *
from app.core.security import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter()

# Signup route for individual users
@router.post("/signup")
def signup_individual(user: IndividualSignUp, request: Request, db: Session = Depends(get_db)):
    # Validate phone number
    is_valid_phone_number(user.phone_number)

    # Validate password strength
    validate_password_strength(user.password)

    # Hash password
    hashed_password = hash_password(user.password)

    # Create new individual user
    db_user = create_user(user, hashed_password, db)

    # Add to Supabase PostgreSQL
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate verification token
    token = generate_verification_token(user.email)
    verification_link = str(request.url_for("verify-email")) + f"?token={token}"

    # Send verification email
    send_verification_email(user.username, user.email, verification_link)

    # Send SMS verification code (Implement the logic)
    # send_sms(user.phone_number, "Your verification code is: 123456")
    #TODO: message": f"Individual user {user.email} signed up successfully. Verification email and SMS sent!

    return {"message": f"Individual user {user.email} signed up successfully. Verification email sent!"}

@router.post("/resend-verification-email")
def resend_verification_email(email: str, request: Request, db: Session = Depends(get_db)):
    # Check if the user exists in the database
    user = get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist."
        )

    # Check if the user is already verified (Optional if you track this in DB)
    if user.is_email_verified:
        raise HTTPException(
            status_code=400, detail="This email is already verified."
        )

    # Check if token exists or has expired
    try:
        # Generate a new verification link
        token = generate_verification_token(email)
        verification_link = str(request.url_for("verify-email")) + f"?token={token}"

        # Resend the verification email
        send_verification_email(user.username, user.email, verification_link)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating verification email.") from e


    return {"message": f"Verification email resent to {email}. Please check your inbox."}

# Email verification route for individual users
@router.get("/verify-email", name="verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):

    email = decode_verification_token(token)

    user = get_user_by_email(email, db)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the email verification status
    user.is_email_verified = True

    # Todo: create sepearte function for verifying phone no later on
    user.is_phone_verified = True

    db.commit()

    # For simplicity, let’s assume we just return a success message
    return {"message": f"Email {email} verified successfully!"}

# Login route for individual users
@router.post("/login")
def login_individual(user: UserLogin, db: Session = Depends(get_db)):
    # Get user by email
    user_in_db = get_user_by_email(user.email, db)

    # Check if the user exists
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Check if email is verified
    if not user_in_db.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified.")
    
    # Check if phone is verified
    if not user_in_db.is_phone_verified:
        raise HTTPException(status_code=403, detail="Phone number not verified.")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user_in_db.email}, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
