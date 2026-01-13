import requests
import random
import json
import pandas as pd
import pathlib as pl
import operator
import pdb
from ui.user_interface import UserInterface 

'''key=input('Enter OMDB API key\n')
request=requests.get(f'http://www.omdbapi.com/?apikey={key}&i=tt0108052')
'''

class MovieAgent():
    '''Main object responsible for clearing, fixing columns and internally consume columns.\n
    Carries data internally.'''
    def __init__(self):
        self.data=None
        self.condition=None
    
    def applyRenamedColumns(self):
        '''Make columns in imdb .tsv files more readable and intuitive'''
        try:    
            self.data:pd.DataFrame=self.data.rename(columns={'tconst': 'IMDBid',
                                    'averageRating': 'Average Rating',
                                    'numVotes': 'Number of Votes',
                                    'titleType': 'Title Type',
                                    'primaryTitle': 'Primary Title',
                                    'originalTitle': 'Original Title',
                                    'isAdult': 'Is Adult',
                                    'startYear': 'Published',
                                    'endYear': 'End Year',
                                    'runtimeMinutes': 'Run Time Minutes',
                                    'genres': 'Genre'})
            return self
        except KeyError as e: raise KeyError(f"Column not found to rename: {e}") from e

    def assignCondition(self, *args:str):
        '''Internal limitation the data with given columns.
        Mutates data to given arguments.
        
        *args: Names of the columns to limit'''
        columns_to_limit=[*args]
        if len(columns_to_limit)>0:self.condition=columns_to_limit
        try:self.applyCondition()
        except KeyError as e:raise KeyError(f"With given arguments, column not found: {e}") from e
        return self

    def applyCondition(self):
        '''Based on condition, adjust the data to display'''
        if self.data is None:
            raise ValueError(f'Failed to apply condition to the file.')
        if self and self.condition:
            self.data=self.data[self.condition]
            self.condition=None #Consume condition after applying for predictable code
        return self
    
    def applyInternalFilter(self, column:str,mask):
        '''Remove unwanted records internally (mostly rows that are not movie )'''
        self.data=self.data[self.data[column]==mask]

class MovieAgentBuilder():
    '''Orchestral class for managing callable hierarchy and the internal state of the object MovieAgent.\n
    Orchestrates the MovieAgent object(s) only.'''

    def __init__(self):
        self.movie_agent_object=None
        self.raw_data=None
        self._initAgent()

    def _initAgent(self):
        '''Orchestrates the flow of code for easy readability.'''
        movie_agent=MovieAgent()
        self.setupData(movie_agent)
        movie_agent.data=movie_agent.data[movie_agent.data['primaryTitle'].notna()&movie_agent.data['genres'].notna()] #Remove movies with NaN Primary Titles
        movie_agent.applyInternalFilter('titleType','movie') #Remove anything else than movie in records
        movie_agent.applyRenamedColumns() #Rename the columns to be more intuitive
        movie_agent.assignCondition('IMDBid', 'Average Rating', 'Number of Votes', 'Primary Title', 'Published', 'Genre') #Mutate only wanted columns
        self.movie_agent_object=movie_agent

    def setupData(self, movie_agent:MovieAgent):
        '''Setup imdb data and call on files to be merged'''
        title_imr=pl.Path(__file__).parent / 'data' / 'imdb.title.ratings.tsv' #imr=id, metadata, rating
        title_basics=pl.Path(__file__).parent / 'data' / 'imdb.title.basics.tsv' #
        title_basics_df=self.assignPath(title_basics)
        title_imr_df=self.assignPath(title_imr)
        movie_agent.data=self.mergeDataFrames(title_imr_df,title_basics_df) #insert df to be merged
        self.raw_data=self.setupRawData(movie_agent)
        return movie_agent
    
    def mergeDataFrames(self,*args:pd.DataFrame):
        '''Merges .tsv data files. Mutates self.data.'''
        result=args[0]
        if len(args)>1:
            for i in range(1,len(args)):
                result=result.merge(args[i],on='tconst')
        return result

    def assignPath(self, path: str):
        '''Assign path to selected dir'''
        path=pl.Path(path)
        try:
            readTSV=pd.read_csv(path, delimiter='\t') #Read file
        except Exception as e:
            raise IOError(f"Failed to read CSV: {e}") from e
        return readTSV

    def setupRawData(self, movie_agent:MovieAgent):
        '''Copies the raw data of movieAgent object's df'''
        self.raw_data=movie_agent.data
        return self.raw_data

