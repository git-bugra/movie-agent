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
        self._setupAgent
        self.data=None
        self.raw_data=None
        self.condition=None

    def _setupAgent(self):
        '''Orchestrates the flow of code for easy readability.'''
        self.setupData()
        self.applyRenamedColumns() #Rename the columns
        self.assignCondition('IMDBid', 'Average Rating', 'Number of Votes', 'Primary Title', 'Published', '')

    def setupData(self):
        '''Setup imdb data to program and call on files to be merged'''
        title_imr=pl.Path(__file__).parent / 'data' / 'imdb.title.ratings.tsv' #imr=id, metadata, rating
        title_basics=pl.Path(__file__).parent / 'data' / 'imdb.title.basics.tsv' #
        title_basics_df=self.assignPath(title_basics)
        title_imr_df=self.assignPath(title_imr)
        self.mergeDataFrames(title_imr_df,title_basics_df) #insert df to be merged
        #Space to insert pretty print
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
        self.raw_data=result
        self.data=result
        return self
    
    def applyRenamedColumns(self):
            '''Make columns more readable and intuitive'''
            self.data=self.data.rename(columns={'tconst': 'IMDBid', 
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
            
            print(self.data.columns)
            return self

    def assignCondition(self, *args:str):
        '''Internal limitation the data with given columns.
        Mutates data to given arguments.
        
        *args: Names of the columns to limit'''
        columns_to_limit=[*args]
        if len(columns_to_limit)>1:self.condition=columns_to_limit
        self.applyCondition()
        return self

    def applyCondition(self):
        '''Based on condition, adjust the data to display'''
        if not self:
            raise ValueError(f'Failed to apply condition to the file.')
        if self and self.condition:
            self.data=self.data[self.condition]
            self.condition=False
        return self
    
    def filterData():
            ''''''

def initAPI():
    '''Pending'''

def initCLI():
    '''Manipulate and communicate to the object and take actions via CLI commands.
    -WIP'''

def recommendationLogic():
    '''
    '''

if __name__ == '__main__':
    main=MovieAgent()

    '''Structural fixes and code improvement
            
            -Fix persistent condition affect, 
            -Add future recovery tools,
            -Add intuitive columns,
            -Add internally limited columns,
            -Fix indentation errors,
            -
            
    TODO:   
            -Make program less concerete (imdb data needs downloaded somehow)
            -Sort the loaded movies with top ratings,
            -Recommend the top n amount,
            -Add previously loaded to memory,
            -Load random top n amount, excluding previously loaded,
            -Add user filtering.
            
    Current:
    
            -Load data files,
            -Read .tsv files as pandas df object,
            -Call on condition to limit the view of the df.'''

    


