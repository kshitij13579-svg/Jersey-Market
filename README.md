# 🏆 Rare Jersey Marketplace — Survey Analytics Dashboard

A Streamlit-based analytics dashboard that validates demand for a digital marketplace app where collectors and fans can buy and sell rare, game-worn, and collectible sports jerseys.

Built as part of the **DAIDM (Data Analytics for Informed Decision Making)** course at **SP Jain School of Global Management, GMBA Programme**.

---

## 📋 Project Overview

This project uses survey data (2,500 responses) to validate whether a dedicated marketplace for rare sports jerseys has viable demand. The analysis covers:

- **Demographics** — Who are the potential users?
- **Fan Profiling** — What type of collectors exist and what do they want?
- **Purchase Behavior** — How much will they spend? How often?
- **Platform Validation** — Would they actually use this app?
- **Correlation Analysis** — What drives purchase decisions?

---

## 🗂️ Project Structure

```
jersey-marketplace-analytics/
├── app.py                  # Main Streamlit dashboard
├── data_cleaning.py        # Data cleaning & transformation module
├── visualizations.py       # All chart/graph generation functions
├── data_raw.csv            # Raw synthetic survey data (2,515 rows)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🚀 Quick Start

### Local Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/jersey-marketplace-analytics.git
cd jersey-marketplace-analytics

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

### Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub account.
4. Select this repository, branch `main`, and file `app.py`.
5. Click **Deploy**.

---

## 📊 Dashboard Features

### Interactive Filters
- Filter by **Fan Type** (Casual, Passionate, Hardcore Collector, Investor)
- Filter by **Nationality Cluster** (South Asian, Arab, Western Expat, East Asian, African)
- Toggle **outlier exclusion** for cleaner analysis

### Five Analysis Tabs

| Tab | Contents |
|-----|----------|
| 📊 Demographics | Age, gender, nationality, income distributions |
| 🏅 Fan Profile | Fan types by age, sport preferences, jersey type interest, authentication & rarity importance |
| 💰 Purchase Behavior | Spending by income/fan type, purchase frequency, discount sensitivity, AI recommendation receptivity |
| 🚀 Platform Validation | Adoption rates, trust factors, reselling interest, loyalty program appeal, feature rankings |
| 🔬 Correlations | Heatmap, collector score distributions, income vs spending scatter |

### Data Downloads
- Download cleaned dataset (CSV)
- Download filtered dataset (CSV)

---

## 🔧 Data Pipeline

### Raw Data (data_raw.csv)
- 2,515 rows (2,500 base responses + 15 simulated duplicate submissions)
- 26 columns mapping to 25 survey questions
- Includes injected noise: missing values (~2–3%), typos, inconsistent casing, outliers

### Cleaning Steps (data_cleaning.py)
1. **Duplicate removal** — Identifies and removes 15 duplicate rows
2. **Text standardization** — Fixes gender typos (M, male, MALE → Male), nationality inconsistencies
3. **Missing value imputation** — Mode-based, context-aware (income imputed within nationality cluster)
4. **Numeric encoding** — Converts ordinal categories to midpoint values
5. **Derived features** — Collector_Score, Value_Sensitivity, Auth_Rarity_Index
6. **Binary target** — Platform_Adoption (Definitely/Probably yes = 1)
7. **Outlier flagging** — Identifies inconsistent responses without removing them
8. **Multi-select parsing** — Splits Q22 trust factors into 5 binary columns
9. **Ranking extraction** — Extracts top-ranked feature from Q25

---

## 📈 Key Findings

- **56% adoption rate** — Majority of respondents would use the platform
- **75%+ adoption among collectors/investors** — Core target segment shows strong intent
- **Authentication is #1** — Verification ranked as most important feature across all segments
- **Two-sided marketplace viable** — 75% of investors would resell on the platform
- **AI recommendations resonate** — 40% of under-35 users want personalized recommendations
- **Pricing should segment** — Investors are price-insensitive; casuals respond to discounts

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** — Dashboard framework
- **Plotly** — Interactive charts
- **Pandas / NumPy** — Data processing
- **Seaborn / Matplotlib** — Statistical visualization support

---

## 👥 Team

SP Jain School of Global Management — GMBA Programme 
Kshitij Singh — January 2025 Cohort

---

## 📄 License

This project is for academic purposes. Data is synthetically generated.
