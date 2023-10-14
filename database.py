import sqlite3

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
            self._con.commit()
        else:
            return False
        return True
    

    def get_random_movies(self, amount : int, genres : tuple = None, years : tuple = None) -> list:
        if amount <= 0:
            return None
        
        sql_request = 'SELECT name, genre, year, link FROM movies '
        
        if genres:
            genres_tuple_str = '('
            for genre in genres:
                genres_tuple_str += f"'{genre}', "
            sql_request += 'WHERE genre IN ' + genres_tuple_str[:-2] + ') '


        if years:
            years_tuple_str = '('
            for year in years:
                years_tuple_str += f"{year}, "

            if genres:
                sql_request += 'AND year IN ' + years_tuple_str[:-2] + ') '
            else:
                sql_request += 'WHERE year IN ' + years_tuple_str[:-2] + ') '

        sql_request += f'ORDER BY RANDOM() LIMIT {amount}'

        self._cur.execute(sql_request)

        movies = self._cur.fetchall()
        if len(movies) == 0:
            return None

        return movies
    
    def __del__(self):
        self._cur.close()
        self._con.close()

def main():
    db = DataBase()
    print(db.get_random_movies(5, genres=('Бойовики', 'Трилери'), years=('2022',  '2023')))

if __name__ == '__main__':
    main()