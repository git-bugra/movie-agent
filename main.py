import requests
import random
import pandas as pd
import pathlib as pl
import pdb
from ui.user_interface import UserInterface
import time

class MovieAgent():
    '''Main object responsible for clearing, fixing columns and internally consume columns.\n
    Carries data internally.'''
    def __init__(self):
        self.data=None
        self.condition=None
    
    def rename_columns(self):
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

    def select_columns(self, *args:str):
        '''Internal limitation the data with given columns.
        Call data to be mutated with given arguments.
        
        *args: Names of the columns to limit'''
        columns_to_limit=[*args]
        if len(columns_to_limit)>0:self.condition=columns_to_limit
        try:self._apply_column_selection()
        except KeyError as e:raise KeyError(f"With given arguments, column not found: {e}") from e
        return self

    def _apply_column_selection(self):
        '''Based on condition, mutate the data to display'''
        if self.data is None:
            raise ValueError(f'Failed to apply condition to the file.')
        if self and self.condition:
            self.data=self.data[self.condition]
            self.condition=None #Consume condition after applying for predictable code
        return self
    
    def filter_rows(self, column:str,mask):
        '''Remove unwanted records internally (mostly rows that are not movie )'''
        self.data=self.data[self.data[column]==mask]

class MovieAgentBuilder():
    '''Orchestral class for managing callable hierarchy and the internal state of the object MovieAgent.\n
    Orchestrates the MovieAgent object(s) only.'''

    def __init__(self):
        self.movie_agent_object=None
        self.raw_data=None
        self.preprocessed_path=pl.Path(__file__).parent / 'data' / 'preprocessed_data.parquet'
        self._build_agent()

    def _build_agent(self):
        '''Orchestrates the flow of code for easy readability.'''
        movie_agent=MovieAgent()
        self.load_data(movie_agent)
        self.movie_agent_object=movie_agent

    def load_data(self, movie_agent:MovieAgent):
        '''Setup imdb data and call on files to be modified'''
        start=time.time()
        if pl.Path.exists(self.preprocessed_path):
            movie_agent.data=pd.read_parquet(self.preprocessed_path)
        else:
            title_imr=pl.Path(__file__).parent / 'data' / 'imdb.title.ratings.tsv' #imr=id, metadata, rating
            title_basics=pl.Path(__file__).parent / 'data' / 'imdb.title.basics.tsv' #
            title_basics_df=self.read_tsv_file(title_basics)
            title_imr_df=self.read_tsv_file(title_imr)
            movie_agent.data=self.merge_dataframes(title_imr_df,title_basics_df) #insert df to be merged
            movie_agent.data=movie_agent.data[movie_agent.data['primaryTitle'].notna()&movie_agent.data['genres'].notna()] #Remove movies with NaN Primary Titles
            movie_agent.filter_rows('titleType','movie') #Remove anything else than movie in records
            movie_agent.rename_columns() #Rename the columns to be more intuitive
            movie_agent.select_columns('IMDBid', 'Average Rating', 'Number of Votes', 'Primary Title', 'Published', 'Genre') #Mutate only wanted columns
            self._save_dataframe(movie_agent.data)
        print(f"Operation runtime: {time.time()-start}")
        self.raw_data=self._copy_raw_data(movie_agent)
        return movie_agent

    def merge_dataframes(self,*args:pd.DataFrame):
        '''Merges .tsv data files. Mutates self.data.'''
        result=args[0]
        if len(args)>1:
            for i in range(1,len(args)):
                result=result.merge(args[i],on='tconst')
        return result

    def read_tsv_file(self, path: str):
        '''Read TSV file from given path'''
        path=pl.Path(path)
        try:
            readTSV=pd.read_csv(path, delimiter='\t') #Read file
        except Exception as e:
            raise IOError(f"Failed to read CSV: {e}") from e
        return readTSV

    def _copy_raw_data(self, movie_agent:MovieAgent):
        '''Copies the raw data of movieAgent object's df'''
        self.raw_data=movie_agent.data
        return self.raw_data
    
    def _save_dataframe(self, data=pd.DataFrame):
        data.to_parquet(self.preprocessed_path)
        print('Data is preprocessed and saved.')

