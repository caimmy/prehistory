import pyotp
import time
import re
from datetime import datetime

if "__main__" == __name__:
    res = pyotp.random_base32()
    print(res)
    
    # r = re.compile("^(\w+)-(\w+)->(\w+)")
    #
    # s = r.findall("刘邦-朝代->秦朝")
    # print(s)

    r = re.compile("^\((\w+)\)-\[:(\w+)\s\{\}\]->\((\w+)\)$")
    s = r.findall("(刘邦)-[:朝代 {}]->(秦朝)")
    print(s)