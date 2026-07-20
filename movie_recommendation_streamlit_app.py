import streamlit as st
import pickle as pk
import requests
import math

st.set_page_config(layout="wide", page_title="Movie App")

st.title("🎬 Movie Recommendation App")

API_KEY = "5efac580ff7d81b02c9c18af440508e6"

# -------------------------------
# LOAD DATA
# -------------------------------
movies = pk.load(open("movies_list.pkl", "rb"))
similarity = pk.load(open("similarity_cos.pkl", "rb"))

# -------------------------------
# SESSION STATE
# -------------------------------
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 10

if "selected_movie_id" not in st.session_state:
    st.session_state.selected_movie_id = None

if "selected_movie_title" not in st.session_state:
    st.session_state.selected_movie_title = None


# -------------------------------
# TMDB HELPERS
# -------------------------------
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        return response.json()
    return None


def fetch_poster(movie_id):
    data = fetch_movie_details(movie_id)
    if data and data.get("poster_path"):
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    return "https://via.placeholder.com/500x750?text=No+Image"


def fetch_backdrop(movie_id):
    data = fetch_movie_details(movie_id)
    if data and data.get("backdrop_path"):
        return f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}"
    return None


def fetch_overview(movie_id):
    data = fetch_movie_details(movie_id)
    if data:
        return data.get("overview", "No description available.")
    return "No description available."


def fetch_release_date(movie_id):
    data = fetch_movie_details(movie_id)
    if data:
        return data.get("release_date", "Unknown")
    return "Unknown"


def fetch_rating(movie_id):
    data = fetch_movie_details(movie_id)
    if data:
        return data.get("vote_average", "N/A")
    return "N/A"


def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
    response = requests.get(url, timeout=10)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        # Prefer YouTube trailer
        for video in results:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return f"https://www.youtube.com/watch?v={video['key']}"

        # fallback: first YouTube video
        for video in results:
            if video.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={video['key']}"

    return None


# -------------------------------
# RECOMMENDER
# -------------------------------
def recommend_by_title(movie_title):
    index = movies[movies["title"] == movie_title].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []

    for i in distances[1:6]:
        movie_row = movies.iloc[i[0]]
        recommended_movies.append({
            "title": movie_row["title"],
            "id": movie_row["id"]
        })

    return recommended_movies


# -------------------------------
# SELECT MOVIE HANDLER
# -------------------------------
def select_movie(movie_id, movie_title):
    st.session_state.selected_movie_id = movie_id
    st.session_state.selected_movie_title = movie_title


def go_home():
    st.session_state.selected_movie_id = None
    st.session_state.selected_movie_title = None


# -------------------------------
# HOME PAGE
# -------------------------------
def show_home():
    st.subheader("Browse Movies")

    visible_movies = movies.iloc[:st.session_state.visible_count]

    num_cols = 5
    rows = math.ceil(len(visible_movies) / num_cols)

    for row in range(rows):
        cols = st.columns(num_cols)
        for col_idx in range(num_cols):
            movie_idx = row * num_cols + col_idx
            if movie_idx < len(visible_movies):
                movie = visible_movies.iloc[movie_idx]
                movie_title = movie["title"]
                movie_id = movie["id"]
                poster_url = fetch_poster(movie_id)

                with cols[col_idx]:
                    st.image(poster_url, use_container_width=True)
                    st.markdown(f"**{movie_title}**")

                    if st.button("View", key=f"view_{movie_id}"):
                        select_movie(movie_id, movie_title)
                        st.rerun()

    if st.session_state.visible_count < len(movies):
        if st.button("Load More"):
            st.session_state.visible_count += 10
            st.rerun()


# -------------------------------
# MOVIE DETAIL PAGE
# -------------------------------
def show_movie_detail(movie_id, movie_title):
    if st.button("⬅ Back to Home"):
        go_home()
        st.rerun()

    backdrop = fetch_backdrop(movie_id)
    poster = fetch_poster(movie_id)
    overview = fetch_overview(movie_id)
    release_date = fetch_release_date(movie_id)
    rating = fetch_rating(movie_id)
    trailer_url = fetch_trailer(movie_id)

    st.markdown(f"## {movie_title}")

    if backdrop:
        st.image(backdrop, use_container_width=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(poster, use_container_width=True)

    with col2:
        st.markdown(f"**Release Date:** {release_date}")
        st.markdown(f"**Rating:** ⭐ {rating}")
        st.markdown("**Overview:**")
        st.write(overview)

    st.markdown("### ▶ Now Playing")

    if trailer_url:
        st.video(trailer_url)
    else:
        st.info("Trailer not available. Showing poster instead.")
        st.image(poster, width=300)

    st.markdown("### Recommended For You")

    recommended = recommend_by_title(movie_title)
    cols = st.columns(5)

    for idx, rec in enumerate(recommended):
        with cols[idx]:
            rec_poster = fetch_poster(rec["id"])
            st.image(rec_poster, use_container_width=True)
            st.markdown(f"**{rec['title']}**")
            if st.button("Watch", key=f"rec_{rec['id']}"):
                select_movie(rec["id"], rec["title"])
                st.rerun()


# -------------------------------
# APP ROUTER
# -------------------------------
if st.session_state.selected_movie_id is None:
    show_home()
else:
    show_movie_detail(
        st.session_state.selected_movie_id,
        st.session_state.selected_movie_title
    )