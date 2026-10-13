import random
import sys
import time
from enum import Enum

class Messages(Enum):
    BIRTHDAY = 0,
    MORNING = 1

msg_list: list[list[int]] = [
    [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 33, 33, 33, 32, 58, 41],
    [71, 111, 111, 100, 32, 109, 111, 114, 110, 105, 110, 103, 33]
]

ascii_numbers: list[int] = msg_list[Messages.MORNING.value]

msg: str = "".join([chr(num) for num in ascii_numbers])

len_HBS: int = len(msg)
ctr: int = 0
# print(ctr, len_HBS)
while ctr < len(msg):
    ctr += random.randint(-1, +2) if ctr > 0 else random.randint(0, +1)
    _ = sys.stdout.write("\r" + msg[0:ctr+1] + "\033[K")
    _ = sys.stdout.flush()
    time.sleep(.05)
