def getClassVariables(_class: type) -> list[str]:
    return [attr for attr in dir(_class) if not attr.startswith("__")]