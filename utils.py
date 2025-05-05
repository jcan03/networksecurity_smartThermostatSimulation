# T00686800 Joel Canonico COMP 3260 Project 
from cryptography.fernet import Fernet

# generate a global key once for the simulation
GLOBAL_KEY = Fernet.generate_key()

# encrypt message function using the global key
def encrypt_message(message, key=GLOBAL_KEY):
    fernet = Fernet(key)
    encrypted = fernet.encrypt(message.encode())
    return encrypted

# decrypt message function using the global key
def decrypt_message(encrypted_message, key=GLOBAL_KEY):
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_message).decode()
    return decrypted

# allowed IPs for simulation (ACL)
ALLOWED_IPS = ['127.0.0.1']  # many more could/ should be added for real application

# check if the IP is in the allowed range
def check_ip(ip):
    if ip not in ALLOWED_IPS:
        raise PermissionError("Unauthorized access: IP not in ACL")
    return True
