from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def _init_():
    print("Hello")

def get_password_hash(password):
    return pwd_context.hash(password)

s = get_password_hash('test')
print(s)