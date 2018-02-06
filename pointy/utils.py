import re

id_re = re.compile('^.[a-zA-Z0-9]*$')


def validate_id(id_: str):
    return bool(id_re.match(id_))
