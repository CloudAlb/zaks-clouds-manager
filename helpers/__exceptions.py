class CommandArgsRequiredException(Exception):
    def __init__(self, message="Command arguments are required for this operation"):
        self.message = message
        super().__init__(self.message)

class InvalidApiIdException(Exception):
    def __init__(self, message="Invalid API ID exception"):
        self.message = message
        super().__init__(self.message)

class EventPatternMatchNotFoundException(Exception):
    def __init__(self, message="Event.pattern_match not found exception"):
        self.message = message
        super().__init__(self.message)

class EventChatNotFoundException(Exception):
    def __init__(self, message="Event.chat not found exception"):
        self.message = message
        super().__init__(self.message)

class MessageNotFoundException(Exception):
    def __init__(self, message="Event.message not found exception"):
        self.message = message
        super().__init__(self.message)

class EventChatMessageNotFoundException(Exception):
    def __init__(self, message="Event.message.text not found exception"):
        self.message = message
        super().__init__(self.message)
