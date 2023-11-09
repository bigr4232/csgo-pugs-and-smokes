class NoPathException(Exception):
    def __init__(self):
        self.message = 'No path found. Please enter path after -dir'
        super().__init__(self.message)

class MissingDirArg(Exception):
    def __init__(self):
        self.message = 'Missing directory argument. Please specify install path with -dir [path]'
        super().__init__(self.message)