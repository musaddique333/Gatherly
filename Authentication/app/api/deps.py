from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.security import verify_access_token
from app.core.db import get_db
from app.models import IndividualUser, CorporateUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency to get the current individual user from the token
def get_current_individual_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    email = payload.get("sub")
    user = db.query(IndividualUser).filter(IndividualUser.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Dependency to get the current corporate user from the token
def get_current_corporate_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    corporate_email = payload.get("sub")
    corporate_user = db.query(CorporateUser).filter(CorporateUser.corporate_email == corporate_email).first()
    if not corporate_user:
        raise HTTPException(status_code=404, detail="Corporate user not found")
    return corporate_user

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

    # Check if the user exists in the database (for both individuals and corporates)
    user = db.query(IndividualUser).filter(IndividualUser.email == email).first()
    if not user:
        user = db.query(CorporateUser).filter(CorporateUser.corporate_email == email).first()

    if not user:
        raise credentials_exception

    return user
