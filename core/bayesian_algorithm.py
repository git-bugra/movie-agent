import pandas as pd

class MoviePicker():
    '''
    Algorithmic class that takes constrained data, outputs the best suitable movie.
    Uses N systems to do this
    '''
    
    def __init__(self, candidates:pd.DataFrame):
        self.data=None
        self.recency_factor=None
        self.bayesian_score=None
        self.v=None
        self.m=None
        self.R=None
        self.C=None
        self.recommend_one(candidates)

    def recommend_one(self, candidates):
        # Main public method
        # Takes filtered candidates, returns best one
        ''''''
        

    def _calculate_bayesian_score(self, movie):
        # Private scoring method
        ''''''
    
    def _calculate_recency_factor(self, score, year):
        # Private adjustment method
        ''''''

    def _retain_algorithmic_stability():
        ''''''
    
if __name__ == '__main__':
    candidates=[{'IMDBid': 'tt0209144', 'Primary Title': 'Memento', 'Average Rating': 8.4, 'Number of Votes': 1415506, 'Published': '2000', 'Genre': 'Drama,Mystery,Thriller'},
                {'IMDBid': 'tt0898367', 'Primary Title': 'The Road', 'Average Rating': 7.2, 'Number of Votes': 267643, 'Published': '2009', 'Genre': 'Drama,Thriller'},
                {'IMDBid': 'tt0126886', 'Primary Title': 'Election', 'Average Rating': 7.2, 'Number of Votes': 110438, 'Published': '1999', 'Genre': 'Comedy,Romance'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Treasure Planet', 'Average Rating': 7.2, 'Number of Votes': 145618, 'Published': '2002', 'Genre': 'Action,Adventure,Animation'}]
    
    algo=MoviePicker(candidates)