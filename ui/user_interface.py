import string

class UserInterface():
    '''Asks user input for filteration such as: Average Rating, >, 5'''

    def __init__(self): #type: ignore
        self.user_input=None
        self.filter_tools:list[list[str]]=self.getInput()

    def getInput(self, flag:bool=True):
        exit_list=['quit', 'exit', 'leave']
        while flag:
            self.user_input=input('Enter values to search for a movie. Like: Average Rating, >, 5 or if looking for titles or genres, try: Shawshank Redemption or Horror\n')
            if self.user_input.strip().lower() in exit_list:
                flag=False
            else:
                try:
                    self.applyInput()
                except ValueError:
                    print("Failed to acknowledge input. Try again or exit the program.")
                    break
            return self.filter_tools
        
    def applyInput(self):
        delimiter=self.assignDelimiter()
        user_filter=self.assignSplit(self.user_input)
        self.filter_tools.append(user_filter)
        
    def assignDelimiter(self):
        delimiter="|"
        user_delimiter=input(f'''Optional: input your one char delimiter or press enter to keep it as: {delimiter}''')
        if user_delimiter in [""," "]:
            pass
        elif user_delimiter in string.punctuation.replace(',', ''):
            delimiter=user_delimiter
        else:
            print('Delimiter configuration failed. Set up as default. ('|')')
        return delimiter
        
    def assignSplit(s, user_input:str):
        '''Mutates self.filtertools'''
        user_filter=user_input.strip().lower().split(',')
        user_filter=[value.strip() for value in user_filter]
        if len(user_filter)<4 and len(user_filter)>0:
            return user_filter
        else:
            raise ValueError
        
    def displayHelp(self, help_delimiter:bool, help_input:bool, ):
        ''''''
        if help_delimiter==True:
            print(f'''A delimiter is your splitting method for multiple filtering in one input. The default is assigned to '|'\n' \
            'A delimiter allows program to recognize seperate filters in one line such as:\n' \
            '"Average Rating, >, 5 | Number of Votes, >, 10000" If you do set delimiter a special case, it needs to be valid. (Any in: {string.punctuation.replace(',','')})\n
            There is no logical reason more than self preference to changing the delimiter.
            
            WARNING: comma is NOT valid delimiter as it is used for different case.''')
        elif help_input==True:
            print(f'''WIP''')
    '''
    NOTE:
            Filter logic update
                -Add compatible CLI commands with multiple filtering in one input,
                -Add user instruction callables,
                -
    TODO:
            assignSplit should look for delimiter and turn each into a user_filter to be passed. 
            (More likely, have an abstract layer that calls and orchestrates assignSplit)'''