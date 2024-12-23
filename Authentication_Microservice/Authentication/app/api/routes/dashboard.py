from fastapi import APIRouter, Depends, HTTPException
from app.models import IndividualUser
from app.api.deps import get_current_individual_user

router = APIRouter()

@router.get("/dashboard")
def get_individual_dashboard(
    current_user: IndividualUser = Depends(get_current_individual_user)
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