from helpers.__exceptions import InvalidCommandArgsException

def assert_is_digit(string_to_test: str):
    try:
        int(string_to_test)
    except ValueError:
        raise InvalidCommandArgsException
