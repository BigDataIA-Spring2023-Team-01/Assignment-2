from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
plain_password = 'test_disabled'
hashed_password = pwd_context.hash('test_disabled')
print(hashed_password)
print(pwd_context.verify(plain_password, hashed_password))


