import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Swagger'daki "Authorize" butonu bu URL'i kullanir
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Her istekte calisan dependency.
    
    1. Authorization header'dan token'i alir (otomatik)
    2. Token'i decode eder
    3. user_id ve role bilgisini dondurur
    4. Token gecersizse 401 hatasi firlatir
    
    Kullanim:
        @router.post("/")
        def my_route(user = Depends(get_current_user)):
            print(user["user_id"])  # 2
            print(user["role"])     # "guest"
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise credentials_exception
