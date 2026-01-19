import string
import asyncio

class UserInterface():
    '''Asks user input for filteration such as: Average Rating, >, 5'''

    def __init__(self): #type: ignore
        self.delimiter="|"
        self.all_filter_tools:list[list[str]]=self.start()

    def start(self):
        ''''''
        flag=True
        while flag:
            user_input=self._get_input()
            if self._is_exit(user_input)==True: break
            elif self._is_display_help(user_input): self.display_help()
            else:
                filter_tools=self._parse_all_filters(user_input)
                flag=False
                #Check if it is valid filter
        return filter_tools

    def _get_input(self):
        return input('Type -help to open instructions menu.\n')
        
    def _is_exit(self, user_input:str):
        ''''''
        exit_list=['quit', 'exit', 'leave']
        if user_input.strip().lower() in exit_list:
            flag=True
        else:
            flag=False
        return flag

    def _parse_all_filters(self, user_input:str):
        ''''''
        user_input=self._split_by_delimiter(user_input)
        parsed_filters=[]
        for filter in user_input:
            parsed_filters.append(self._parse_filter(filter))
        return parsed_filters

    def _split_by_delimiter(self, user_input:str):
        self.delimiter=self._get_delimiter()
        return self._parse_delimiter(self.delimiter, user_input)

    def _get_delimiter(self):
        user_delimiter=input(f'''Optional: input your one char delimiter or press enter to keep it as: {self.delimiter}, type /help to get more information\n''')
        if user_delimiter in [""," "]:
            pass
        elif user_delimiter in string.punctuation.replace(',', ''):self.delimiter=user_delimiter
        else:
            print('Delimiter configuration failed. Set up as default. ('|')')
        return self.delimiter

    def _parse_delimiter(self, delimiter:str, user_input:str):
        '''Applies delimiter to multiple filters, if there is only one filter ignore.'''
        filtered_input=user_input.strip().lower().split(delimiter)
        filtered_input=[value.strip() for value in filtered_input]
        return filtered_input

    def _parse_filter(self, user_input:str):
        ''''''
        filtered_input=user_input.strip().lower().split(',')
        filtered_input=[value.strip() for value in filtered_input]
        if len(filtered_input)<4 and len(filtered_input)>0:
            return filtered_input
        else:
            raise ValueError
        
    def _is_display_help(self, user_input:str):
        '''Checks for is user asking for help.'''
        if user_input in ['delimiter', 'search', 'filter', 'help']:
            return self.display_help(True)

    def display_help(self, flag:bool):
        ''''''
        user_text=input('You opened instructions/help menu. Choose options and press enter to see intructions. \nOptions:\n\tsearch\n\tdelimiter\n\tfilter\n\tquit\n')

        while flag==True:
            
            if user_text in 'delimiter':
                print(f'''A delimiter is your splitting method for multiple filtering in one input. The default is assigned to '|'\n' \
                'A delimiter allows program to recognize seperate filters in one line such as:\n' \
                '"Average Rating, >, 5 | Number of Votes, >, 10000" If you do set delimiter a special case, it needs to be valid. (Any in: {string.punctuation.replace(',','')})\n
                There is no logical reason more than self preference to changing the delimiter.
                
                WARNING: comma is NOT valid delimiter as it is used for different case.''')
                user_text=input('\nOptions:\n\tsearch\n\tdelimiter\n\tfilter\n\tquit\n')

            elif user_text in 'search':
                print(f'''To search for a movie, enter values such as: Average Rating, >, 5 or if looking for titles or genres, try typing and entering: Shawshank Redemption or Horror\n''')
            
            elif user_text in 'filter':
                print('''To apply more than one filter ''')

            elif self._is_exit(user_text):
                flag=False

if __name__ == "__main__":
    ui=UserInterface()    
    '''
    NOTE:
            Filter logic update
                -Add compatible CLI commands with multiple filtering in one input,
                -Add user instruction callables,
                -Fix unconventional and confusing callable names.
    TODO:
            -Need to check filtering twice. 
                Once in ui interface for syntax good enough for splitting (which is done at applyFilterSplit)
                Once more in main.py in applyAdvice for valid values in df.'''