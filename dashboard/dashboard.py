import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from babel.numbers import format_currency
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(layout="wide")

def daily_sales(dataframe: pd.DataFrame) -> pd.DataFrame:
    daily_orders_df = dataframe.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df.reset_index(inplace=True)
    daily_orders_df.rename(columns={
        "order_purchase_timestamp": "Waktu Pesanan",
        "order_id": "Jumlah Pesanan",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df


def create_demographic_df(dataframe: pd.DataFrame) -> pd.DataFrame: 
    demographic_df = dataframe.groupby(by='customer_state').size().reset_index(name='total_customers')
    demographic_df.sort_values(by='total_customers', ascending=False, inplace=True)

    return demographic_df

def create_average_rating_in_month_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    average_rating_in_month = dataframe.groupby(['order_purchase_year', 'order_purchase_month'], as_index=False).agg({
    'review_score' : 'mean' # Menghitung rata-rata skor review
    })
    average_rating_in_month.columns = ['year', 'month', 'average_rating']
    
    return average_rating_in_month

def create_rfm_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    rfm_df = dataframe.groupby(by='customer_unique_id', as_index=False).agg({
        'order_purchase_timestamp' : lambda x: (dataframe['order_purchase_timestamp'].max().date() - x.max().date()).days, 
        'order_id' : 'nunique', 
        'price' : 'sum'
    })
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    return rfm_df

def sort_values_df(dataframe: pd.DataFrame, column: str, ascending: bool) -> pd.DataFrame:
    dataframe.sort_values(by=column, ascending=ascending, inplace=True)
    
    return dataframe

all_df = pd.read_csv('./dashboard/all_data_dashboard.csv')
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])
all_df.reset_index(inplace=True)

min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

st.sidebar.header("Filter Tanggal Order")
try:
    with st.sidebar:
            start_date, end_date = st.date_input(
                label='Rentang Waktu', min_value=min_date,
                max_value=max_date,
                value=[min_date, max_date]
            )
except:
    st.sidebar.error("Silahkan pilih rentang waktu yang tersedia")
    st.stop()

filtered_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) & 
                     (all_df['order_purchase_timestamp'] <= str(end_date))]

daily_orders_df = daily_sales(filtered_df)
demographic_df = create_demographic_df(filtered_df)
average_rating_in_month = create_average_rating_in_month_df(filtered_df)
rfm_df = create_rfm_df(filtered_df)


st.title("Dashboard Submission Dicoding: Analisis Dataset E-Commerce")

st.markdown(
    """
    - Nama: Dzulfikri Adjmal
- Email: dzulfikriadjmal@gmail.com
- Id Dicoding: dzulfikriadjmal 
    """
)

st.subheader("Grafik Total Order Harian")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df['Jumlah Pesanan'].sum()
    st.metric(label='Total Order', value=total_order)

with col2:
    total_revenue = daily_orders_df['revenue'].sum()
    total_revenue = format_currency(total_revenue, 'BRL', locale='pt_BR')
    st.metric(label='Total Revenue', value=total_revenue)

daily_orders_df_plot = px.line(daily_orders_df, x='Waktu Pesanan', y='Jumlah Pesanan', title='Total Order Harian', markers=True, template='plotly_dark')
st.plotly_chart(daily_orders_df_plot, use_container_width=True, theme='streamlit')

st.subheader("Grafik Total Pelanggan per Negara Bagian")

demographic_df_plot = px.bar(demographic_df.head(10), x='customer_state', y='total_customers', color='customer_state', title='Jumlah Customer Berdasarkan Lokasi', template='plotly_dark')
st.plotly_chart(demographic_df_plot, use_container_width=True, theme='streamlit')

st.subheader("Grafik Rata-rata Rating Produk per Bulan")

average_rating_in_month_plot = px.line(average_rating_in_month, x='month', y='average_rating', color='year', title='Rata-Rata Rating Setiap Bulan', markers=True, template='plotly_dark')
st.plotly_chart(average_rating_in_month_plot, use_container_width=True, theme='streamlit')

st.subheader("Pelanggan terbaik berdasarkan RFM")

col1, col2, col3 = st.columns(3)

try: 
    with col1:
        avg_recency = round(rfm_df['recency'].mean(), 1)
        st.metric(label='Rata-rata Recency', value=avg_recency)

    with col2:
        avg_frequency = round(rfm_df['frequency'].mean(), 1)
        st.metric(label='Rata-rata Frequency', value=avg_frequency)

    with col3:
        avg_monetary = round(rfm_df['monetary'].mean(), 1)
        st.metric(label='Rata-rata Monetary', value=format_currency(avg_monetary, 'BRL', locale='pt_BR'))
except:
    st.error("Tidak ada data yang tersedia")

figPlotly = make_subplots(rows=1, cols=3, subplot_titles=("Recency", "Frequency", "Monetary"))

df_recency = sort_values_df(rfm_df, 'recency', False).head()
figPlotly.add_trace(
    go.Bar(y=df_recency['recency'], x=df_recency['customer_id'], text=df_recency['recency'], marker_color='#90CAF9'),
    row=1, col=1
)

df_frequency = sort_values_df(rfm_df, 'frequency', False).head()
figPlotly.add_trace(
    go.Bar(y=df_frequency['frequency'], x=df_frequency['customer_id'], text=df_frequency['frequency'], marker_color='#90CAF9'),
    row=1, col=2
)

df_monetary = sort_values_df(rfm_df, 'monetary', False).head()
figPlotly.add_trace(
    go.Bar(y=df_monetary['monetary'], x=df_monetary['customer_id'], text=df_monetary['monetary'], marker_color='#90CAF9'),
    row=1, col=3
)

figPlotly.update_xaxes(title_text="Customer ID", row=1, col=1)
figPlotly.update_xaxes(title_text="Customer ID", row=1, col=2)
figPlotly.update_xaxes(title_text="Customer ID", row=1, col=3)

figPlotly.update_layout(height=600, width=1200, title_text="RFM Analysis Customer", title_x=0.5, title_font_size=20, template='plotly_dark')
figPlotly.update_traces(showlegend=False)
st.plotly_chart(figPlotly, use_container_width=True, theme='streamlit')