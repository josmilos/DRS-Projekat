class UserNotFoundError(Exception):
    pass


class AddUserError(Exception):
    pass


class UserNotFoundByEmail(UserNotFoundError):
    def __init__(self, email):
        super.__init__(f"User with email {email} does not exist!")


class UserUnknownError():
    def __init__(self, email):
        super.__init__(f"UnknownError: Could not find user with email {email}!")

