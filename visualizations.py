"""
visualizations.py
Consulting-grade chart library for Jersey Marketplace Survey Analytics.
Design system: Dark navy base, gold/amber accents, high-contrast consulting palette.
All charts use Plotly for interactivity and drill-down capability.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ══════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Consulting Color Grading
# ══════════════════════════════════════════════════════════════

C = {
    'bg_primary':    '#0A0F1A',
    'bg_card':       '#111827',
    'bg_elevated':   '#1A2332',
    'text_primary':  '#F1F5F9',
    'text_secondary':'#94A3B8',
    'text_muted':    '#64748B',
    'gold':          '#F59E0B',
    'gold_light':    '#FCD34D',
    'gold_dark':     '#D97706',
    'green':         '#10B981',
    'green_light':   '#34D399',
    'red':           '#EF4444',
    'red_light':     '#F87171',
    'blue':          '#3B82F6',
    'blue_light':    '#60A5FA',
    'blue_muted':    '#1E40AF',
    'cat5':          '#8B5CF6',
    'grid':          '#1E293B',
    'divider':       '#334155',
}

CAT_COLORS = [C['gold'], C['blue'], C['green'], C['red'], C['cat5'], '#EC4899', '#14B8A6', '#F97316']

CONSULTING_SEQ = [[0.0, '#0C1929'], [0.2, '#1E3A5F'], [0.4, '#2563EB'], [0.6, '#F59E0B'], [0.8, '#FBBF24'], [1.0, '#FDE68A']]
DIVERGING_SCALE = [[0.0, '#1E40AF'], [0.25, '#3B82F6'], [0.5, '#F1F5F9'], [0.75, '#F59E0B'], [1.0, '#D97706']]


def _layout(fig, title="", subtitle="", height=480, showlegend=True):
    full_title = f"{title}<br><span style='font-size:12px;color:{C['text_muted']}'>{subtitle}</span>" if subtitle else title
    fig.update_layout(
        title=dict(text=full_title, font=dict(family="Söhne, Helvetica Neue, Arial", size=17, color=C['text_primary']), x=0.01, xanchor='left'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor=C['bg_card'],
        font=dict(family="Söhne, Helvetica Neue, Arial", color=C['text_secondary'], size=12),
        height=height, margin=dict(l=55, r=25, t=75, b=50), showlegend=showlegend,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=C['text_secondary'], size=11), bordercolor='rgba(0,0,0,0)'),
    )
    fig.update_xaxes(gridcolor=C['grid'], zerolinecolor=C['grid'], tickfont=dict(color=C['text_muted'], size=10), title_font=dict(color=C['text_secondary'], size=11))
    fig.update_yaxes(gridcolor=C['grid'], zerolinecolor=C['grid'], tickfont=dict(color=C['text_muted'], size=10), title_font=dict(color=C['text_secondary'], size=11))
    return fig


# ══════════════════════════════════════════════════════════════
# NORTH STAR
# ══════════════════════════════════════════════════════════════

def plot_northstar_funnel(df):
    total = len(df)
    own = (df['Q8_Own_Jerseys'] == 'Yes').sum()
    open_p = df['Q21_Would_Use_Platform'].isin(['Definitely yes', 'Probably yes', 'Not sure']).sum()
    adopt = df['Q21_Would_Use_Platform'].isin(['Definitely yes', 'Probably yes']).sum()
    high = (df['Q21_Would_Use_Platform'] == 'Definitely yes').sum()
    stages = ['Total Respondents', 'Own Sports Jerseys', 'Open to Platform', 'Would Adopt', 'High Intent']
    values = [total, own, open_p, adopt, high]
    fig = go.Figure(go.Funnel(
        y=stages, x=values, textinfo="value+percent initial",
        textposition="inside", textfont=dict(color=C['text_primary'], size=14),
        marker=dict(color=[C['blue'], C['blue_light'], C['gold'], C['gold_light'], C['green']], line=dict(color=C['bg_primary'], width=2)),
        connector=dict(line=dict(color=C['divider'], width=1)),
    ))
    return _layout(fig, "North Star Funnel", "Conversion: respondent → jersey owner → open → adopter → high intent", height=420, showlegend=False)


def plot_northstar_sankey(df):
    fan_types = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    adoption_levels = ['Definitely yes', 'Probably yes', 'Not sure', 'Probably no', 'Definitely no']
    resell_levels = ['Yes', 'Maybe', 'No']
    labels = fan_types + adoption_levels + resell_levels
    idx = {l: i for i, l in enumerate(labels)}
    src, tgt, val, lc = [], [], [], []
    ac = {'Definitely yes': C['green'], 'Probably yes': C['green_light'], 'Not sure': C['blue'], 'Probably no': C['red_light'], 'Definitely no': C['red']}
    def _rgba(hex_c, a=0.33):
        h = hex_c.lstrip('#')
        return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'
    for ft in fan_types:
        s = df[df['Q7_Fan_Type'] == ft]
        for al in adoption_levels:
            c = (s['Q21_Would_Use_Platform'] == al).sum()
            if c > 0: src.append(idx[ft]); tgt.append(idx[al]); val.append(c); lc.append(_rgba(ac[al]))
    rc = {'Yes': _rgba(C['green']), 'Maybe': _rgba(C['gold']), 'No': _rgba(C['red'])}
    for al in adoption_levels:
        s = df[df['Q21_Would_Use_Platform'] == al]
        for rl in resell_levels:
            c = (s['Q23_Would_Resell'] == rl).sum()
            if c > 0: src.append(idx[al]); tgt.append(idx[rl]); val.append(c); lc.append(rc[rl])
    nc = [C['gold'], C['blue'], C['gold_light'], C['green']] + [C['green'], C['green_light'], C['blue'], C['red_light'], C['red']] + [C['green'], C['gold'], C['red']]
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(pad=20, thickness=22, line=dict(color=C['bg_primary'], width=1), label=labels, color=nc),
        link=dict(source=src, target=tgt, value=val, color=lc),
    ))
    return _layout(fig, "Value Flow: Fan Type → Adoption → Resell Intent", "Full path from segment to platform engagement to two-sided marketplace", height=520, showlegend=False)


# ══════════════════════════════════════════════════════════════
# SECTION 1: DEMOGRAPHICS
# ══════════════════════════════════════════════════════════════

def plot_age_distribution(df):
    order = ['18-24', '25-34', '35-44', '45-54', '55-65']
    counts = df['Q1_Age_Group'].value_counts().reindex(order).fillna(0)
    pcts = (counts / counts.sum() * 100).round(1)
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values, marker=dict(color=C['gold'], cornerradius=4),
        text=[f"{v:,.0f}<br><span style='font-size:10px;color:{C['text_muted']}'>{p}%</span>" for v, p in zip(counts.values, pcts)],
        textposition='outside', textfont=dict(color=C['text_primary'], size=12),
    ))
    return _layout(fig, "Age Distribution", "60%+ under 35 — digital-native audience", showlegend=False)


def plot_gender_donut(df):
    counts = df['Q2_Gender'].value_counts()
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=[C['blue'], C['gold'], C['text_muted']][:len(counts)], line=dict(color=C['bg_primary'], width=2)),
        textinfo='label+percent', textfont=dict(size=12, color=C['text_primary']),
    ))
    fig.add_annotation(text=f"<b>{len(df):,}</b><br><span style='font-size:11px'>total</span>", x=0.5, y=0.5, showarrow=False,
                       font=dict(size=20, color=C['text_primary']))
    return _layout(fig, "Gender Split", "68% male — consistent with sports memorabilia market", height=380)


def plot_nationality_bars(df):
    counts = df['Q3_Nationality_Cluster'].value_counts().sort_values()
    colors = [C['gold'] if v == counts.max() else C['blue_muted'] for v in counts.values]
    fig = go.Figure(go.Bar(
        y=counts.index, x=counts.values, orientation='h', marker=dict(color=colors, cornerradius=4),
        text=[f"{v:,}" for v in counts.values], textposition='outside', textfont=dict(color=C['text_primary']),
    ))
    return _layout(fig, "Nationality Clusters", "South Asian + Arab = 55% — UAE market core", showlegend=False)


def plot_income_cumulative(df):
    order = ['Below 3,000', '3,000-10,000', '10,001-20,000', '20,001-35,000', '35,001-50,000', 'Above 50,000']
    counts = df['Q4_Monthly_Income'].value_counts().reindex(order).fillna(0)
    cumul = (counts.cumsum() / counts.sum() * 100).round(1)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=counts.index, y=counts.values, name="Count", marker=dict(color=C['blue'], cornerradius=4),
                         text=counts.values.astype(int), textposition='outside', textfont=dict(color=C['text_primary'], size=11)), secondary_y=False)
    fig.add_trace(go.Scatter(x=counts.index, y=cumul.values, name="Cumulative %", mode='lines+markers+text',
                             line=dict(color=C['gold'], width=2.5), marker=dict(size=7, color=C['gold']),
                             text=[f"{v}%" for v in cumul.values], textposition='top center', textfont=dict(color=C['gold'], size=10)), secondary_y=True)
    fig.update_yaxes(title_text="Count", secondary_y=False, gridcolor=C['grid'])
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True, gridcolor='rgba(0,0,0,0)', range=[0, 110])
    fig.update_xaxes(tickangle=25)
    return _layout(fig, "Income Distribution + Cumulative", "68% earn under $20K — mid-market pricing critical")


def plot_demo_treemap(df):
    grouped = df.groupby(['Q3_Nationality_Cluster', 'Q1_Age_Group', 'Q7_Fan_Type']).size().reset_index(name='count')
    fig = px.treemap(grouped, path=['Q3_Nationality_Cluster', 'Q1_Age_Group', 'Q7_Fan_Type'], values='count', color='count',
                     color_continuous_scale=[[0, C['bg_elevated']], [0.5, C['blue']], [1, C['gold']]])
    fig.update_traces(textfont=dict(color=C['text_primary'], size=12))
    return _layout(fig, "Demographic Drill-Down Treemap", "Click to drill: Nationality → Age → Fan Type", height=550, showlegend=False)


# ══════════════════════════════════════════════════════════════
# SECTION 2: FAN PROFILE
# ══════════════════════════════════════════════════════════════

def plot_fan_type_by_age(df):
    order = ['18-24', '25-34', '35-44', '45-54', '55-65']
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    fc = [C['text_muted'], C['blue'], C['gold'], C['green']]
    ct = pd.crosstab(df['Q1_Age_Group'], df['Q7_Fan_Type'], normalize='index').reindex(order).reindex(columns=fo).fillna(0) * 100
    fig = go.Figure()
    for i, f in enumerate(fo):
        fig.add_trace(go.Bar(name=f, x=ct.index, y=ct[f], marker=dict(color=fc[i], cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title_text="% of Age Group", ticksuffix="%")
    return _layout(fig, "Fan Type Composition by Age", "Collector + Investor share rises from ~20% (18-24) to ~65% (45-54)")


def plot_sport_by_nationality(df):
    ct = pd.crosstab(df['Q3_Nationality_Cluster'], df['Q5_Favorite_Sport'], normalize='index') * 100
    sc = {'Football': C['gold'], 'Basketball': C['blue'], 'Cricket': C['green'], 'Baseball': C['red'], 'Other': C['text_muted']}
    fig = go.Figure()
    for sport in ct.columns:
        fig.add_trace(go.Bar(name=sport, y=ct.index, x=ct[sport], orientation='h', marker=dict(color=sc.get(sport, C['cat5']), cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_xaxes(title_text="% of Nationality", ticksuffix="%")
    return _layout(fig, "Sport Preference by Nationality", "Football dominates globally — Cricket is the South Asian differentiator")


def plot_jersey_heatmap(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    jo = ['Regular replica', 'Limited Edition', 'Signed by player', 'Vintage', 'Game-Worn']
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q10_Jersey_Type_Interest'], normalize='index').reindex(index=fo, columns=jo).fillna(0) * 100
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=ct.columns.tolist(), y=ct.index.tolist(), colorscale=CONSULTING_SEQ,
        text=np.round(ct.values, 1), texttemplate="%{text}%", textfont=dict(color=C['text_primary'], size=12),
        colorbar=dict(title="%", tickfont=dict(color=C['text_muted'])),
    ))
    return _layout(fig, "Jersey Type Interest Matrix", "Game-Worn leads for Collectors (35%) & Investors (40%)", height=400, showlegend=False)


def plot_auth_rarity_box(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    fc = [C['text_muted'], C['blue'], C['gold'], C['green']]
    fig = make_subplots(rows=1, cols=2, subplot_titles=[
        f"<span style='color:{C['text_secondary']}'>Authentication Importance (1–5)</span>",
        f"<span style='color:{C['text_secondary']}'>Rarity Importance (1–5)</span>"
    ], horizontal_spacing=0.08)
    for i, f in enumerate(fo):
        s = df[df['Q7_Fan_Type'] == f]
        fig.add_trace(go.Box(y=s['Q11_Authentication_Importance'], name=f, marker_color=fc[i], boxmean=True, legendgroup=f), row=1, col=1)
        fig.add_trace(go.Box(y=s['Q14_Rarity_Importance'], name=f, marker_color=fc[i], boxmean=True, showlegend=False, legendgroup=f), row=1, col=2)
    return _layout(fig, "Authentication & Rarity Importance by Segment", "Collectors & Investors cluster at 4–5 — validates authentication as core feature", height=450)


def plot_vintage_interest(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    vo = ['Yes, very interested', 'Somewhat interested', 'Not interested']
    vc = [C['green'], C['gold'], C['red_light']]
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q15_Vintage_Interest'], normalize='index').reindex(index=fo, columns=vo).fillna(0) * 100
    fig = go.Figure()
    for i, v in enumerate(vo):
        fig.add_trace(go.Bar(name=v, x=ct.index, y=ct[v], marker=dict(color=vc[i], cornerradius=2)))
    fig.update_layout(barmode='group')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Vintage Jersey Interest", "55% of Collectors are 'very interested' — vintage section warranted")


def plot_condition_preference(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q12_Preferred_Condition'], normalize='index').reindex(index=fo).fillna(0) * 100
    cc = {'Mint (perfect)': C['green'], 'Good (minor wear)': C['blue'], 'Used (visible wear, but authentic)': C['gold'], "Condition doesn't matter if rare": C['cat5']}
    fig = go.Figure()
    for cond in ct.columns:
        fig.add_trace(go.Bar(name=cond, x=ct.index, y=ct[cond], marker=dict(color=cc.get(cond, C['text_muted']), cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Preferred Condition by Segment", "Mint dominates for Investors (55%) — condition grading adds value")


# ══════════════════════════════════════════════════════════════
# SECTION 3: PURCHASING BEHAVIOR
# ══════════════════════════════════════════════════════════════

def plot_spend_heatmap(df):
    so = ['Under 50', '50-200', '201-500', '501-1,500', '1,501-3,000', '3,000+']
    io = ['Below 3,000', '3,000-10,000', '10,001-20,000', '20,001-35,000', '35,001-50,000', 'Above 50,000']
    ct = pd.crosstab(df['Q4_Monthly_Income'], df['Q16_Willingness_to_Spend'], normalize='index').reindex(index=io, columns=so).fillna(0) * 100
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=ct.columns.tolist(), y=ct.index.tolist(), colorscale=CONSULTING_SEQ,
        text=np.round(ct.values, 0), texttemplate="%{text}%", textfont=dict(color=C['text_primary'], size=11),
        colorbar=dict(title="%", tickfont=dict(color=C['text_muted'])),
    ))
    return _layout(fig, "Spending × Income Matrix", "Diagonal pattern = spending tracks income; top-left outliers = aspirational buyers", height=460, showlegend=False)


def plot_spend_by_fan(df):
    so = ['Under 50', '50-200', '201-500', '501-1,500', '1,501-3,000', '3,000+']
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q16_Willingness_to_Spend'], normalize='index').reindex(index=fo, columns=so).fillna(0) * 100
    sc = [C['bg_elevated'], C['blue_muted'], C['blue'], C['gold_dark'], C['gold'], C['gold_light']]
    fig = go.Figure()
    for i, s in enumerate(so):
        fig.add_trace(go.Bar(name=s, x=ct.index, y=ct[s], marker=dict(color=sc[i], cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Spending Willingness by Fan Type", "48% of Investment Buyers willing to spend $1,500+")


def plot_frequency_by_fan(df):
    fro = ['Once a year or less', '2-4 times a year', '5-10 times a year', 'More than 10 times a year']
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q17_Purchase_Frequency'], normalize='index').reindex(index=fo, columns=fro).fillna(0) * 100
    fc = [C['bg_elevated'], C['blue_muted'], C['gold_dark'], C['gold']]
    fig = go.Figure()
    for i, f in enumerate(fro):
        fig.add_trace(go.Bar(name=f, x=ct.index, y=ct[f], marker=dict(color=fc[i], cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Purchase Frequency by Fan Type", "70% of Hardcore Collectors buy 5+ times/year — high LTV")


def plot_discount_influence(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    do = ['Strongly influences', 'Somewhat influences', 'No impact']
    dc = [C['gold'], C['blue'], C['text_muted']]
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q18_Discount_Influence'], normalize='index').reindex(index=fo, columns=do).fillna(0) * 100
    fig = go.Figure()
    for i, d in enumerate(do):
        fig.add_trace(go.Bar(name=d, x=ct.index, y=ct[d], marker=dict(color=dc[i], cornerradius=3)))
    fig.update_layout(barmode='group')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Discount Sensitivity", "55% of Casuals strongly influenced vs 55% of Investors unaffected")


def plot_recommendation_heatmap(df):
    ao = ['18-24', '25-34', '35-44', '45-54', '55-65']
    ro = ['Yes, definitely', 'Maybe', 'No, I prefer browsing on my own']
    ct = pd.crosstab(df['Q1_Age_Group'], df['Q19_Recommendation_Influence'], normalize='index').reindex(index=ao, columns=ro).fillna(0) * 100
    fig = go.Figure(go.Heatmap(
        z=ct.values, x=['Yes, definitely', 'Maybe', 'No, self-browse'], y=ct.index.tolist(),
        colorscale=CONSULTING_SEQ, text=np.round(ct.values, 1), texttemplate="%{text}%",
        textfont=dict(color=C['text_primary'], size=12), colorbar=dict(title="%", tickfont=dict(color=C['text_muted'])),
    ))
    return _layout(fig, "AI Recommendation Receptivity × Age", "40% of under-35 'definitely' want recs — validates AI engine", height=380, showlegend=False)


def plot_spend_income_scatter(df):
    dff = df.dropna(subset=['Income_Numeric', 'Spend_Numeric']).copy()
    dff['Inc_J'] = dff['Income_Numeric'] + np.random.normal(0, 600, len(dff))
    dff['Sp_J'] = dff['Spend_Numeric'] + np.random.normal(0, 40, len(dff))
    fc = {'Casual viewer': C['text_muted'], 'Passionate fan': C['blue'], 'Hardcore collector': C['gold'], 'Investment buyer': C['green']}
    fig = px.scatter(dff, x='Inc_J', y='Sp_J', color='Q7_Fan_Type', color_discrete_map=fc, opacity=0.45,
                     labels={'Inc_J': 'Monthly Income (USD)', 'Sp_J': 'Spending per Jersey (USD)', 'Q7_Fan_Type': 'Fan Type'})
    fig.update_traces(marker=dict(size=5))
    return _layout(fig, "Income vs Spending (by Segment)", "Investors (green) cluster top-right; Casuals bottom-left", height=500)


def plot_purchase_sankey(df):
    il = ['Inc: <3K', 'Inc: 3-10K', 'Inc: 10-20K', 'Inc: 20-35K', 'Inc: 35-50K', 'Inc: 50K+']
    sl = ['Spend: <50', 'Spend: 50-200', 'Spend: 201-500', 'Spend: 501-1.5K', 'Spend: 1.5-3K', 'Spend: 3K+']
    fl = ['Freq: ≤1/yr', 'Freq: 2-4/yr', 'Freq: 5-10/yr', 'Freq: 10+/yr']
    io = ['Below 3,000', '3,000-10,000', '10,001-20,000', '20,001-35,000', '35,001-50,000', 'Above 50,000']
    so = ['Under 50', '50-200', '201-500', '501-1,500', '1,501-3,000', '3,000+']
    fro = ['Once a year or less', '2-4 times a year', '5-10 times a year', 'More than 10 times a year']
    labels = il + sl + fl
    idx = {l: i for i, l in enumerate(labels)}
    def _rgba(hex_c, a=0.19):
        h = hex_c.lstrip('#')
        return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'
    src, tgt, val, lc = [], [], [], []
    for ii, inc in enumerate(io):
        s = df[df['Q4_Monthly_Income'] == inc]
        for si, sp in enumerate(so):
            c = (s['Q16_Willingness_to_Spend'] == sp).sum()
            if c > 2: src.append(idx[il[ii]]); tgt.append(idx[sl[si]]); val.append(c); lc.append(_rgba(C['blue']))
    for si, sp in enumerate(so):
        s = df[df['Q16_Willingness_to_Spend'] == sp]
        for fi, fq in enumerate(fro):
            c = (s['Q17_Purchase_Frequency'] == fq).sum()
            if c > 2: src.append(idx[sl[si]]); tgt.append(idx[fl[fi]]); val.append(c); lc.append(_rgba(C['gold']))
    nc = [C['blue']] * 6 + [C['gold']] * 6 + [C['green']] * 4
    fig = go.Figure(go.Sankey(arrangement='snap',
        node=dict(pad=18, thickness=20, line=dict(color=C['bg_primary'], width=1), label=labels, color=nc),
        link=dict(source=src, target=tgt, value=val, color=lc)))
    return _layout(fig, "Money Flow: Income → Spending → Frequency", "How earning power translates to purchase velocity", height=520, showlegend=False)


# ══════════════════════════════════════════════════════════════
# SECTION 4: PLATFORM VALIDATION
# ══════════════════════════════════════════════════════════════

def plot_adoption_waterfall(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    seg = [df[df['Q7_Fan_Type'] == ft]['Platform_Adoption'].sum() for ft in fo]
    total = sum(seg)
    fig = go.Figure(go.Waterfall(
        x=fo + ['Total Adopters'], y=seg + [total],
        measure=['relative'] * 4 + ['total'],
        text=[f"+{v}" for v in seg] + [f"<b>{total}</b>"],
        textposition='outside', textfont=dict(color=C['text_primary'], size=12),
        connector=dict(line=dict(color=C['divider'], width=1)),
        increasing=dict(marker=dict(color=C['gold'])), totals=dict(marker=dict(color=C['green'])),
    ))
    fig.update_yaxes(title_text="Adopters")
    return _layout(fig, "Adoption Waterfall — Segment Contribution", "Which segments drive total platform adoption?", height=440, showlegend=False)


def plot_adoption_stacked(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    ao = ['Definitely yes', 'Probably yes', 'Not sure', 'Probably no', 'Definitely no']
    ac = [C['green'], C['green_light'], C['blue'], C['red_light'], C['red']]
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q21_Would_Use_Platform'], normalize='index').reindex(index=fo, columns=ao).fillna(0) * 100
    fig = go.Figure()
    for i, a in enumerate(ao):
        fig.add_trace(go.Bar(name=a, x=ct.index, y=ct[a], marker=dict(color=ac[i], cornerradius=2)))
    fig.update_layout(barmode='stack')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Platform Adoption by Fan Type", "80%+ of Collectors & Investors positive — core target confirmed")


def plot_trust_factors(df):
    tm = {'Trust_Third-party': 'Third-party Auth', 'Trust_Blockchain': 'Blockchain', 'Trust_Seller': 'Seller Ratings',
          'Trust_Money-back': 'Money-back Guarantee', 'Trust_AI-powered': 'AI Authenticity'}
    counts = {v: df[k].sum() for k, v in tm.items() if k in df.columns}
    sc = dict(sorted(counts.items(), key=lambda x: x[1]))
    colors = [C['gold'] if v == max(sc.values()) else C['blue'] for v in sc.values()]
    fig = go.Figure(go.Bar(
        y=list(sc.keys()), x=list(sc.values()), orientation='h', marker=dict(color=colors, cornerradius=4),
        text=[f"{v:,}" for v in sc.values()], textposition='outside', textfont=dict(color=C['text_primary']),
    ))
    return _layout(fig, "Trust-Building Features", "Which features make users trust the platform?", showlegend=False)


def plot_top_feature(df):
    counts = df[df['Top_Feature'] != 'Not provided']['Top_Feature'].value_counts()
    colors = [C['gold'] if i == 0 else C['blue_muted'] for i in range(len(counts))]
    fig = go.Figure(go.Bar(
        y=counts.index, x=counts.values, orientation='h', marker=dict(color=colors, cornerradius=4),
        text=[f"{v:,} ({v / len(df) * 100:.1f}%)" for v in counts.values],
        textposition='outside', textfont=dict(color=C['text_primary'], size=11),
    ))
    return _layout(fig, "#1 Ranked Feature", "Authentication verification leads across all segments", showlegend=False)


def plot_resell_by_fan(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    ro = ['Yes', 'Maybe', 'No']
    rc = [C['green'], C['gold'], C['red_light']]
    ct = pd.crosstab(df['Q7_Fan_Type'], df['Q23_Would_Resell'], normalize='index').reindex(index=fo, columns=ro).fillna(0) * 100
    fig = go.Figure()
    for i, r in enumerate(ro):
        fig.add_trace(go.Bar(name=r, x=ct.index, y=ct[r], marker=dict(color=rc[i], cornerradius=3)))
    fig.update_layout(barmode='group')
    fig.update_yaxes(title_text="%", ticksuffix="%")
    return _layout(fig, "Resell Intent by Segment", "75% of Investors would resell — two-sided marketplace confirmed")


def plot_loyalty_donut(df):
    order = ['Yes, strongly', 'Somewhat', 'Not really']
    counts = df['Q24_Loyalty_Interest'].value_counts().reindex(order).fillna(0)
    colors = [C['green'], C['gold'], C['text_muted']]
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.55,
                           marker=dict(colors=colors, line=dict(color=C['bg_primary'], width=2)),
                           textinfo='label+percent', textfont=dict(size=12, color=C['text_primary']), sort=False))
    pct = (counts.iloc[0] + counts.iloc[1]) / counts.sum() * 100
    fig.add_annotation(text=f"<b>{pct:.0f}%</b><br><span style='font-size:11px'>interested</span>",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=22, color=C['gold']))
    return _layout(fig, "Loyalty Program Interest", "80% interested — strong retention lever", height=380)


# ══════════════════════════════════════════════════════════════
# SECTION 5: DEEP ANALYSIS
# ══════════════════════════════════════════════════════════════

def plot_correlation_heatmap(df):
    cols = ['Age_Numeric', 'Income_Numeric', 'Q11_Authentication_Importance', 'Q13_Player_Popularity_Importance',
            'Q14_Rarity_Importance', 'Spend_Numeric', 'Freq_Numeric', 'Collector_Score', 'Value_Sensitivity', 'Platform_Adoption']
    avail = [c for c in cols if c in df.columns]
    corr = df[avail].corr()
    nice = {'Age_Numeric': 'Age', 'Income_Numeric': 'Income', 'Q11_Authentication_Importance': 'Auth Imp.',
            'Q13_Player_Popularity_Importance': 'Player Pop.', 'Q14_Rarity_Importance': 'Rarity Imp.',
            'Spend_Numeric': 'Spending', 'Freq_Numeric': 'Frequency', 'Collector_Score': 'Collector Score',
            'Value_Sensitivity': 'Value Sens.', 'Platform_Adoption': '★ Adoption'}
    labels = [nice.get(c, c) for c in avail]
    fig = go.Figure(go.Heatmap(z=corr.values, x=labels, y=labels, colorscale=DIVERGING_SCALE, zmin=-1, zmax=1,
                               text=np.round(corr.values, 2), texttemplate="%{text}", textfont=dict(color=C['text_primary'], size=10),
                               colorbar=dict(title="r", tickfont=dict(color=C['text_muted']))))
    return _layout(fig, "Correlation Matrix", "★ Adoption correlates with Collector Score, Auth & Rarity importance", height=550, showlegend=False)


def plot_collector_violin(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    fc = {'Casual viewer': C['text_muted'], 'Passionate fan': C['blue'], 'Hardcore collector': C['gold'], 'Investment buyer': C['green']}
    def _rgba(hex_c, a=0.2):
        h = hex_c.lstrip('#')
        return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'
    fig = go.Figure()
    for ft in fo:
        s = df[df['Q7_Fan_Type'] == ft]
        fig.add_trace(go.Violin(y=s['Collector_Score'], name=ft, line_color=fc[ft], fillcolor=_rgba(fc[ft]), meanline_visible=True, box_visible=True))
    fig.update_yaxes(title_text="Collector Score")
    return _layout(fig, "Collector Score Distribution", "Clear segment separation — Hardcore peaks 28–48, Casuals 1–3")


def plot_adoption_drivers(df):
    cols = ['Collector_Score', 'Q11_Authentication_Importance', 'Q14_Rarity_Importance', 'Value_Sensitivity',
            'Auth_Rarity_Index', 'Freq_Numeric', 'Spend_Numeric', 'Income_Numeric', 'Q13_Player_Popularity_Importance', 'Age_Numeric']
    nice = {'Collector_Score': 'Collector Score', 'Q11_Authentication_Importance': 'Auth Importance',
            'Q14_Rarity_Importance': 'Rarity Importance', 'Value_Sensitivity': 'Value Sensitivity',
            'Auth_Rarity_Index': 'Auth × Rarity', 'Freq_Numeric': 'Purchase Freq.', 'Spend_Numeric': 'Spending',
            'Income_Numeric': 'Income', 'Q13_Player_Popularity_Importance': 'Player Pop. Imp.', 'Age_Numeric': 'Age'}
    avail = [c for c in cols if c in df.columns]
    corr = df[avail + ['Platform_Adoption']].corr()['Platform_Adoption'].drop('Platform_Adoption').reindex(avail).sort_values()
    labels = [nice.get(c, c) for c in corr.index]
    colors = [C['green'] if v > 0 else C['red_light'] for v in corr.values]
    fig = go.Figure(go.Bar(y=labels, x=corr.values, orientation='h', marker=dict(color=colors, cornerradius=3),
                           text=[f"{v:.3f}" for v in corr.values], textposition='outside', textfont=dict(color=C['text_primary'], size=11)))
    fig.update_xaxes(title_text="Correlation with Platform Adoption", zeroline=True, zerolinecolor=C['divider'])
    return _layout(fig, "Adoption Drivers — What Predicts Platform Use?", "Ranked by correlation with North Star (Adoption)", height=480, showlegend=False)


def plot_segment_radar(df):
    fo = ['Casual viewer', 'Passionate fan', 'Hardcore collector', 'Investment buyer']
    metrics = ['Q11_Authentication_Importance', 'Q14_Rarity_Importance', 'Q13_Player_Popularity_Importance', 'Freq_Numeric', 'Spend_Numeric']
    nice = ['Authentication', 'Rarity', 'Player Pop.', 'Frequency', 'Spending']
    fc = [C['text_muted'], C['blue'], C['gold'], C['green']]
    norm = df[metrics].copy()
    for col in metrics:
        mn, mx = norm[col].min(), norm[col].max()
        if mx > mn: norm[col] = (norm[col] - mn) / (mx - mn)
    def _rgba(hex_c, a=0.13):
        h = hex_c.lstrip('#')
        return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'
    fig = go.Figure()
    for i, ft in enumerate(fo):
        vals = norm[df['Q7_Fan_Type'] == ft][metrics].mean().tolist()
        vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(r=vals, theta=nice + [nice[0]], name=ft, fill='toself',
                                      line=dict(color=fc[i], width=2), fillcolor=_rgba(fc[i])))
    fig.update_layout(polar=dict(bgcolor=C['bg_card'],
                                 radialaxis=dict(visible=True, range=[0, 1], gridcolor=C['grid'], tickfont=dict(color=C['text_muted'], size=9)),
                                 angularaxis=dict(gridcolor=C['grid'], tickfont=dict(color=C['text_secondary'], size=11))))
    return _layout(fig, "Segment Profile Radar", "Normalized comparison — each segment's fingerprint", height=500)


# ══════════════════════════════════════════════════════════════
# KEY METRICS
# ══════════════════════════════════════════════════════════════

def get_key_metrics(df):
    total = len(df)
    adopt = df['Platform_Adoption'].mean() * 100
    hi = (df['Q21_Would_Use_Platform'] == 'Definitely yes').mean() * 100
    hv = df['Q7_Fan_Type'].isin(['Hardcore collector', 'Investment buyer']).mean() * 100
    own = (df['Q8_Own_Jerseys'] == 'Yes').mean() * 100
    resell = (df['Q23_Would_Resell'] == 'Yes').mean() * 100
    hva = len(df[(df['Q7_Fan_Type'].isin(['Hardcore collector', 'Investment buyer'])) & (df['Platform_Adoption'] == 1)]) / total * 100
    return {
        'total_responses': total, 'adoption_rate': round(adopt, 1), 'high_intent_pct': round(hi, 1),
        'high_value_segment_pct': round(hv, 1), 'own_jersey_pct': round(own, 1),
        'resell_interest_pct': round(resell, 1), 'hv_adopter_pct': round(hva, 1),
        'outlier_count': df['Outlier_Flag'].sum(),
    }
