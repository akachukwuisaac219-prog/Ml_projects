import streamlit as st
import pickle as pk
import requests

st.title("Movie Recommendation System")

# Put your TMDB API key here for now
# Better later: use st.secrets["TMDB_API_KEY"]
API_KEY = "5efac580ff7d81b02c9c18af440508e6"

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return "https://via.placeholder.com/500x750?text=No+Image"

    data = response.json()
    poster_path = data.get("poster_path")

    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

movies = pk.load(open("movies_list.pkl", "rb"))
similarity = pk.load(open("similarity_cos.pkl", "rb"))

movies_list = movies["title"].values
select_movie = st.selectbox("Select Movie", movies_list)

def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []
    recommended_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id   # your dataframe must contain TMDB movie IDs
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

if st.button("Show Recommendation"):
    recommended_movies, recommended_posters = recommend(select_movie)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(recommended_movies[0])
        st.image(recommended_posters[0])

    with col2:
        st.text(recommended_movies[1])
        st.image(recommended_posters[1])

    with col3:
        st.text(recommended_movies[2])
        st.image(recommended_posters[2])

    with col4:
        st.text(recommended_movies[3])
        st.image(recommended_posters[3])

    with col5:
        st.text(recommended_movies[4])
        st.image(recommended_posters[4])