import secrets
from cryptography.fernet import Fernet

def main():
    app_secret = secrets.token_hex(32)
    jwt_secret = secrets.token_hex(32)
    fernet_key = Fernet.generate_key().decode()

    print(f"APP_SECRET_KEY={app_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"TOKEN_ENCRYPTION_KEY={fernet_key}")

if __name__ == "__main__":
    main()
