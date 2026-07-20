import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from glob import glob
from category_encoders import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Buenos Aires Housing Price Predictor",
    page_icon="🏙️",
    layout="wide",
)

# ─── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e0e6ff;
    }
    .sub-header {
        color: #a0aac0;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #4361ee;
    }
    .prediction-box {
        background: linear-gradient(135deg, #4361ee, #7209b7);
        color: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)
 
# ─── Wrangle Function ───────────────────────────────────────────────────────────
def wrangle(filepath):
    df = pd.read_csv(filepath)
    mask_ba = df["place_with_parent_names"].str.contains("Capital Federal")
    mask_apt = df["property_type"] == "apartment"
    mask_price = df["price_aprox_usd"] < 400_000
    df = df[mask_ba & mask_apt & mask_price]
    low, high = df["surface_covered_in_m2"].quantile([0.1, 0.9])
    mask_area = df["surface_covered_in_m2"].between(low, high)
    df = df[mask_area]
    df[["lat", "lon"]] = df["lat-lon"].str.split(",", expand=True).astype(float)
    df.drop(columns="lat-lon", inplace=True)
    df["neighborhood"] = df["place_with_parent_names"].str.split("|", expand=True)[3]
    df.drop(columns="place_with_parent_names", inplace=True)
    df.drop(columns=["floor", "expenses"], inplace=True, errors="ignore")
    df.drop(columns=["operation", "property_type", "currency", "properati_url"], inplace=True, errors="ignore")
    df.drop(columns=["price", "price_aprox_local_currency", "price_per_m2", "price_usd_per_m2"], inplace=True, errors="ignore")
    df.drop(columns=["surface_total_in_m2", "rooms"], inplace=True, errors="ignore")
    return df

# ─── Load & Cache Data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    files = glob(r"C:\\Users\\OMEN\\OneDrive\\Desktop\\aptech\\buenos-aires-real-estate-*.csv")
    if not files:
        st.error("⚠️ No CSV data files found. Please add `buenos-aires-real-estate-*.csv` files.")
        st.stop()
    frames = [wrangle(f) for f in files]
    return pd.concat(frames, ignore_index=True)

@st.cache_resource
def train_model(df):
    target = "price_aprox_usd"
    features = ["surface_covered_in_m2", "lat", "lon", "neighborhood"]
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = make_pipeline(
        OneHotEncoder(use_cat_names=True),
        SimpleImputer(),
        Ridge()
    )
    model.fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    baseline_mae = mean_absolute_error(y_train, [y_train.mean()] * len(y_train))
    return model, train_mae, test_mae, baseline_mae, X_train, X_test, y_train, y_test

# ─── Load ───────────────────────────────────────────────────────────────────────
df = load_data()
model, train_mae, test_mae, baseline_mae, X_train, X_test, y_train, y_test = train_model(df)

neighborhoods = sorted(df["neighborhood"].dropna().unique().tolist())

# ─── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🏙️ Buenos Aires Housing Price Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Predict apartment prices in Capital Federal using size, location, and neighborhood features.</div>', unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔮 Predict Price", "📊 Model Performance", "🔍 Data Explorer"])

# ═══════════════════════════════════════════════════════════
# TAB 1 — PREDICT
# ═══════════════════════════════════════════════════════════
with tab1:
    st.subheader("Estimate Apartment Price")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### Property Details")
        neighborhood = st.selectbox("📍 Neighborhood", neighborhoods)
        area = st.slider("📐 Surface Area (m²)", min_value=20, max_value=200, value=65, step=5)

        # Default lat/lon per neighborhood (approx centres)
        neigh_coords = {
            n: df[df["neighborhood"] == n][["lat", "lon"]].median().values
            for n in neighborhoods
        }
        default_lat, default_lon = neigh_coords.get(neighborhood, [-34.60, -58.44])

        with st.expander("⚙️ Advanced: Adjust coordinates"):
            lat = st.number_input("Latitude", value=float(round(default_lat, 4)), format="%.4f", step=0.001)
            lon = st.number_input("Longitude", value=float(round(default_lon, 4)), format="%.4f", step=0.001)
        # Use default if user didn't open expander
        input_df = pd.DataFrame({
            "surface_covered_in_m2": [area],
            "lat": [lat],
            "lon": [lon],
            "neighborhood": [neighborhood],
        })
        predicted_price = model.predict(input_df)[0]

    with col2:
        st.markdown("#### Prediction")
        st.markdown(f"""
        <div class="prediction-box">
            <div style="font-size:1rem;opacity:0.85;margin-bottom:0.25rem;">Estimated Price</div>
            <div style="font-size:3rem;font-weight:800;">USD {predicted_price:,.0f}</div>
            <div style="font-size:0.9rem;opacity:0.75;margin-top:0.5rem;">
                {neighborhood} &nbsp;·&nbsp; {area} m²
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        price_per_m2 = predicted_price / area
        col_a, col_b = st.columns(2)
        col_a.metric("Price per m²", f"USD {price_per_m2:,.0f}")
        col_b.metric("Model Test MAE", f"USD {test_mae:,.0f}")

        # Price range sensitivity
        st.markdown("#### Price vs. Area (this neighborhood)")
        areas = np.arange(20, 201, 5)
        prices = model.predict(pd.DataFrame({
            "surface_covered_in_m2": areas,
            "lat": [lat] * len(areas),
            "lon": [lon] * len(areas),
            "neighborhood": [neighborhood] * len(areas),
        }))
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(areas, prices, color="#4361ee", linewidth=2)
        ax.axvline(area, color="#e63946", linestyle="--", alpha=0.7, label=f"Your area ({area}m²)")
        ax.set_xlabel("Area (m²)")
        ax.set_ylabel("Predicted Price (USD)")
        ax.legend(fontsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        fig.tight_layout()
        st.pyplot(fig)

# ═══════════════════════════════════════════════════════════
# TAB 2 — MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════
with tab2:
    st.subheader("Model Evaluation")

    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline MAE", f"USD {baseline_mae:,.0f}", help="Always predicting mean price")
    c2.metric("Train MAE", f"USD {train_mae:,.0f}", delta=f"-{baseline_mae - train_mae:,.0f} vs baseline")
    c3.metric("Test MAE", f"USD {test_mae:,.0f}", delta=f"-{baseline_mae - test_mae:,.0f} vs baseline")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Predicted vs. Actual (Test Set)")
        y_pred_test = model.predict(X_test)
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        ax2.scatter(y_test, y_pred_test, alpha=0.3, s=15, color="#4361ee")
        lim = max(y_test.max(), y_pred_test.max())
        ax2.plot([0, lim], [0, lim], "r--", linewidth=1.5, label="Perfect prediction")
        ax2.set_xlabel("Actual Price (USD)")
        ax2.set_ylabel("Predicted Price (USD)")
        ax2.legend(fontsize=8)
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
        fig2.tight_layout()
        st.pyplot(fig2)

    with col_right:
        st.markdown("#### Residuals Distribution")
        residuals = y_test.values - y_pred_test
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.hist(residuals, bins=40, color="#7209b7", edgecolor="white", alpha=0.85)
        ax3.axvline(0, color="red", linestyle="--")
        ax3.set_xlabel("Residual (Actual - Predicted)")
        ax3.set_ylabel("Count")
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
        fig3.tight_layout()
        st.pyplot(fig3)

    st.markdown("#### Average Predicted Price by Neighborhood")
    neigh_prices = []
    for n in neighborhoods:
        sample = df[df["neighborhood"] == n].head(30)
        if len(sample) > 0:
            pred = model.predict(sample[["surface_covered_in_m2", "lat", "lon", "neighborhood"]]).mean()
            neigh_prices.append({"Neighborhood": n, "Avg Predicted Price": pred})

    neigh_df = pd.DataFrame(neigh_prices).sort_values("Avg Predicted Price", ascending=True)
    fig4, ax4 = plt.subplots(figsize=(8, max(4, len(neigh_df) * 0.35)))
    bars = ax4.barh(neigh_df["Neighborhood"], neigh_df["Avg Predicted Price"], color="#4361ee")
    ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    ax4.set_xlabel("Average Predicted Price (USD)")
    fig4.tight_layout()
    st.pyplot(fig4)

# ═══════════════════════════════════════════════════════════
# TAB 3 — DATA EXPLORER
# ═══════════════════════════════════════════════════════════
with tab3:
    st.subheader("Dataset Overview")
    st.write(f"**{len(df):,} apartments** · **{df.shape[1]} features**")

    c1, c2, c3 = st.columns(3)
    c1.metric("Median Price", f"USD {df['price_aprox_usd'].median():,.0f}")
    c2.metric("Median Size", f"{df['surface_covered_in_m2'].median():.0f} m²")
    c3.metric("Neighborhoods", df["neighborhood"].nunique())

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### Price Distribution")
        fig5, ax5 = plt.subplots(figsize=(5, 3))
        ax5.hist(df["price_aprox_usd"], bins=50, color="#4361ee", edgecolor="white", alpha=0.85)
        ax5.set_xlabel("Price (USD)")
        ax5.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
        fig5.tight_layout()
        st.pyplot(fig5)

    with col_r:
        st.markdown("#### Correlation Heatmap")
        corr = df.select_dtypes("number").drop(columns=["price_aprox_usd"], errors="ignore").corr()
        fig6, ax6 = plt.subplots(figsize=(5, 3))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax6, linewidths=0.5)
        fig6.tight_layout()
        st.pyplot(fig6)

    st.markdown("#### Sample Data")
    st.dataframe(df.sample(min(100, len(df)), random_state=1).reset_index(drop=True), use_container_width=True)