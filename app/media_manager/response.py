from enum import Enum

class Response(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    REMOVED = "removed"
    INCOMPLETE = "incomplete"
    UNSUPPORTED = "unsupported"
    RATE_LIMITED = "rate_limited"

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
