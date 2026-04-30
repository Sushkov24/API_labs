from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from db.session import get_db
from repository.user_repo import UserRepository
from schemas.user import UserCreate, Token
from core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(user_in: UserCreate, db=Depends(get_db)):
    repo = UserRepository(db)
    if await repo.get_user_by_email(user_in.email):
        raise HTTPException(status_code=400, detail="User already exists")
    await repo.create_user(user_in)
    return {"message": "User created"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "access_token": create_access_token({"email": user["email"]}),
        "refresh_token": create_refresh_token({"email": user["email"]}),
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str = Body(..., embed=True), db=Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Перевіряємо, що це саме refresh токен
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate refresh token")

    return {
        "access_token": create_access_token({"email": email}),
        "refresh_token": create_refresh_token({"email": email}),
        "token_type": "bearer"
    }