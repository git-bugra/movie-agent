import string

class UserInterface():
    '''Asks user input for filteration such as: Average Rating, >, 5'''

    def __init__(self): #type: ignore
        self.delimiter="|"
        #self.all_filter_tools:list[list[str]]=self.start()
        self._parse_all_filters("Average Rating, >, 5 | Memento")

    def start(self):
        ''''''
        while True:
            user_input=self._get_input()
            if self._apply_flag_control(user_input): break
            else:
                filter_tools=self._parse_all_filters(self, user_input)
                #Check if it is valid filter
        return filter_tools

    def _get_input(self):
        return input('Enter values to search for a movie. Like: Average Rating, >, 5 or if looking for titles or genres, try: Shawshank Redemption or Horror\n')
        
    def _apply_flag_control(self, user_input:str):
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
        elif user_delimiter.strip().lower() in ['help', '-help', '--help', '/help']:self._display_help(help_delimiter=True)
        elif user_delimiter in string.punctuation.replace(',', ''):self.delimiter=user_delimiter
        else:
            print('Delimiter configuration failed. Set up as default. ('|')')
        return self.delimiter

    def _parse_delimiter(self, delimiter:str, user_input:str):
        '''Applies delimiter to multiple filters, if there is only one filter ignore.'''
        filtered_input=user_input.strip().lower().split(delimiter)
        filtered_input=[value.strip() for value in filtered_input]
        print(filtered_input, "DELIMITER SPLIT")
        return filtered_input

    def _parse_filter(self, user_input:str):
        ''''''
        filtered_input=user_input.strip().lower().split(',')
        filtered_input=[value.strip() for value in filtered_input]
        if len(filtered_input)<4 and len(filtered_input)>0:
            return filtered_input
        else:
            raise ValueError
        
    def _display_help(self, help_delimiter:bool=False, help_input:bool=False ):
        ''''''
        if help_delimiter==True:
            print(f'''A delimiter is your splitting method for multiple filtering in one input. The default is assigned to '|'\n' \
            'A delimiter allows program to recognize seperate filters in one line such as:\n' \
            '"Average Rating, >, 5 | Number of Votes, >, 10000" If you do set delimiter a special case, it needs to be valid. (Any in: {string.punctuation.replace(',','')})\n
            There is no logical reason more than self preference to changing the delimiter.
            
            WARNING: comma is NOT valid delimiter as it is used for different case.''')
        elif help_input==True:
            print(f'''WIP''')

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