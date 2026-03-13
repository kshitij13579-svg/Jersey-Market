"""
app.py — Jersey Marketplace Survey Analytics Dashboard
Consulting-grade Streamlit dashboard with North Star funnel,
Sankey diagrams, drill-down treemaps, and executive insights.
"""

import streamlit as st
import pandas as pd
from data_cleaning import load_and_clean
from visualizations import *

# ── Page Config ─────────────────────────────────────────────
st.set_page_config(page_title="Jersey Marketplace Analytics", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")

# ── Consulting-Grade CSS ────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg: #0A0F1A;
        --card: #111827;
        --elevated: #1A2332;
        --gold: #F59E0B;
        --gold-light: #FCD34D;
        --green: #10B981;
        --blue: #3B82F6;
        --red: #EF4444;
        --text-1: #F1F5F9;
        --text-2: #94A3B8;
        --text-3: #64748B;
        --border: #1E293B;
    }

    .block-container { padding-top: 1.2rem; max-width: 1280px; }
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important; }
    h1, h2, h3, h4 { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; letter-spacing: -0.02em; }

    /* KPI Cards */
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 1rem 0 1.5rem; }
    .kpi-card {
        background: linear-gradient(145deg, var(--card) 0%, var(--elevated) 100%);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: var(--gold); }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 800;
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1.1;
    }
    .kpi-value.gold { color: var(--gold); }
    .kpi-value.green { color: var(--green); }
    .kpi-value.blue { color: var(--blue); }
    .kpi-value.white { color: var(--text-1); }
    .kpi-label {
        font-size: 0.72rem;
        color: var(--text-3);
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }
    .kpi-sublabel {
        font-size: 0.68rem;
        color: var(--text-3);
        margin-top: 2px;
    }

    /* Insight Boxes */
    .insight {
        background: linear-gradient(90deg, #F59E0B0D 0%, transparent 100%);
        border-left: 3px solid var(--gold);
        padding: 0.9rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.8rem 0;
        font-size: 0.88rem;
        line-height: 1.7;
        color: var(--text-2);
    }
    .insight strong { color: var(--text-1); }
    .insight .tag {
        display: inline-block;
        background: var(--gold);
        color: var(--bg);
        font-size: 0.65rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 3px;
        margin-right: 6px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        vertical-align: middle;
    }
    .insight .tag.strategy { background: var(--blue); color: white; }
    .insight .tag.risk { background: var(--red); color: white; }

    /* Summary boxes */
    .summary-box {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }
    .summary-box h4 { color: var(--gold); margin-bottom: 0.6rem; font-size: 1rem; }
    .summary-box p { color: var(--text-2); font-size: 0.88rem; line-height: 1.65; margin: 0; }
    .summary-box ul { color: var(--text-2); font-size: 0.88rem; line-height: 1.8; padding-left: 1.2rem; margin: 0.3rem 0 0; }

    /* Divider */
    .divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, var(--border), transparent); margin: 1.5rem 0; }

    /* Tab styling */
    div[data-testid="stTabs"] button { font-weight: 600 !important; font-size: 0.85rem !important; letter-spacing: 0.01em; }
    div[data-testid="stTabs"] button[aria-selected="true"] { border-bottom-color: var(--gold) !important; color: var(--gold) !important; }
