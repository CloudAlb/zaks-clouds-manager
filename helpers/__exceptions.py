class EnvironmentEnvVarNotDefined(Exception):
    def __init__(self, message="The environment variable \"environment\" was not defined in the OS"):
        self.message = message
        super().__init__(self.message)

class CommandArgsRequiredException(Exception):
    def __init__(self, message="Command arguments are required for this operation"):
        self.message = message
        super().__init__(self.message)

class InvalidCommandArgsException(Exception):
    def __init__(self, message="The command arguments for this command are invalid!"):
        self.message = message
        super().__init__(self.message)

class MissingDotEnvField(Exception):
    def __init__(self, message="Attempted to retrieve data from \".env\" file but failed"):
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
