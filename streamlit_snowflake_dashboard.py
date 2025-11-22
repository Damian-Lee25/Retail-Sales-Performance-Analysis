import streamlit as st
import pandas as pd
import plotly.express as px
import logging

# ------------ Logging Setup ------------
logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Page setup 
st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("📊 Retail Sales Dashboard")

@st.cache_data
def load_data():
    try:
        data = "sales_cleaned.csv"
        return pd.read_csv(data)
    except FileNotFoundError as e:
        logging.error(e)
        st.error("❌ The file 'sales_cleaned.csv' was not found.")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        logging.error(e)
        st.error("❌ CSV file could not be parsed—file may be corrupted.")
        return pd.DataFrame()
    except Exception as e:
        logging.exception("Unexpected error loading data")
        st.error(f"❌ Unexpected error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- Data processing with error handling ---
try:
    df.columns = df.columns.str.upper()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['MONTH_NAME'] = df['DATE'].dt.strftime('%B')
    df['MONTH_NUM'] = df['DATE'].dt.month
except Exception as e:
    logging.exception("Error processing data columns")
    st.error(f"❌ Error processing data columns: {e}")
    st.stop()

# --- Sidebar Filters 
st.sidebar.title("Filters")

try:
    regions = st.sidebar.multiselect("Select Region(s):", df['REGION'].unique(), default=df['REGION'].unique())
    products = st.sidebar.multiselect("Select Product(s):", df['PRODUCT'].unique(), default=df['PRODUCT'].unique())
    df = df[df['REGION'].isin(regions) & df['PRODUCT'].isin(products)]
    if df.empty:
        st.warning("⚠️ No data available after applying filters.")
except Exception as e:
    logging.exception("Filter processing error")
    st.error(f"❌ Error applying filters: {e}")
    st.stop()

# --- Top KPIs
try:
    total_sales = df['SALES'].sum()
    top_product = df.groupby('PRODUCT')['SALES'].sum().idxmax()
    top_region = df.groupby('REGION')['SALES'].sum().idxmax()
    avg_monthly_sales = df.groupby('MONTH_NUM')['SALES'].sum().mean()
except Exception as e:
    logging.exception("Error computing KPIs")
    st.error(f"❌ Error computing KPI values: {e}")
    st.stop()

jan_sales = 78000.04
apr_sales = 24280.16

try:
    sales_drop_pct = ((apr_sales - jan_sales) / jan_sales) * 100
except Exception as e:
    logging.exception("Error computing sales drop")
    st.error(f"❌ Error computing sales drop: {e}")
    sales_drop_pct = 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("📉 Sales Drop Jan → Apr", f"{abs(sales_drop_pct):.1f}%", delta=f"{sales_drop_pct:.1f}%")
kpi2.metric("💰 Total Sales", f"${total_sales:,.0f}")
kpi3.metric("🏆 Top Product", top_product)
kpi4.metric("🌍 Top Region", top_region)
kpi5.metric("📈 Avg Monthly Sales", f"${avg_monthly_sales:,.0f}")

st.markdown("---")

# --- Analysis Menu 
option = st.sidebar.selectbox(
    "Chose a Visual:",
    ["1. Product Sales Performance", "2. Monthly Trends", "3. Regional Insights"]
)

# --- Product Sales Performance 
if option == "1. Product Sales Performance":
    try:
        by_product = df.groupby('PRODUCT', as_index=False)['SALES'].sum().sort_values(by='SALES', ascending=False)

        fig = px.bar(
            by_product, 
            x='PRODUCT', 
            y='SALES', 
            color='SALES',
            text='SALES',
            labels={'SALES': 'Total Sales', 'PRODUCT': 'Product'},
            title="📊 Product Sales Performance",
            color_continuous_scale='Blues'
        )

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

        st.subheader("Product C is the top performing product")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Detailed Table")
        st.dataframe(by_product)
    except Exception as e:
        logging.exception("Error generating Product Sales chart")
        st.error(f"❌ Error generating Product Sales chart: {e}")

# --- Monthly Trends 
elif option == "2. Monthly Trends":
    try:
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

        st.subheader("Sales are down 69% overall")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Monthly Totals")
        st.dataframe(monthly[['MONTH_NAME', 'SALES', 'MoM_Change_%']])
        st.info(
            f"💡 Highest monthly sales: "
            f"{monthly.loc[monthly['SALES'].idxmax(),'MONTH_NAME']} "
            f"(${monthly['SALES'].max():,.0f})"
        )
    except Exception as e:
        logging.exception("Error generating Monthly Trends chart")
        st.error(f"❌ Error generating Monthly Trends chart: {e}")
             


# --- Regional Insights
elif option == "3. Regional Insights":
    try:
        
        df['MONTH'] = df['DATE'].dt.strftime('%Y-%m')

        
        regional_monthly = df.groupby(['MONTH', 'REGION'], as_index=False)['SALES'].sum()
        regional = df.groupby(['REGION', 'PRODUCT'], as_index=False)['SALES'].sum()

        
        fig = px.line(
            regional_monthly,
            x="MONTH",
            y="SALES",
            color="REGION",
            markers=True,
            title="🏙️ Regional Sales Over Time",
            labels={"MONTH": "Month", "SALES": "Total Sales", "REGION": "Region"}
        )

        
        fig.update_layout(
            showlegend=True,
            legend=dict(
                title="Region",
                orientation="h",         
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, color="black")
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black"),
            title_font=dict(size=20)
        )

        
        fig.update_xaxes(tickfont=dict(size=12, color="black"))
        fig.update_yaxes(tickfont=dict(size=12, color="black"))

        st.subheader("Regional Sales Trends Over Time")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Detailed Monthly Regional Sales")
        st.dataframe(regional)
        st.markdown("Region Total Sales")
        st.dataframe(df.groupby('REGION',as_index=False)['SALES'].sum().sort_values(by='SALES',ascending=False))

    

    except Exception as e:
        logging.exception("Error generating Regional Insights chart")
        st.error(f"❌ Error generating Regional Insights chart: {e}")

st.markdown("---")
st.caption("Retail Sales Performance Analysis")