class MoviePicker():
    '''Class that internally selects and gives movie advice(s).\n
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
        self.get_recommendations(5,filter_tools)

    def get_recommendations(self, n:int, filter_tools:list[list[str]]):
        '''Retrieve/get movie recommendations. Main method for selection logic.\n
        n: number of movie recommendation\n
        filter_tools: Filter params: column_name, operator, value such as: Average Rating, >, 7
        '''
        #Check if column_name, operatr, value valid in dataframe
        candidates=self.apply_all_filters(filter_tools)
        self.configure_sort('Average Rating', False)
        recommended=self._select_movies(n,candidates)
        return recommended
    
    def _parse_filter_tools(self, filter_tools:list[str]):
        '''Based on the argument length, assign variables to apply filters.
        This is needed for allowing user to type in titles and genres without explicit operations.'''
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

    def _select_movies(self, n, candidates):
        '''Based on given candidates and n as int, print and return the list of recommend which has movies with their information.'''
        recommend:list[dict]=[]
        sorted_candidate:pd.DataFrame=self.sort_candidates(candidates) 
        for index, row_value in sorted_candidate.iterrows():
            if row_value['IMDBid'] not in self.previous and len(recommend)<n:
                recommend.append(self._row_to_dict(row_value)) #Append richened data from sorted and filtered rows to recommended list
            if row_value['IMDBid'] not in self.previous: self.previous.add(row_value['IMDBid'])
        print('\033c') #Remove previous lines
        for j in recommend:
            print(j, '\n')
        return recommend

    def _row_to_dict(self, row_value:pd.Series):
        '''Convert row to dictionary with primary column values.'''
        movie_info={
            'IMDBid': row_value['IMDBid'],
            'Primary Title': row_value['Primary Title'],
            'Average Rating': row_value['Average Rating'],
            'Number of Votes': row_value['Number of Votes'],
            'Published': row_value['Published'],
            'Genre': row_value['Genre']
        }
        return movie_info

    def apply_all_filters(self, filter_tools:list[list[str]]):
        '''Unpacks filter tools and applies each filter in it manually.'''
        candidates=self.df
        for filters in filter_tools:
            column_name, operatr, value=self._parse_filter_tools(filters)
            self.apply_filter(column_name, operatr, value)
            candidates=candidates[self.condition]
        return candidates

    def apply_filter(self, column_name:str, operatr:str, value:str):
        '''Apply appropiate value as filter to column_name.'''
        value=self._convert_value(column_name, value)
        if column_name == 'Primary Title' or column_name == 'Genre':candidates=self.df[self._build_filter_condition(column_name, operatr, value, True)] #check for genre to make filter more inclusive.
        else:
            condition=self._build_filter_condition(column_name, operatr, value)
            candidates=self.df[condition]
            self._store_condition(condition)
        return candidates
    
    def _store_condition(self, condition:pd.Series):
        '''Store condition property for filterization'''
        if condition is None:
            self.condition=None
        else:
            self.condition=condition
    
    def _convert_value(self, column_name:str, value:str):
        '''Convert value if applicable to its column's value type.'''
        new_value=value
        if column_name is None:
            return value
        if pd.api.types.is_numeric_dtype(self.df[column_name]): 
            try: new_value=int(value)
            except ValueError: 
                try: new_value=float(value) 
                except ValueError:
                    raise ValueError
        return new_value

    def _build_filter_condition(self, column_name:str, operator:str, value:str):
        '''Build pandas condition based on column, operator, and value\n
        contains: Movies tend to have more than one genre. To avoid fixed listing, you can set this setting to true to for instance: your horror movie search includes movies that have horror and action etc.'''
        if operator is not None:
            condition=self.df[self.column_map[column_name.lower()]]
            if operator == ">":
                return condition>value
            elif operator == "<":
                return condition<value
            elif operator == "<=":
                return condition<=value
            elif operator == ">=":
                return condition>=value
            elif operator == "==":
                return condition==value
            else:
                raise ValueError(f'Filter operation failed. One of the following is invalid: {column_name},{operator},{value}')
        elif value is not None:
            condition=self._build_string_condition(column_name, value)
        else: raise ValueError(f'Operation failed. One of the following is invalid: {column_name},{operator},{value}')
        return condition
    
    def _build_string_condition(self, column_name:str, value):
        '''Helper function that checks data for broader string matches, not exact.'''
        if column_name is not None: #User is given two strings
            condition=self.df[self.column_map[column_name.lower()]].str.lower().str.contains(value)
        else: #User is given single string
            if value.lower() in self.genres:
                condition=self.df[self.column_map['genre']].str.lower().str.contains(value)
            else:
                condition=self.df[self.column_map['primary title']].str.lower().str.contains(value)
        return condition
    
    def configure_sort(self, column:str, ascend=True):
        '''Set sort properties of MoviePicker object based on column parameter.'''
        self.sort_ascending=ascend
        self.sort_column=column

    def sort_candidates(self, candidates:pd.DataFrame):
        '''Apply sorting properties with respect to candidates parameter.'''
        if self.sort_column is not None:
            sorted_candidates=candidates.sort_values(self.sort_column, ascending=self.sort_ascending)
        else:
            sorted_candidates=candidates
        return sorted_candidates
                
class ServerRequests():
    '''Future'''

    def init_api(self):
        '''Pending'''

class AppManager():
    '''Main orchestrator that assembles necessary classes and communication.'''
    
    def __init__(self):
        self.builder=MovieAgentBuilder()
        self.CLI=UserInterface() #Expects prompts like Average Rating>5 or Shawshank Redemption
        self._create_movie_picker()
        
    def _create_movie_picker(self):
        self.filter_tools:list[str]=self.CLI.all_filter_tools #Needs work
        self.advice=MoviePicker(self.builder, self.filter_tools)

if __name__ == '__main__':
    AppManager()
    
    '''
    NOTE:  86x faster runtime update

            -Add abstraction layers,
            -Add fully operational multi filtering,
            -Add data load and saving for faster runtime,
            -Fix high debugging overhead,
            -Add better instruction prints.

    TODO:   
            -Make program less concrete (imdb data needs downloaded somehow)
            -Sort the loaded movies with top ratings,
            -Load random top n amount, excluding previously loaded,
            -Add https request handling,
            -Add constant backend data insertion and update,
            -Need to check validation for user filters.
            
    ABLE TO:
            -Load data files,
            -Read .tsv files as pandas df object,
            -Call on condition to limit the view of the df,
            -Manipulate columns on the df,
            -Filter records given arguments,
            -Calculate advice,
            -Externally filter and sort,
            -Add previously loaded to memory to avoid recommendations,
            -Recommend the top n amount of movies,'''

    


