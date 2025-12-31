import requests
import random
import json
import pandas as pd
import pathlib as pl

'''key=input('Enter OMDB API key\n')
request=requests.get(f'http://www.omdbapi.com/?apikey={key}&i=tt0108052')
'''

class MovieAgent():
    '''Main object. Carries data internally'''
    def __init__(self):
        self.injectData()
        self.data=None
        self.condition=None

    def injectData(self):
        '''Inject imdb data to program'''
        title_imr=pl.Path(__file__).parent / 'data' / 'imdb.title.ratings.tsv' #imr=id, metadata, rating
        title_basics=pl.Path(__file__).parent / 'data' / 'imdb.title.basics.tsv' #
        title_basics_df=self.assignPath(title_basics)
        title_imr_df=self.assignPath(title_imr)
        self.mergeDataFrames(title_imr_df,title_basics_df) #insert df to be merged
        return self

    def assignPath(self, path: str):
        '''Assign path to user selected dir'''
        path = pl.Path(path)
        try:
            main = pd.read_csv(path, delimiter='\t') #Read file
        except Exception as e:
            raise IOError(f"Failed to read CSV: {e}") from e
        return main
    
    def mergeDataFrames(self,*args:pd.DataFrame):
        '''Merge .tsv data files'''
        result=args[0]
        if len(args)>1:
            for i in range(1,len(args)):
                result=result.merge(args[i],on='tconst')
        self.data=result
        return self
    
    def assignCondition(self, *args:str):
        '''Limit the data with given columns.
        
        *args: Names of the columns to limit'''
        columns_to_limit=[*args]
        if len(columns_to_limit)>1:self.condition=columns_to_limit
        configureFile(self)
        return self

def configureFile(movie_agent:MovieAgent):
    '''Based on condition, adjust the data to display'''
    if movie_agent and movie_agent.condition:
        movie_agent.data=movie_agent.data[movie_agent.condition]
    elif not movie_agent:
        raise ValueError(f'Failed to configure the file. MovieAgent.data: {movie_agent.data}')
    return movie_agent

def configureAPI():
    '''Pending'''

def configureCLI():
    '''Manipulate and communicate to the object and take actions via CLI commands.'''

def genreFiltering():
    ''''''

def recommendationLogic():
    '''
    '''

if __name__ == '__main__':
    main=MovieAgent()

    '''Initialize main callables and set data
            
            -Add internal table configuration,
            -Fix verbose and unecessary variables,
            -
            
    TODO:   
            -Make program less concerete (imdb data needs downloaded somehow)
            -Sort the loaded movies with top ratings,
            -Recommend the top n amount,
            -Put previously loaded to memory,
            -Load random top n amount, excluding previously loaded,


            
    Current:
    
            -Load data files,
            -Read .tsv files as pandas df object,
            -Call on condition to limit the view of the df.'''

    


