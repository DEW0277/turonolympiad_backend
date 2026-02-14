from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str
    last_name: str
    

class UserRegister(UserBase):
    phone_number: str
    password: str
    verification_method: str
    otp: int



class UserLogin(UserBase):
    password: str
    

class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class OtpRequest(BaseModel):
    phone_number: str
    otp_code: int