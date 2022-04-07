import bcrypt
from fnmatch import fnmatch


def password_hash(password):
    return (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')


class glob_list(list):
    def __contains__(self, value):
        for pattern in self:
            if fnmatch(value, pattern):
                return True
        return False
