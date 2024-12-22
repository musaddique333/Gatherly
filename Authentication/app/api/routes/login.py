from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import IndividualSignUp, CorporateSignUp, IndividualUser, CorporateUser
from app.utils import *
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from datetime import timedelta

router = APIRouter()

# Signup route for individual users
@router.post("/signup")
def signup_individual(user: IndividualSignUp, db: Session = Depends(get_db)):
    # Validate phone number
    is_valid_phone_number(user.phone_number)

    # Validate password strength
    validate_password_strength(user.password)

    # Hash password
    hashed_password = hash_password(user.password)

    # Create new individual user
    db_user = IndividualUser(
        username=user.username, 
        email=user.email, 
        phone_number=user.phone_number, 
        hashed_password=hashed_password
    )

    # Add to Supabase PostgreSQL
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send verification email
    verification_link = f"http://localhost:8000/auth/verify-email?email={user.email}"
    send_verification_email(user.username, user.email, verification_link)

    # Send SMS verification code (Implement the logic)
    # send_sms(user.phone_number, "Your verification code is: 123456")
    #TODO: message": f"Individual user {user.email} signed up successfully. Verification email and SMS sent!

    return {"message": f"Individual user {user.email} signed up successfully. Verification email sent!"}

@router.post("/resend-verification-email")
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    """
    Resend the email verification link to the user.
    """
    # Check if the user exists in the database
    user = db.query(IndividualUser).filter(IndividualUser.email == email).first()

    if not user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist."
        )

    # Check if the user is already verified (Optional if you track this in DB)
    if user.is_verified:  # Assuming `is_verified` is a boolean column in the user model
        raise HTTPException(
            status_code=400, detail="This email is already verified."
        )

    # Generate a new verification link
    verification_link = f"http://localhost:8000/auth/verify-email?email={user.email}"

    # Resend the verification email
    send_verification_email(user.username, user.email, verification_link)

    return {"message": f"Verification email resent to {email}. Please check your inbox."}

# Signup route for corporate users
@router.post("/signup-corporate")
def signup_corporate(user: CorporateSignUp, db: Session = Depends(get_db)):
    # Validate corporate email
    is_corporate_email(user.corporate_email)
    
    # Hash password
    hashed_password = hash_password(user.password)

    # Create new corporate user
    db_user = CorporateUser(
        corporate_email=user.corporate_email,
        contact_person=user.contact_person,
        company_name=user.company_name,
        hashed_password=hashed_password
    )
    
    # Add to Supabase PostgreSQL
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": f"Corporate user {user.company_name} signed up successfully"}

# Email verification route for individual users
@router.get("/verify-email")
def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(IndividualUser).filter(IndividualUser.email == email).first()
    
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
def login_individual(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(IndividualUser).filter(IndividualUser.email == email).first()

    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify your email to proceed.")
    
    if not user.is_phone_verified:
        raise HTTPException(status_code=403, detail="Phone no not verified. Please verify your phone number to proceed.")
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Login route for corporate users
@router.post("/login-corporate")
def login_corporate(corporate_email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(CorporateUser).filter(CorporateUser.corporate_email == corporate_email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.corporate_email}, expires_delta=access_token_expires)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
