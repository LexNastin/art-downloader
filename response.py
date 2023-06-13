from enum import Enum

class Response(Enum):
    SUCCESS = 1
    FAILED = 2
    REMOVED = 3
    INCOMPLETE = 4
    UNSUPPORTED = 5
    RATE_LIMITED = 6

# formats
#
# success
# links: list(str)
#
# failed
# message: str
#
# removed
#
# incomplete
# links: list(str)
#
# unsupported
#
# rate_limited
# time: int
