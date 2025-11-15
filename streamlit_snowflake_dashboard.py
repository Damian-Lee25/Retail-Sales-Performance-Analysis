import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup 
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("📊 Retail Sales Dashboard")

# ---  Query data 
df = session.table("SALES.PUBLIC.SOURCE").to_pandas()
df['DATE'] = pd.to_datetime(df['DATE'])
df['MONTH_NAME'] = df['DATE'].dt.strftime('%B')
df['MONTH_NUM'] = df['DATE'].dt.month

# --- Sidebar Filters 
st.sidebar.title("Filters")
regions = st.sidebar.multiselect("Select Region(s):", df['REGION'].unique(), default=df['REGION'].unique())
products = st.sidebar.multiselect("Select Product(s):", df['PRODUCT'].unique(), default=df['PRODUCT'].unique())
df = df[df['REGION'].isin(regions) & df['PRODUCT'].isin(products)]

# --- Top KPIs
total_sales = df['SALES'].sum()
top_product = df.groupby('PRODUCT')['SALES'].sum().idxmax()
top_region = df.groupby('REGION')['SALES'].sum().idxmax()
avg_monthly_sales = df.groupby('MONTH_NUM')['SALES'].sum().mean()
jan_sales = 78000.04
apr_sales = 24280.16
sales_drop_pct = ((apr_sales - jan_sales) / jan_sales) * 100 

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("📉 Sales Drop Jan → Apr", f"{abs(sales_drop_pct):.1f}%", delta=f"{sales_drop_pct:.1f}%")
kpi2.metric("💰 Total Sales", f"${total_sales:,.0f}")
kpi3.metric("🏆 Top Product", top_product)
kpi4.metric("🌍 Top Region", top_region)
kpi5.metric("📈 Avg Monthly Sales", f"${avg_monthly_sales:,.0f}")

st.markdown("---")

# --- Analysis Menu 
option = st.sidebar.selectbox(
    "Choose a Visual:",
    ["1. Product Sales Performance", "2. Monthly Trends", "3. Regional Insights"]
)

# --- Product Sales Performance 
if option == "1. Product Sales Performance":
    by_product = df.groupby('PRODUCT', as_index=False)['SALES'].sum().sort_values(by='SALES', ascending=False)

    fig = px.bar(
        by_product, 
        x='PRODUCT', 
        y='SALES', 
        color='SALES',
        text='SALES',
        labels={'SALES': 'Total Sales', 'PRODUCT': 'Product'},
        title="📊 Product Sales Performance",
        color_continuous_scale='Blues'  # subtle color scale for readability
    )

    # --- Updated styling for better label visibility ---
    fig.update_traces(
        texttemplate='%{text:,.0f}',      
        textposition='outside',
        textfont=dict(color='black', size=12, family='Arial Black')  
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),          
        title_font=dict(size=20, color='black', family='Arial Black'),
        margin=dict(t=70, b=70)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Detailed Table")
    st.dataframe(by_product)


# --- Monthly Trends 
elif option == "2. Monthly Trends":
    monthly = df.groupby(['MONTH_NUM', 'MONTH_NAME'])['SALES'].sum().reset_index()
    monthly = monthly.sort_values('MONTH_NUM')
    monthly['MoM_Change_%'] = monthly['SALES'].pct_change() * 100  
    monthly['MoM_Change_%'] = monthly['MoM_Change_%'].round(2)
    fig = px.line(
        monthly,
        x='MONTH_NAME',
        y='SALES',
        markers=True,
        title="📈 Monthly Sales Trend",
        labels={'SALES': 'Sales', 'MONTH_NAME': 'Month'}
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Monthly Totals")
    st.dataframe(monthly[['MONTH_NAME', 'SALES', 'MoM_Change_%']])
    st.info(f"💡 Highest monthly sales: {monthly.loc[monthly['SALES'].idxmax(),'MONTH_NAME']} (${monthly['SALES'].max():,.0f})")

# --- Regional Insights
elif option == "3. Regional Insights":
    regional = df.groupby(['REGION', 'PRODUCT'], as_index=False)['SALES'].sum()
    fig = px.bar(
        regional,
        x='REGION',
        y='SALES',
        color='PRODUCT',
        text='SALES',
        labels={'SALES': 'Total Sales', 'REGION': 'Region', 'PRODUCT': 'Product'},
        title="🏙️ Product Sales by Region"
    )
    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Detailed Table")
    st.dataframe(regional)
    st.markdown("Region Total Sales")
    st.dataframe(df.groupby('REGION',as_index=False)['SALES'].sum().sort_values(by='SALES',ascending=False))

st.markdown("---")
st.caption("Dashboard built with Streamlit & Snowflake Snowpark")
