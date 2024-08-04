import streamlit as st
import pickle
import requests
import time
import logging

# Configure logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Simple cache to store poster URLs
poster_cache = {}

def fetch_poster(movie_id):
    if movie_id in poster_cache:
        return poster_cache[movie_id]

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
    retries = 3
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                poster_cache[movie_id] = full_path
                return full_path
            else:
                return "https://via.placeholder.com/500"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching poster (attempt {i+1}/{retries}): {e}")
            time.sleep(2 ** i)  # Exponential backoff
    return "https://via.placeholder.com/500"

# Load the movie list and similarity matrix
movies = pickle.load(open("movie_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
movies_list = movies['title'].values

st.header("Movie Recommendation System")

# Create a dropdown to select a movie
selected_movie = st.selectbox("Select a movie:", movies_list)

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    recommend_poster = []
    for i in distance[1:6]:
        movies_id = movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movies_id))
    return recommend_movie, recommend_poster

if st.button("Recommend"):
    movie_name, movie_poster = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(movie_name[0])
        st.image(movie_poster[0])
    with col2:
        st.text(movie_name[1])
        st.image(movie_poster[1])
    with col3:
        st.text(movie_name[2])
        st.image(movie_poster[2])
    with col4:
        st.text(movie_name[3])
        st.image(movie_poster[3])
    with col5:
        st.text(movie_name[4])
        st.image(movie_poster[4])
