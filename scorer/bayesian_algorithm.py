import pandas as pd
import datetime
import pathlib as pl
from pandas import Series

class MoviePicker():
    """
    Algorithmic class that takes constrained data, outputs the best suitable movie.
    """
    def __init__(self, candidates:pd.DataFrame):
        self.raw_data=candidates.copy()
        self.data=candidates.copy()
        self.date=datetime.date.today()
        self.picks=[]
        self.file_operator = MovieFileOperator(pd.DataFrame(self.picks), self.data)
        self._convert_dtypes()
        self.recommend()
        self.file_operator=MovieFileOperator(pd.DataFrame(self.picks), self.data)
        print(self.picks, self.date)

    def _convert_dtypes(self):
        """
        For numerical operators, converts columns to appropriate primitive type.
        """
        self.data['Number of Votes']=self.data['Number of Votes'].astype(int)
        self.data['Average Rating']=self.data['Average Rating'].astype(float)
        self.data['Published']=self.data['Published'].astype(int)

    def recommend(self):
        """
        Orchestrator method for retrieval, processing of candidates and giving output.
        """
        self._build_score() #modifies self.data and adds scores as new columns
        self._pick_n_movie(3)
        return self

    def _build_score(self):
        """
        Builds bayesian algorithm taking release year, number of votes and average rating into account.
        """
        bayes_scores = []
        decay_factors = []
        adjusted_scores = []
        m=self.data['Number of Votes'].mean()
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
        self.data['Date'] = self.date
        return True
    
    def _pick_n_movie(self, n):
        """
        From score populated df, picks n amount of movies.
        """
        candidates=self.data.sort_values('Adjusted Score', ascending=False)
        for hashable, value in candidates.iterrows():
            if value['IMDBid'] not in self.file_operator.previous['IMDBid'].values and len(self.picks) < n:
                self.picks.append({'IMDBid': value['IMDBid'], 'Date': self.date})
            elif len(self.picks)>=n:
                break
        return self.picks

    @staticmethod
    def _calculate_bayesian_score(movie, m, c):
        """
        Calculate bayesian score for single movie.
        movie: single pandas row
        m: median of number of votes in entire df
        C: mean of average rating in entire df
        Returns: weighted score
        """
        v=movie['Number of Votes']
        r=movie['Average Rating']
        bayes_score=(v/(v+m)) * r + (m/(v+m) * c)
        return bayes_score
    
    @staticmethod
    def _calculate_decay_factor(movie):
        """
        Calculate decay factor for single movie.
        """
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

class MovieFileOperator():
    """
    Class that handles file operations for orchestrator class.
    """

    def __init__(self, picks_df:pd.DataFrame, main_data:pd.DataFrame):
        """"""
        self.previous=None
        self.data=main_data
        self.picks_df=picks_df
        self.data_path=pl.Path(__file__).parent.parent / 'data' / 'main_data.parquet'
        self.previous_path=pl.Path(__file__).parent.parent / 'data' / 'previous_data.parquet'
        self.bayesian_path= pl.Path(__file__).parent.parent / 'data' / 'bayesian_data.parquet'
        self._process_file_memory()
        self._process_file_save(self.picks_df)

    def _process_file_save(self, picks_df):
        """
        Orchestrate saving and expanding previous movies and bayesian scores.
        """
        print(f'B_df:\n{self.bayesian.to_string()}\n')
        self.previous=pd.concat([self.previous,picks_df],ignore_index=True)
        self.bayesian = pd.concat([self.bayesian, self.data], ignore_index=True)
        self._save_file(self.data, self.data_path)
        self._save_file(self.bayesian,self.bayesian_path)
        self._save_file(self.previous,self.previous_path)

    def _process_file_memory(self):
        """

        """
        self._load_memory()
        self._clear_memory()

    def _clear_memory(self):
        """

        """
        self.data.drop_duplicates()

    def _load_memory(self):
        """
        Load all saved files and scores into the cache, if file not found, or corrupted, reset it.
        """

        data_load = self._load_file(self.data_path)
        if data_load is not pd.DataFrame:
            pass
        else:
            self.data = data_load

        previous_load = self._load_file(self.previous_path)
        if previous_load is not pd.DataFrame:
            self.previous = pd.DataFrame(columns=['IMDBid', 'Date'])
        else:
            self.previous = previous_load

        bayesian_load = self._load_file(self.bayesian_path)
        if bayesian_load is not pd.DataFrame:
            self.bayesian = pd.DataFrame(columns=['IMDBid', 'Date', 'Bayes Score', 'Decay Factor', 'Adjusted Score'])
        else:
            self.bayesian = bayesian_load
        return True

    def _save_file(self, file: pd.DataFrame, path: pl.Path):
        """
        Save previously recommended movies df.
        """
        file.to_parquet(str(path))
        return self

    @staticmethod
    def _load_file(path: pl.Path):
        """
        Load parquet files with boolean failure case return.
        """
        try:
            file = pd.read_parquet(str(path))
        except FileNotFoundError:
            return False
        except ValueError:
            return False
        return file

if __name__ == '__main__':
    data=[{'IMDBid': 'tt0209144', 'Primary Title': 'Memento', 'Average Rating': 8.4, 'Number of Votes': 1415506, 'Published': '2000', 'Genre': 'Drama,Mystery,Thriller'},
                {'IMDBid': 'tt0898367', 'Primary Title': 'The Road', 'Average Rating': 7.2, 'Number of Votes': 267643, 'Published': '2009', 'Genre': 'Drama,Thriller'},
                {'IMDBid': 'tt0126886', 'Primary Title': 'Election', 'Average Rating': 5.1, 'Number of Votes': 110438, 'Published': '1999', 'Genre': 'Comedy,Romance'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Treasure Planet', 'Average Rating': 7.2, 'Number of Votes': 145618, 'Published': '1980', 'Genre': 'Action,Adventure,Animation'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Casablanca', 'Average Rating': 8.5, 'Number of Votes': 6145618, 'Published': '1942', 'Genre': 'Action,Adventure,Animation'},
                {'IMDBid': 'tt0133240', 'Primary Title': 'Metropolis', 'Average Rating': 9.5, 'Number of Votes': 75618, 'Published': '2020', 'Genre': 'Action,Adventure,Animation'}]
    candidates_df=pd.DataFrame(data)
    algo=MoviePicker(candidates_df)
    