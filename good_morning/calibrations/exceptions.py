class InvalidTrainingModeError(Exception):
    
    def __init__(self, mode, message = "Invalid mode given for training"):
        self.message = message
        self.mode = mode
        super().__init__(message)
        
        
    def __str__(self):
        return f"{self.mode} -> {self.message}"

class InvalidModelError(Exception):
    
    def __init__(self, message = "Model needs to be a nn.Module"):
        super().__init__(message)
   
class NotFullyLabeledError(Exception):

    def __init__(self, message = "Dataset is not fully labeled!"):
        super().__init__(message)

class LoadModelError(Exception):
    pass