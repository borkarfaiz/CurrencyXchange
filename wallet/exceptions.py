class InsufficientBalance(Exception):
    def __init__(self, message):
        super(InsufficientBalance, self).__init__(message)
