from sqlalchemy.orm import Session

from . import models, schemas
from sqlalchemy import and_, or_, func, cast, Integer
from typing import Union
import json, requests

API_KEY = "9ab68902-3f25-4848-8384-3a217a763e5a"

# check if there are duplicate movies
def get_movie_match(db: Session, openDate: str, title: str, runningTimeMinute: str, titleEng: str):
    name = db.query(models.Movie).filter(models.Movie.title == title).first()
    nameEng = db.query(models.Movie).filter(models.Movie.titleEng == titleEng).first()
    runningtime = db.query(models.Movie).filter(models.Movie.runningTimeMinute == runningTimeMinute).first()
    openDate = db.query(models.Movie).filter(models.Movie.openDate == openDate).first()
    result = 0
    if nameEng is not None and name is not None and runningtime is not None and openDate is not None:
        result = 1
    return result

# insert movie metadata into SQLite database
def insert_data_into_db(db: Session, data: schemas.Movie):
    db_movie = models.Movie(title = data.title,
                            titleEng = data.titleEng,
                            openDate = data.openDate,
                            runningTimeMinute = data.runningTimeMinute)
    db_movie.set_list_field("genre", data.genre)
    db_movie.set_list_field("actors", data.actors)
    db_movie.set_list_field("directors", data.directors)
    db_movie.set_list_field("producer", data.producer)
    db_movie.set_list_field("distributor", data.distributor)
    db_movie.set_list_field("keywords", data.keywords)
    db_movie.set_list_field("posterUrl", data.posterUrl)
    db_movie.set_list_field("vodUrl", data.vodUrl)
    db_movie.set_dict_field("synopsis", data.synopsis)

    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# search movie : accessing from the SQLite database. 
def search_movies(db: Session, search_query: Union[str, None] = None):
    query = db.query(models.Movie)
    if search_query is not None:
        matching_movies = []
        for movie in query.all():
            movie_directors = json.loads(movie.directors)
            movie_actors = json.loads(movie.actors)
            movie_keywords = json.loads(movie.keywords)
            if search_query in movie_directors:
                matching_movies.append(movie)
            if search_query in movie_actors:
                matching_movies.append(movie)
            if search_query in movie_keywords:
                matching_movies.append(movie)
            if movie.title == search_query:
                matching_movies.append(movie)
        return matching_movies

    return query.all()

# filtering tool: filter by the range of year released (openDate)
def get_opendate(db: Session, openyear: Union[int, None]=0, endyear: Union[int, None]=9999):
    query = db.query(models.Movie).filter(models.Movie.openDate != None)

    if openyear is not None:
        query = query.filter(func.cast(func.substring(models.Movie.openDate, 1, 4), Integer) >= openyear)
    if endyear is not None:
        query = query.filter(func.cast(func.substring(models.Movie.openDate, 1, 4), Integer) <= endyear)

    return query.all()

# filtering tool: filter by genres (union method)
def get_genre(db: Session, genres: list[str]):
    query = db.query(models.Movie).filter(models.Movie.genre != None)

    if genres is not None and genres:
        matching_movies = []
        for movie in query.all():
            movie_genres = json.loads(movie.genre)
            if any(genre in movie_genres for genre in genres):
                matching_movies.append(movie)
        return matching_movies

    return query.all()

def all_movies_dataset(dataset_list: list, result: list, final:list):
    for movie in dataset_list:
        for filtered_movie in result:
            if movie['name'] == filtered_movie.title and json.loads(movie["description"])['synopsis']['plotText'] == (filtered_movie.synopsis)['plotText']:
                final.append(json.loads(movie["description"]))
    return final

def searchquery(db: Session, genres: list[str], openyear: Union[int, None]=0, endyear: Union[int, None]=9999, offset: int = 0,
limit: int = 10, q: Union[str,None]=None):
    result = filtering(db, genres, openyear, endyear)
    final = []
    if q is not None:
        start = 0
        rows = 10
        while(True):
            url = f"https://snu.dataverse.ac.kr/api/search?q={q}&subtree=movies&start={start}"
            headers = {
                "X-Dataverse-key": API_KEY
            }
            response = requests.get(url, headers = headers)

            if response.status_code == 200:
                dataset_list = response.json()["data"]["items"]
                final = all_movies_dataset(dataset_list, result, final)

                total = response.json()["data"]["total_count"]
                start += rows

                if start >= total:
                    break
            else:
                return "검색 결과 없음"
    else:
        final = result
            
    # Apply offset and limit to the final result
    paginated_final = final[offset : offset + limit]
    paginated_final.append(len(paginated_final))  # Adding total count
    return paginated_final

# filtering tool: filter movies by range of year released and genres
def filtering(db: Session, genres: list[str], openyear: Union[int, None]=0, endyear: Union[int, None]=9999, q: Union[str,None]=None):
    query = db.query(models.Movie).filter(models.Movie.openDate != None)

    if openyear is not None:
        query = query.filter(func.cast(func.substring(models.Movie.openDate, 1, 4), Integer) >= openyear)
    if endyear is not None:
        query = query.filter(func.cast(func.substring(models.Movie.openDate, 1, 4), Integer) <= endyear)
    if genres is not None and genres:
        matching_movies = []
        for movie in query.all():
            # movie_genres = json.loads(movie.genre)
            movie_genres = movie.get_list_field('genre')
            if any(genre in movie_genres for genre in genres):
                movie.genre =  movie.get_list_field('genre')
                movie.directors =  movie.get_list_field('directors')
                movie.distributor =  movie.get_list_field('distributor')
                movie.posterUrl =  movie.get_list_field('posterUrl')
                movie.actors =  movie.get_list_field('actors')
                movie.producer =  movie.get_list_field('producer')
                movie.keywords =  movie.get_list_field('keywords')
                movie.vodUrl =  movie.get_list_field('vodUrl')
                movie.synopsis =  movie.get_dict_field('synopsis')
                matching_movies.append(movie)

        # Sort the matching movies by openDate in descending order
        matching_movies.sort(key=lambda movie: movie.openDate, reverse=True)
            
        return matching_movies
    
    matching_movies = query.order_by(models.Movie.openDate.desc()).all()
    for movie in matching_movies:
        movie.genre =  movie.get_list_field('genre')
        movie.directors =  movie.get_list_field('directors')
        movie.distributor =  movie.get_list_field('distributor')
        movie.posterUrl =  movie.get_list_field('posterUrl')
        movie.actors =  movie.get_list_field('actors')
        movie.producer =  movie.get_list_field('producer')
        movie.keywords =  movie.get_list_field('keywords')
        movie.vodUrl =  movie.get_list_field('vodUrl')
        movie.synopsis =  movie.get_dict_field('synopsis')
    return matching_movies

# Delete all from the databse
def delete_all_records(db: Session):
    db.query(models.Movie).delete()
    db.commit()
