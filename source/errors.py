class UnknownActionError(Exception):
    def __init__(self, action, possible_actions):
        self.message = f"Unknown action '{action}', please us one of the defined actions: {possible_actions}"
        super().__init__(self.message)

class UnknownChoiceError(Exception):
    def __init__(self, chosen, possible):
        self.message = f"Unknown option {chosen} chosen, please pick one of the computed choices: {possible}"
        super().__init__(self.message)
    
class MissingModelError(Exception):
    def __init__(self, action):
        self.message = f"To compute {action} provide path to language model\n Usage: --model PATH_TO_MODEL"
        super().__init__(self.message)

class NotMatchingSizeError(Exception):
    def __init__(self, l1, l2):        
        self.message = f"Size of rows doesn't match, expected {l1}, new row has size {l2}"
        super().__init__(self.message)