class MoviePicker():
    '''Class that internally selects and give movie advice(s).\n
    Carries MovieAgent dataframe and MovieAgentBuilder raw_data internally'''
    def __init__(self, movie_agent_builder:MovieAgentBuilder, filter_tools:list[str]):
        '''Requires movieAgentBuilder object to initialize
        filter_tools: column_name, operatr, value to be filtered'''
        self.randomizer=random.Random()
        self.previous=set() #previously recommended movies. list --> IMDBid1,IMDBid2
        self.df=movie_agent_builder.movie_agent_object.data.copy()
        self.raw_data=movie_agent_builder.raw_data.copy()
        self.condition = None
        self.sort_column = None
        self.sort_ascending = True
        self.genres=self.df['Genre'].str.lower().str.split(',').explode().unique()
        self.column_map={col.lower(): col for col in self.df.columns}
        self.applyAdvice(5,filter_tools)

    def applyAdvice(self, n:int, filter_tools:list[str]):
        '''Retrieve/get movie recommendations. Main method for selection logic.\n
        n: number of movie recommendation\n
        filter_tools: Filter params: column_name, operator, value such as: Average Rating, >, 7
        '''
        column_name, operatr, value=self.assignFilterTools(filter_tools)
        candidates:pd.DataFrame=self.applyFilter(column_name, operatr, value)
        print('survived candidates', candidates)
        candidates=candidates[(candidates['Number of Votes']>10000)&(candidates['Average Rating']>7)]
        #May want CLI to ask user for sorting, probably not though
        self.assignSort('Average Rating', False)
        recommended=self.assignAdvice(n,candidates)
        return recommended
    
    def assignFilterTools(self, filter_tools:list[str]):
        operatr=None
        if len(filter_tools)==3:
            column_name, operatr, value=filter_tools
        elif len(filter_tools)==2:
            value=filter_tools[1]
            column_name=filter_tools[0]
        elif len(filter_tools)==1:
            value=filter_tools[0]
            column_name=None
        return column_name, operatr, value

    def assignAdvice(self, n,candidates):
        ''''''
        recommend:list[dict]=[]
        sorted_candidate:pd.DataFrame=self.applySort(candidates) 
        for index, row_value in sorted_candidate.iterrows():
            if row_value['IMDBid'] not in self.previous and len(recommend)<n:
                recommend.append(self.assignRecommendedHelper(row_value)) #Append richened data from sorted and filtered rows to recommended list
            if row_value['IMDBid'] not in self.previous: self.previous.add(row_value['IMDBid'])
        for j in recommend:
            print(j, '\n')
        return recommend

    def assignRecommendedHelper(self, row_value:pd.Series):
        '''Assign primary column values to a dictionary.'''
        movie_info={
            'IMDBid': row_value['IMDBid'],
            'Primary Title': row_value['Primary Title'],
            'Average Rating': row_value['Average Rating'],
            'Number of Votes': row_value['Number of Votes'],
            'Published': row_value['Published'],
            'Genre': row_value['Genre']
        }
        return movie_info

    def applyFilter(self, column_name:str, operatr:str, value:str):
        '''Apply appropiate value as filter to column_name.'''
        value=self.assignConversion(column_name, value)
        if column_name == 'Primary Title' or column_name == 'Genre':candidates=self.df[self.assignOperator(column_name, operatr, value, True)] #check for genre to make filter more inclusive.
        else:
            condition=self.assignOperator(column_name, operatr, value)
            candidates=self.df[condition]
            self.assignCondition(condition)
        return candidates
    
    def assignCondition(self, condition:pd.Series):
        '''Apply condition property for filterization'''
        if condition is None:
            self.condition=None
        else:
            self.condition=condition
    
    def assignConversion(self, column_name:str, value:str):
        '''Converts value if applicable to its column's value type.'''
        new_value=value
        if column_name is None:
            return value
        if pd.api.types.is_numeric_dtype(self.df[column_name]): 
            try: new_value=int(value)
            except ValueError: 
                try: new_value=float(value) 
                except ValueError:
                    pass
        return new_value

    def assignOperator(self, column_name:str, operator:str, value:str):
        '''Assign str variable to Python operator and return condition\n
        contains: Movies tend to have more than one genre. To avoid fixed listing, you can set this setting to true to for instance: your horror movie search includes movies that have horror and action etc.'''
        if operator is not None:
            if operator == ">":
                condition=self.df[self.column_map[column_name.lower()]]>value
            elif operator == "<":
                condition=self.df[self.column_map[column_name].lower()]<value
            elif operator == "<=":
                condition=self.df[self.column_map[column_name].lower()]<=value
            elif operator == ">=":
                condition=self.df[self.column_map[column_name].lower()]>=value
            elif operator == "==":
                condition=self.df[self.column_map[column_name].lower()]==value
            else:
                raise ValueError(f'Filter operation failed. One of the following is invalid: {column_name},{operator},{value}')
        elif column_name is not None: #User is given two strings
            condition=self.df[self.column_map[column_name]].str.lower().str.contains(value)
        elif value is not None: #User is given single string
            if value.lower() in self.genres:
                condition=self.df[self.column_map['genre']].str.lower().str.contains(value)
            else:
                condition=self.df[self.column_map['primary title']].str.lower().str.contains(value)
        return condition
    
    def assignSort(self, column:str, ascend=True):
        '''Flag sort properties of MoviePicker object based on column parameter.'''
        self.sort_ascending=ascend
        self.sort_column=column

    def applySort(self, candidates:pd.DataFrame):
        '''Apply sorting properties with respect to candidates parameter.'''
        if self.sort_column is not None:
            sorted_candidates=candidates.sort_values(self.sort_column, ascending=self.sort_ascending)
        else:
            sorted_candidates=candidates
        return sorted_candidates
                
class ServerRequests():
    '''Future'''

    def initAPI(self):
        '''Pending'''

class AppInitializer():
    ''''''
    
    def __init__(self):
        self.builder=MovieAgentBuilder()
        self.CLI=UserInterface() #['Genre', '>', 'Action']
        self.assignMoviePicker()
        
    def assignMoviePicker(self):
        self.filter_tools:list[str]=self.CLI.filter_tools
        self.advice=MoviePicker(self.builder, self.filter_tools)

if __name__ == '__main__':
    
    AppInitializer()
    
    '''
    NOTE:  

    TODO:   
            -Make program less concrete (imdb data needs downloaded somehow)
            -Sort the loaded movies with top ratings,
            -Recommend the top n amount of movies,
            -Add previously loaded to memory to avoid recommendations,
            -Load random top n amount, excluding previously loaded,
            
    ABLE TO:
            -Load data files,
            -Read .tsv files as pandas df object,
            -Call on condition to limit the view of the df,
            -Manipulate columns on the df,
            -Filter records given arguments,
            -Calculate advice,
            -Externally filter and sort,'''

    


