import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration & Styling ---
st.set_page_config(page_title="Executive Student Insights", layout="wide")

# คลุมโทนสีตามที่คุณกำหนด (แก้เลขศูนย์ในรหัสสีให้ถูกต้อง)
theme_colors = ['#FD536D', '#FF8957', '#EED054', '#CAD849', '#00C182', '#429EB0']

# --- Load Data ---
@st.cache_data
def load_data():
    path = '/workspaces/KaninggDashboard/data/student_dropout_dataset_v3.csv'
    df = pd.read_csv(path)
    cols = ['Age', 'Gender', 'Family_Income', 'Study_Hours_per_Day', 'Travel_Time_Minutes', 'Dropout']
    df = df[cols].dropna()
    df['Dropout_Status'] = df['Dropout'].map({1: 'Dropped Out', 0: 'Stayed'})
    return df

df = load_data()

# --- Sidebar Filters ---
with st.sidebar:
    st.header("🛠️ Data Filters")
    st.info("ปรับแต่งช่วงข้อมูลที่ต้องการวิเคราะห์")
    age_range = st.slider("ช่วงอายุ (Age)", 
                          int(df['Age'].min()), int(df['Age'].max()), 
                          (int(df['Age'].min()), int(df['Age'].max())))
    genders = st.multiselect("เลือกเพศ (Gender)", options=df['Gender'].unique(), default=df['Gender'].unique())
    st.divider()
    st.write("📌 *Dashboard จะอัปเดตอัตโนมัติ*")

mask = (df['Age'].between(*age_range)) & (df['Gender'].isin(genders))
df_filtered = df[mask]

# --- MAIN DASHBOARD ---
st.title("🚀 Student Analytics Executive Summary")
st.markdown("---")

# --- 1. OVERALL METRICS (Header Row) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Age (Average)", f"{df_filtered['Age'].mean():.1f} yrs")
with m2:
    st.metric("Avg. Family Income", f"{df_filtered['Family_Income'].mean():,.0f} ฿")
with m3:
    st.metric("Study Hours/Day", f"{df_filtered['Study_Hours_per_Day'].mean():.1f} hrs")
with m4:
    dropout_rate = (df_filtered['Dropout'].mean() * 100)
    st.metric("Dropout Rate", f"{dropout_rate:.1f}%")

st.markdown("###") # เพิ่มช่องว่าง

# --- 2. DEMOGRAPHICS & STATUS (Main Row) ---
col_left, col_right = st.columns([1, 1])

with col_left:
    with st.container(border=True):
        st.subheader("👥 Dropout by Age Distribution")
        fig_age = px.histogram(df_filtered, x='Age', color='Dropout_Status',
                              barmode='group',
                              color_discrete_map={'Stayed': theme_colors[5], 'Dropped Out': theme_colors[0]})
        fig_age.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
        st.plotly_chart(fig_age, use_container_width=True)

with col_right:
    with st.container(border=True):
        st.subheader("🚻 Dropout Count by Gender")
        gender_stats = df_filtered.groupby(['Gender', 'Dropout_Status']).size().reset_index(name='Count')
        fig_gen = px.bar(gender_stats, x='Gender', y='Count', color='Dropout_Status',
                        barmode='stack',
                        color_discrete_map={'Stayed': theme_colors[4], 'Dropped Out': theme_colors[1]})
        fig_gen.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=350)
        st.plotly_chart(fig_gen, use_container_width=True)

# --- 3. DEEP ANALYSIS (Scatter & Heatmap) ---
st.markdown("### 🎯 Relationship & Correlation Analysis")
col_scat, col_heat = st.columns([1.5, 1])

with col_scat:
    with st.container(border=True):
        c_a, c_b = st.columns(2)
        with c_a: x_val = st.selectbox("แกน X", ['Family_Income', 'Study_Hours_per_Day', 'Travel_Time_Minutes'], index=0)
        with c_b: y_val = st.selectbox("แกน Y", ['Study_Hours_per_Day', 'Family_Income', 'Travel_Time_Minutes'], index=0)
        
        fig_scatter = px.scatter(df_filtered, x=x_val, y=y_val, color='Dropout_Status', 
                                hover_name='Gender', size_max=12,
                                color_discrete_map={'Stayed': theme_colors[5], 'Dropped Out': theme_colors[0]},
                                template="plotly_white")
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

with col_heat:
    with st.container(border=True):
        st.write("**Correlation Matrix**")
        corr = df_filtered[['Age', 'Family_Income', 'Study_Hours_per_Day', 'Travel_Time_Minutes', 'Dropout']].corr()
        fig_heat = px.imshow(corr, text_auto=".2f", 
                            color_continuous_scale=[theme_colors[0], theme_colors[2], theme_colors[4]])
        fig_heat.update_layout(height=435, margin=dict(t=10))
        st.plotly_chart(fig_heat, use_container_width=True)

# --- 4. BEHAVIORAL INSIGHTS (Bottom Row) ---
row3_1, row3_2, row3_3 = st.columns([1, 1, 1])

with row3_1:
    with st.container(border=True):
        st.write("**Travel Impact**")
        fig_travel = px.box(df_filtered, x='Dropout_Status', y='Travel_Time_Minutes',
                           color='Dropout_Status',
                           color_discrete_map={'Stayed': theme_colors[3], 'Dropped Out': theme_colors[0]})
        fig_travel.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_travel, use_container_width=True)

with row3_2:
    with st.container(border=True):
        st.write("**Student Proportion**")
        fig_pie = px.pie(df_filtered, names='Dropout_Status', hole=0.5,
                        color_discrete_sequence=[theme_colors[5], theme_colors[0]])
        fig_pie.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

with row3_3:
    with st.container(border=True):
        st.write("**Avg Income by Gender**")
        inc_gen = df_filtered.groupby('Gender')['Family_Income'].mean().reset_index()
        fig_inc = px.bar(inc_gen, x='Gender', y='Family_Income', 
                         color_discrete_sequence=[theme_colors[1]])
        fig_inc.update_layout(height=300)
        st.plotly_chart(fig_inc, use_container_width=True)

# --- Table ---
with st.expander("📂 View Filtered Dataset"):
    st.dataframe(df_filtered, use_container_width=True)
