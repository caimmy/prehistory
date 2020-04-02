import pyotp
import time
import re
from datetime import datetime
from tempfile import mkstemp


if "__main__" == __name__:
    m = mkstemp("gensim_temp")
    print(m)