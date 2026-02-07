import pandas as pd
import datetime

class MoviePicker():
    '''
    Algorithmic class that takes constrained data, outputs the best suitable movie.
    Uses N systems to do this
    '''
    
    def __init__(self, candidates:pd.DataFrame):
        self.raw_data=candidates.copy()
        self.data=candidates.copy()
        self._convert_dtypes()
        self.recommend_one()

    def _convert_dtypes(self):
        self.data['Number of Votes']=self.data['Number of Votes'].astype(int)
        self.data['Average Rating']=self.data['Average Rating'].astype(float)
        self.data['Published']=self.data['Published'].astype(int)

    def recommend_one(self):
        '''
        '''
        self._build_score() #modifies self.data and adds scores as new columns
        print('MOVIEPICKER_DF:\n',self.data.to_string())

    def _build_score(self):
        bayes_scores = []
        decay_factors = []
        adjusted_scores = []
        m=self.data['Number of Votes'].median()
        m=25000
        c=self.data['Average Rating'].mean()
        for index, movie in self.data.iterrows():
            b_score=self._calculate_bayesian_score(movie, m, c)
            d_factor=self._calculate_decay_factor(movie)
            a_score=b_score*d_factor
            bayes_scores.append(b_score)
            decay_factors.append(d_factor)
            adjusted_scores.append(a_score)
        self.data['Bayes Score'] = bayes_scores
        self.data['Decay Factor'] = decay_factors
        self.data['Adjusted Score'] = adjusted_scores
        return self.data

    def _calculate_bayesian_score(self, movie, m, c):
        '''
        movie: single pandas row
        m: median of number of votes in entire df
        C: mean of average rating in entire df
        Returns: weighted score
        '''
        v=movie['Number of Votes']
        r=movie['Average Rating']
        bayes_score=(v/(v+m)) * r + (m/(v+m) * c)
        return bayes_score
    
    def _calculate_decay_factor(self, movie):
        # Private adjustment method
        ''''''
        years_old=datetime.date.today().year-int(movie['Published'])
        if years_old<10:
            decay_factor=0.9997**years_old
        elif years_old<15:
            decay_factor=0.9996**years_old
        elif years_old<20:
            decay_factor=0.9995**years_old
        elif years_old<30:
            decay_factor=0.9994**years_old
        elif years_old<45:
            decay_factor=0.9993**years_old
        else:
            decay_factor=0.9992**years_old
        return decay_factor

    def _retain_algorithmic_stability(self):
        ''''''
    
if __name__ == '__main__':
    data=[{'IMDBid': 'tt0209144', 'Primary Title': 'Memento', 'Average Rating': 8.4, 'Number of Votes': 1415506, 'Published': '2000', 'Genre': 'Drama,Mystery,Thriller'},
                {'IMDBid': 'tt0898367', 'Primary Title': 'The Road', 'Average Rating': 7.2, 'Number of Votes': 267643, 'Published': '2009', 'Genre': 'Drama,Thriller'},
                {'IMDBid': 'tt0126886', 'Primary Title': 'Election', 'Average Rating': 5.1, 'Number of Votes': 110438, 'Published': '1999', 'Genre': 'Comedy,Romance'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Treasure Planet', 'Average Rating': 7.2, 'Number of Votes': 145618, 'Published': '1980', 'Genre': 'Action,Adventure,Animation'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Casablanca', 'Average Rating': 8.5, 'Number of Votes': 6145618, 'Published': '1942', 'Genre': 'Action,Adventure,Animation'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Metropolis', 'Average Rating': 8.5, 'Number of Votes': 6145618, 'Published': '1924', 'Genre': 'Action,Adventure,Animation'}]
    candidates_df=pd.DataFrame(data)
    algo=MoviePicker(candidates_df)
    