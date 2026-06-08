
class Invalid_Mode(Exception):
    pass

class Driver:
    def __init__(self) -> None:
        pass

    def load(self, *args):
        pass

    def shutdown(self):
        pass

    def get_functions(self)-> list[str]:
        return [""]