</style>
""", unsafe_allow_html=True)


# ── Data ────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_clean("data_raw.csv")

df, cleaning_log = get_data()
metrics = get_key_metrics(df)


# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏆 Controls")
    fan_filter = st.multiselect("Fan Type", df['Q7_Fan_Type'].unique().tolist(), default=df['Q7_Fan_Type'].unique().tolist())
    nat_filter = st.multiselect("Nationality", sorted(df['Q3_Nationality_Cluster'].unique().tolist()), default=sorted(df['Q3_Nationality_Cluster'].unique().tolist()))
    exclude_outliers = st.checkbox("Exclude flagged outliers", value=False)
    st.markdown("---")
    with st.expander("📋 Data Cleaning Log"):
        for step in cleaning_log:
            st.caption(step)
    st.markdown("---")
    st.caption("DAIDM · SP Jain GMBA · 2025")

df_f = df[(df['Q7_Fan_Type'].isin(fan_filter)) & (df['Q3_Nationality_Cluster'].isin(nat_filter))].copy()
if exclude_outliers:
    df_f = df_f[df_f['Outlier_Flag'] == 0]
m = get_key_metrics(df_f)


# ══════════════════════════════════════════════════════════════
# HEADER + KPIs
# ══════════════════════════════════════════════════════════════
st.markdown("# 🏆 Rare Jersey Marketplace")
st.markdown("##### Survey Analytics Dashboard — Demand Validation Study")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-value white">{m['total_responses']:,}</div><div class="kpi-label">Responses</div></div>
    <div class="kpi-card"><div class="kpi-value gold">{m['adoption_rate']}%</div><div class="kpi-label">Adoption Rate</div><div class="kpi-sublabel">Def. + Prob. Yes</div></div>
    <div class="kpi-card"><div class="kpi-value green">{m['high_intent_pct']}%</div><div class="kpi-label">High Intent</div><div class="kpi-sublabel">Definitely Yes</div></div>
    <div class="kpi-card"><div class="kpi-value gold">{m['high_value_segment_pct']}%</div><div class="kpi-label">High-Value Segments</div><div class="kpi-sublabel">Collectors + Investors</div></div>
    <div class="kpi-card"><div class="kpi-value blue">{m['own_jersey_pct']}%</div><div class="kpi-label">Own Jerseys</div></div>
    <div class="kpi-card"><div class="kpi-value green">{m['resell_interest_pct']}%</div><div class="kpi-label">Would Resell</div></div>
    <div class="kpi-card"><div class="kpi-value gold">{m['hv_adopter_pct']}%</div><div class="kpi-label">HV Adopters</div><div class="kpi-sublabel">Collectors/Investors who'd adopt</div></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 North Star", "📊 Demographics", "🏅 Fan Profile",
    "💰 Purchase Behavior", "🚀 Platform Validation", "🔬 Deep Analysis"
])


# ── TAB 0: NORTH STAR ──────────────────────────────────────
with tab0:
    st.markdown("### 🎯 North Star: Platform Adoption")
    st.markdown("""<div class="insight">
        <span class="tag">NORTH STAR</span>
        The core metric is <strong>Platform Adoption Rate</strong> — the percentage of respondents who would
        'Definitely' or 'Probably' use a dedicated rare jersey marketplace. Everything else feeds into this.
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_northstar_funnel(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The funnel shows progressive conversion: from total respondents, ~70% own jerseys, ~56% would adopt the
        platform, and ~30% have high intent. The 56% adoption rate validates market demand. The drop from
        'own jerseys' to 'would adopt' is the conversion gap the product must close.
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_northstar_sankey(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The Sankey reveals the full value chain: <strong>Hardcore Collectors and Investment Buyers</strong> flow
        overwhelmingly into 'Definitely Yes' and then into 'Would Resell' — confirming two-sided marketplace
        viability. Casual viewers mostly flow to 'Not Sure' or 'No' — they are awareness targets, not core users.
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="summary-box">
        <h4>Executive Summary</h4>
        <ul>
            <li><strong>56% adoption rate</strong> validates core demand for a rare jersey marketplace</li>
            <li><strong>Collectors & Investors (45% of base)</strong> are the acquisition priority — 80%+ would adopt</li>
            <li><strong>Two-sided marketplace confirmed</strong> — 75% of investors would resell on the platform</li>
            <li><strong>Authentication is the #1 feature</strong> — invest in verification infrastructure first</li>
            <li><strong>AI recommendations resonate with under-35s</strong> — build personalization early</li>
        </ul>
    </div>""", unsafe_allow_html=True)


# ── TAB 1: DEMOGRAPHICS ────────────────────────────────────
with tab1:
    st.markdown("### 📊 Who Is the Market?")

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(plot_age_distribution(df_f), use_container_width=True)
    with c2: st.plotly_chart(plot_gender_donut(df_f), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3: st.plotly_chart(plot_nationality_bars(df_f), use_container_width=True)
    with c4: st.plotly_chart(plot_income_cumulative(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The user base is <strong>young (60%+ under 35), predominantly male (68%), and UAE-centric</strong>
        (South Asian + Arab = 55%). Income peaks at $3K–$20K/mo. This profile suggests: mobile-first UX,
        mid-market pricing ($200–$1,500 sweet spot), and content in English with regional sport curation
        (Football primary, Cricket for South Asian segment).
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_demo_treemap(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag strategy">STRATEGY</span>
        The treemap enables drill-down segmentation. Click any nationality block to see age composition,
        then fan type breakdown. Use this to identify <strong>micro-segments</strong> — e.g., South Asian
        25–34 Hardcore Collectors may be the single highest-value acquisition target.
    </div>""", unsafe_allow_html=True)


# ── TAB 2: FAN PROFILE ─────────────────────────────────────
with tab2:
    st.markdown("### 🏅 What Do They Want?")

    st.plotly_chart(plot_fan_type_by_age(df_f), use_container_width=True)
    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        Fan type composition shifts dramatically with age. <strong>18–24</strong>: 45% casual.
        <strong>45–54</strong>: 65% collector/investor. Marketing for younger users should focus on
        discovery and social proof. For 35+ users, emphasize rarity, authentication, and investment returns.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(plot_sport_by_nationality(df_f), use_container_width=True)
    with c2: st.plotly_chart(plot_jersey_heatmap(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The heatmap reveals product-market fit per segment. <strong>Casuals want replicas (55%)</strong> — they aren't
        the core marketplace user. <strong>Collectors want Game-Worn (35%) and Signed (25%)</strong>.
        <strong>Investors want Game-Worn (40%) and Vintage (20%)</strong>. Curate inventory accordingly.
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_auth_rarity_box(df_f), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3: st.plotly_chart(plot_vintage_interest(df_f), use_container_width=True)
    with c4: st.plotly_chart(plot_condition_preference(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag strategy">STRATEGY</span>
        Build three product pillars: <strong>(1) Authentication engine</strong> — rated 4.3/5 by high-value segments.
        <strong>(2) Vintage collection</strong> — 55% of collectors 'very interested'. <strong>(3) Condition grading</strong>
        — Mint preference at 50–55% for Investors/Collectors justifies a standardized grading system.
    </div>""", unsafe_allow_html=True)


# ── TAB 3: PURCHASE BEHAVIOR ───────────────────────────────
with tab3:
    st.markdown("### 💰 Will They Pay?")

    st.plotly_chart(plot_spend_heatmap(df_f), use_container_width=True)
    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The spending-income matrix shows a clear <strong>diagonal pattern</strong> — spending tracks income.
        But note the <strong>top-left outliers</strong>: low-income users claiming $3K+ spend. These are either
        aspirational responses or signal a strong emotional connection to jerseys that overrides budget constraints.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(plot_spend_by_fan(df_f), use_container_width=True)
    with c2: st.plotly_chart(plot_frequency_by_fan(df_f), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3: st.plotly_chart(plot_discount_influence(df_f), use_container_width=True)
    with c4: st.plotly_chart(plot_recommendation_heatmap(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag strategy">STRATEGY</span>
        Implement <strong>segment-aware pricing</strong>: Discounts for Casuals/Passionate fans (acquisition tool),
        premium positioning for Collectors/Investors (value-based pricing). Never discount rare Game-Worn items —
        scarcity is the value driver. AI recommendations should be aggressive for under-35 users (40% receptive).
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_spend_income_scatter(df_f), use_container_width=True)
    st.plotly_chart(plot_purchase_sankey(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The purchase Sankey traces <strong>how income flows through spending to frequency</strong>. High earners
        ($35K+) concentrate in $1.5K–$3K+ spending at 5–10 purchases/year — these are the platform's
        <strong>revenue backbone</strong>. The $3K–$10K income segment primarily spends $50–$200 at 2–4 times/year
        — a volume play, not a value play.
    </div>""", unsafe_allow_html=True)


# ── TAB 4: PLATFORM VALIDATION ─────────────────────────────
with tab4:
    st.markdown("### 🚀 Will They Come?")

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(plot_adoption_waterfall(df_f), use_container_width=True)
    with c2: st.plotly_chart(plot_adoption_stacked(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The waterfall reveals <strong>which segments drive adoption volume</strong>. While Collectors and
        Investors have higher per-capita rates, Passionate Fans contribute significant absolute numbers.
        The stacked view confirms 80%+ positive intent among Collectors/Investors vs ~45% for Casuals.
    </div>""", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3: st.plotly_chart(plot_trust_factors(df_f), use_container_width=True)
    with c4: st.plotly_chart(plot_top_feature(df_f), use_container_width=True)

    c5, c6 = st.columns(2)
    with c5: st.plotly_chart(plot_resell_by_fan(df_f), use_container_width=True)
    with c6: st.plotly_chart(plot_loyalty_donut(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag strategy">STRATEGY</span>
        <strong>Launch priorities based on survey validation:</strong><br>
        ① Authentication verification system (ranked #1 feature, highest trust driver)<br>
        ② Seller ratings + reviews (second-highest trust factor)<br>
        ③ Loyalty program (80% interested — early retention lever)<br>
        ④ Resell capability from day one (75% of investors want it)
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="insight">
        <span class="tag risk">RISK</span>
        <strong>23% of respondents said 'Probably No' or 'Definitely No'.</strong> Key barriers likely include:
        trust in online jersey authenticity (solvable via verification), price concerns for casual fans
        (solvable via entry-level inventory), and competition from existing platforms like eBay.
        The 'Not Sure' segment (20%) is the <strong>swing vote</strong> — converting even half would push
        adoption above 65%.
    </div>""", unsafe_allow_html=True)


# ── TAB 5: DEEP ANALYSIS ───────────────────────────────────
with tab5:
    st.markdown("### 🔬 Correlation & Segment Analysis")

    st.plotly_chart(plot_adoption_drivers(df_f), use_container_width=True)
    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        <strong>Collector Score is the single strongest predictor</strong> of platform adoption, followed by
        Authentication Importance and Rarity Importance. Income and Age have weak/no correlation with adoption —
        meaning <strong>fan intensity matters more than demographics</strong>. Target by behavior, not demographics.
    </div>""", unsafe_allow_html=True)

    st.plotly_chart(plot_correlation_heatmap(df_f), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(plot_collector_violin(df_f), use_container_width=True)
    with c2: st.plotly_chart(plot_segment_radar(df_f), use_container_width=True)

    st.markdown("""<div class="insight">
        <span class="tag">INSIGHT</span>
        The violin plot confirms <strong>Collector Score cleanly separates segments</strong> — no overlap
        between Casual (1–3) and Hardcore (28–48). This validates the derived feature for ML classification.
        The radar chart shows each segment's 'fingerprint': Investors maximize spending, Collectors maximize
        frequency and rarity sensitivity.
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="summary-box">
        <h4>Final Verdict: Business Idea Validation</h4>
        <p>
            Based on 2,500 survey responses, the rare jersey marketplace concept shows <strong>strong demand
            validation</strong> with a 56% adoption rate, 80%+ intent among high-value segments, and
            confirmed two-sided marketplace potential (75% resell interest among investors).
        </p>
        <ul>
            <li>✅ <strong>Demand exists</strong> — 56% would use the platform</li>
            <li>✅ <strong>Willingness to pay</strong> — 48% of investors would spend $1,500+</li>
            <li>✅ <strong>Two-sided marketplace</strong> — sellers AND buyers confirmed</li>
            <li>✅ <strong>Clear segmentation</strong> — 3 distinct user personas with different needs</li>
            <li>✅ <strong>Feature validation</strong> — authentication ranked #1 unanimously</li>
            <li>⚠️ <strong>Risk: casual segment</strong> — low conversion, needs entry-level inventory</li>
            <li>⚠️ <strong>Risk: trust</strong> — authentication system is table stakes, not a differentiator</li>
        </ul>
        <p style="margin-top: 0.8rem; color: #F59E0B; font-weight: 600;">
            Recommendation: PROCEED with MVP — focus on Collector/Investor segment, authentication-first
            product, Football jerseys as launch vertical, UAE as beachhead market.
        </p>
    </div>""", unsafe_allow_html=True)

    # Downloads
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📥 Export Data")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 Cleaned Dataset (CSV)", df.to_csv(index=False).encode('utf-8'), "jersey_survey_cleaned.csv", "text/csv")
    with c2:
        st.download_button("📄 Filtered Dataset (CSV)", df_f.to_csv(index=False).encode('utf-8'), "jersey_survey_filtered.csv", "text/csv")
