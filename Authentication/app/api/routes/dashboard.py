from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import IndividualUser, CorporateUser
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/individual/dashboard")
def get_individual_dashboard(
    db: Session = Depends(get_db), current_user: IndividualUser = Depends(get_current_user)
):
    # Check if the user is an individual user
    if not isinstance(current_user, IndividualUser):
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Return individual user data
    return {
        "username": current_user.username,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_email_verified": current_user.is_email_verified,
        "is_phone_verified": current_user.is_phone_verified,
    }

@router.get("/corporate/dashboard")
def get_corporate_dashboard(
    db: Session = Depends(get_db), current_user: CorporateUser = Depends(get_current_user)
):
    # Check if the user is a corporate user
    if not isinstance(current_user, CorporateUser):
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Return corporate user data
    return {
        "company_name": current_user.company_name,
        "contact_person": current_user.contact_person,
        "corporate_email": current_user.corporate_email,
        "is_email_verified": current_user.is_email_verified,
        "is_phone_verified": current_user.is_phone_verified,
    }

