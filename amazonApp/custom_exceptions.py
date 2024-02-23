class DuplicateUserException(Exception):
    def __init__(self, message="A user with that username and email already exists"):
        self.message = message
        super().__init__(self.message)


class DuplicateUsernameException(Exception):
    def __init__(self, message="A user with that username already exists"):
        self.message = message
        super().__init__(self.message)


class DuplicateEmailException(Exception):
    def __init__(self, message="A user with that email already exists"):
        self.message = message
        super().__init__(self.message)