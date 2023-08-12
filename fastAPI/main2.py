from typing import Union
from fastapi import FastAPI, Query, Depends, FastAPI, HTTPException
import requests
import json
from sqlalchemy.orm import Session
from sql_app import crud, models, schemas
from sql_app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


API_KEY = "9ab68902-3f25-4848-8384-3a217a763e5a"

def all_movies_dataset(dataset_list: list, result: list):
    for movie in dataset_list:
        result.append(json.loads(movie["description"]))
    return result

# Search bar tool: search movie; access directly from Dataverse database
# returns a list with each movie metadata as an item in dict format
@app.get("/movies/") 
def read_movie(q: Union[str, None] = None):
    result = []
    condition = True
    start = 0
    rows = 10
    while(condition):
        if q == None:
            url = f"https://snu.dataverse.ac.kr/api/search?q=*&subtree=movies&start={start}"
        else:
            url = f"https://snu.dataverse.ac.kr/api/search?q={q}&subtree=movies&start={start}"
        headers = {
            "X-Dataverse-key": API_KEY
        }
        response = requests.get(url, headers = headers)
        total = response.json()["data"]["total_count"]
        start = start + rows
        condition = start < total

        if response.status_code == 200:
            dataset_list = response.json()["data"]["items"]
            result = all_movies_dataset(dataset_list, result)
        else:
            return "검색 결과 없음"
    return result
    
# @app.get("/movies/search/")
# def search_movies_endpoint(search_query: Union[str, None] = None, db: Session = Depends(get_db)):
#     movies = crud.search_movies(db, search_query)
#     return movies

@app.post("/movies/upload/")
def create_movies(data: list[schemas.Movie], db: Session = Depends(get_db)):
    results = []
    for per_movie in data:
        print(per_movie)
        db_movie = crud.get_movie_match(db, openDate=per_movie.openDate, title=per_movie.title, titleEng=per_movie.titleEng, runningTimeMinute=per_movie.runningTimeMinute)
        if db_movie:
            raise HTTPException(status_code=400, detail="Movie already registered")
        result = crud.insert_data_into_db(db=db, data=per_movie)
        results.append(result)
    return results

@app.get("/movies/filter_by_opendate/")
def filter_movies_by_opendate(openyear: Union[int, None] = None, endyear: Union[int, None] = None, db: Session = Depends(get_db)):
    movies = crud.get_opendate(db, openyear, endyear)
    return movies

@app.get("/movies/filter_by_genre/")
def filter_movies_by_genre(genres: list[str] = Query(None, description="List of genres to filter by"), db: Session = Depends(get_db)):
    movies = crud.get_genre(db, genres)
    return movies

# @app.post("/delete_all_records/")
# def delete_records(db: Session = Depends(get_db)):
#     crud.delete_all_records(db)
#     return {"message": "All records deleted"}
