from fastapi import APIRouter, Depends, HTTPException

from app.models import IndividualUser
from app.api.deps import get_current_individual_user

router = APIRouter()


@router.get("/dashboard", response_model=dict)
def get_individual_dashboard(
    current_user: IndividualUser = Depends(get_current_individual_user)
):
    """
    Endpoint to get the individual user's dashboard.

    Args:
        current_user (IndividualUser): The current authenticated user.

    Returns:
        dict: A dictionary containing the user's dashboard data.
    """

    # Check if the user is an individual user
    if not isinstance(current_user, IndividualUser):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Ensure the user exists and has necessary attributes
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return individual user data
    return {
        "username": current_user.username,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "is_email_verified": current_user.is_email_verified,
        "is_phone_verified": current_user.is_phone_verified,
    }