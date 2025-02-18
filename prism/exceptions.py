
"""
Prism Exceptions
"""


class PrismException(Exception):
    """
    Parent class for all prismexceptions
    """
    pass


class InvalidProjectException(PrismException):
    """
    Exception raised if project is not valid
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class RuntimeException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidProfileException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ProjectPyNotFoundException(PrismException):
    """
    Exception raised if the prism_project.py isn't found
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ModulesDirNotFoundException(PrismException):
    """
    Exception raised if modules dir isn't not found
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class YamlNotFoundException(PrismException):
    """
    Exception raised if the profile YML not found
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidProjectPyException(PrismException):
    """
    Exception raised if parsing prism_project.py raises an error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidImportException(PrismException):
    """
    Exception raised if imports in prism_project.py are not specified correctly
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidJinjaException(PrismException):
    """
    Exception raised when parsing jinja syntax in .yml files
    """
    def __init__(self, message, line_number):
        self.message = message
        self.line_number = line_number
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CompileException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DAGException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ConsoleEventException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ParserException(PrismException):
    """
    Exception raised during command runtime.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidTriggerException(PrismException):
    """
    Exception raised for invalid triggers.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class TaskAlreadyExistsException(PrismException):
    """
    Exception raised if task already exists.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidAgentsYmlException(PrismException):
    """
    Exception raise if agent configuration is invalid
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidAgentsConfException(PrismException):
    """
    Exception raise if agent configuration is invalid
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NotImplementedException(PrismException):
    """
    Exception raise if agent configuration is invalid
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class AgentAlreadyExistsException(PrismException):
    """
    Exception raise if agent YAML file already exists
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FileNotFoundException(PrismException):
    """
    Exception raise if agent YAML file already exists
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EnvironmentVariableNotFoundException(PrismException):
    """
    Exception raise if agent YAML file already exists
    """

    def __init__(self, environment_var):
        self.message = f"environment variable `{environment_var}` not found"
        super().__init__(self.message)

    def __str__(self):
        return self.message
