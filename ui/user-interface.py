
class UserInterface():
    '''Asks user input for filteration such as: Average Rating, >, 5'''

    def __init__(self): #type: ignore
        self.user_input=None
        self.filter_tools:list[str]=self.getInput()

    def getInput(self, flag:bool=True):
        exit_list=['quit', 'exit', 'leave']
        while flag:
            self.user_input=input('Enter values to search for a movie. Like: Average Rating, >, 5')
            
            if self.user_input.strip().lower() in exit_list:
                flag=False
            else:
                if self.assignSplit(self.user_input):
                    return self.filter_tools
                else:
                    print("Failed to acknowledge input. Try again or exit the program.")
    
    def assignSplit(self, user_input:str):
        self.filter_tools=user_input.strip().lower().split(',')
        if len(self.filter_tools) == 3:
            return True
        else:
            return False