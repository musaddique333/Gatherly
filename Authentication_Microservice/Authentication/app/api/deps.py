from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.security import verify_access_token
from app.core.db import get_db
from app.crud import get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# General dependency to get the current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the JWT token
    payload = verify_access_token(token)
    if not payload:
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Retrieve user from the database
    user = get_user_by_email(email=email, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Dependencies for specific user types
def get_current_individual_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    return get_current_user(token=token, db=db)
