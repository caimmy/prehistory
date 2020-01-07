import pyotp
import time
from datetime import datetime

if "__main__" == __name__:
    res = pyotp.random_base32()
    print(res)
    
    