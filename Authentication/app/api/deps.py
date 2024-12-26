from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.core.db import get_db
from app.crud import get_user_by_email

# OAuth2 Password Bearer for extracting the token from headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# General dependency to get the current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Dependency to get the current logged-in user from the provided JWT token.
    
    Args:
        token (str): The JWT token passed in the Authorization header.
        db (Session): The database session.

    Returns:
        User object if the token is valid and the user exists, else raises HTTPException.
    """
    try:
        # Decode the JWT token and verify the payload
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing email information",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Retrieve user from the database
        user = get_user_by_email(email=email, db=db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency for specific individual user type
def get_current_individual_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependency to get the current individual user based on the provided token.
    
    Args:
        token (str): The JWT token passed in the Authorization header.
        db (Session): The database session.

    Returns:
        IndividualUser object if the token is valid and the user exists, else raises HTTPException.
    """
    return get_current_user(token=token, db=db)
