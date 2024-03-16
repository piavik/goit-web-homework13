from fastapi import APIRouter, Depends, HTTPException, status #, BackgroundTasks
from starlette.responses import JSONResponse
from src.models.db import get_db
from sqlalchemy.orm import Session
from src.workers.users import get_user_by_email
from starlette.background import BackgroundTasks
from pydantic import BaseModel, EmailStr
from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.config.settings import settings


router = APIRouter(prefix="", tags=["temp"])
mail_conf = ConnectionConfig(
    MAIL_USERNAME   = settings.mail_username,
    MAIL_PASSWORD   = settings.mail_password,
    MAIL_FROM       = settings.mail_from,
    MAIL_PORT       = settings.mail_port,
    MAIL_SERVER     = settings.mail_server,
    MAIL_FROM_NAME  = settings.mail_from_name,
    MAIL_STARTTLS   = settings.mail_starttls,
    MAIL_SSL_TLS    = settings.mail_ssl_tls,
    USE_CREDENTIALS = settings.mail_use_credentials,
    VALIDATE_CERTS  = settings.mail_validate_certs,
    # TEMPLATE_FOLDER = Path(__file__).parent / 'templates',
)

JWT_SECRET_KEY = settings.jwt_secret_key
JWT_ALGORITHM = settings.jwt_algorithm

class ForgetPasswordRequest(BaseModel):
    email: EmailStr

def create_reset_password_token(email: str):
    data = {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=10)}
    token = jwt.encode(data, JWT_SECRET_KEY, JWT_ALGORITHM)
    return token

@router.post("/forget-password")
async def forget_password(
    background_tasks: BackgroundTasks,
    fpr: ForgetPasswordRequest,
    db: Session = Depends(get_db)
):
    try:
        user = await get_user_by_email(email=fpr.email, db=db)
        if user is None:
           raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                  detail="Invalid Email address")

        secret_token = create_reset_password_token(email=user.email)

        forget_url_link =  f"http://192.168.0.222:8000/tmp/reset-password/{secret_token}"

        email_body = { "company_name": settings.mail_from_name,
                       "link_expiry_min": 15,
                       "reset_link": forget_url_link }

        message = MessageSchema(
            subject="Password Reset Instructions",
            recipients=[fpr.email],
            template_body=email_body,
            subtype=MessageType.html
          )
       
        template_name = "workers/templates/reset_password_email_template.html"

        fm = FastMail(mail_conf)
        # background_tasks.add_task(fm.send_message, message, template_name)
        await fm.send_message(message, template_name=template_name)
        return JSONResponse(status_code=status.HTTP_200_OK,
           content={"message": "Email has been sent", "success": True,
               "status_code": status.HTTP_200_OK})

    except Exception as e:
    #     raise CustomHttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #           detail="Something Unexpected, Server Error", error_level=ErrorLevel.ERROR_LEVEL_2)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail=f"Some thing unexpected happened! - {e}")

from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class ResetForegetPassword(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str

class SuccessMessage(BaseModel):
    success: bool
    status_code: int
    message: str

def decode_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY,
                   algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None 

@router.post("/reset-password", response_model=SuccessMessage)
async def reset_password(
    rfp: ResetForegetPassword,
    db: Session = Depends(get_db)
):
    try:
        info = decode_reset_password_token(token=rfp.secret_token)
        if info is None:
            raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail="Invalid Password Reset Payload or Reset Link Expired")
        if rfp.new_password != rfp.confirm_password:
            raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   detail="New password and confirm password are not same.")

        hashed_password = pwd_context.hash(rfp.new_password) 
        user = get_user_by_email(email=info, db=db)
        user.password = hashed_password
        db.add(user)
        db.commit()
        return {'success': True, 'status_code': status.HTTP_200_OK,
                 'message': 'Password Rest Successfull!'}
    except Exception as e:
        raise HttpException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
              detail="Some thing unexpected happened!")