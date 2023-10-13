import sqlite3
from random import choice, sample

class DataBase:
    def __init__(self) -> None:
        self._con = sqlite3.connect(r'C:\Users\User\Desktop\telebot fims\database.db')
        self._cur = self._con.cursor()
        self._create_movie_table()
        

    def _create_movie_table(self) -> None:
        self._cur.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name  STRING  NOT NULL,
            genre STRING,
            year  INTEGER,
            link  STRING
        )
        ''')
        self._con.commit()

    def fill_movie_table(self, movies) -> None:
        self._cur.execute('DROP TABLE movies')
        self._con.commit()
        self._create_movie_table()
        for movie in movies[::-1]:
            self._cur.execute('''
            INSERT INTO movies (name, genre, year, link) VALUES (?, ?, ?, ?)
            ''', (movie['name'], movie['genre'], movie['year'], movie['link'])
            )
        self._con.commit()

    def add_movie(self, movie):
        self._cur.execute('INSERT INTO movies (name, genre, year, link) VALUES (?, ?, ?, ?)', (movie['name'], movie['genre'], movie['year'], movie['link']))
        self._con.commit()

    def update_movie_table(self, movie) -> bool:
        self._cur.execute("""
            SELECT * FROM movies
            WHERE link=?
        """, movie['link'])

        if self._cur.fetchone():
            self._cur.execute('''
            INSERT INTO movies (name, genre, year, link) VALUES (?, ?, ?, ?)
            ''', (movie['name'], movie['genre'], movie['year'], movie['link']))
        else:
            return False
        return True

    
    def get_movies(self, genres : tuple = None, years : tuple = None) -> list:
        movies = []
        sql_start = 'SELECT name, genre, year, link FROM movies '

        if genres:
            if years:
                for genre in genres:
                    for year in years:
                        self._cur.execute(sql_start + 'WHERE genre=? AND year=?', (genre, int(year)))
                        movies.extend(self._cur.fetchall())
            else:
                for genre in genres:
                    self._cur.execute(sql_start + 'WHERE genre=?', (genre, ))
                    movies.extend(self._cur.fetchall())
        else:
            if years:
                for year in years:
                    self._cur.execute(sql_start + 'WHERE year=?', (int(year), ))
                    movies.extend(self._cur.fetchall())
            else:
                self._cur.execute('SELECT name, genre, year, link FROM movies')
                movies = self._cur.fetchall()
    
        return movies
    
    def get_random_movie(self, genres : tuple = None, years : tuple = None) -> tuple:
        movies = self.get_movies(genres=genres, years=years)
        return choice(movies) if len(movies) > 0 else None

    def get_random_movies(self, amount : int, genres : tuple = None, years : tuple = None) -> list:
        assert amount > 0
        movies = self.get_movies(genres=genres, years=years)
        if len(movies) <= 0:
            return None
        elif len(movies) >= amount:
            return movies
        else:
            return sample(movies, amount)
    

    
    def __del__(self):
        self._cur.close()
        self._con.close()

def main():
    db = DataBase()
    print(db.get_movies(genres=('genre5', )))

if __name__ == '__main__':
    main()