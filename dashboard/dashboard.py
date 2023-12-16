import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from babel.numbers import format_currency
import warnings
warnings.filterwarnings('ignore')

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
st.plotly_chart(daily_orders_df_plot, theme='streamlit')

st.subheader("Grafik Total Pelanggan per Negara Bagian")

demographic_df_plot = px.bar(demographic_df.head(10), x='customer_state', y='total_customers', color='customer_state', title='Jumlah Customer Berdasarkan Lokasi', template='plotly_dark')
st.plotly_chart(demographic_df_plot, theme='streamlit')

st.subheader("Grafik Rata-rata Rating Produk per Bulan")

average_rating_in_month_plot = px.line(average_rating_in_month, x='month', y='average_rating', color='year', title='Rata-Rata Rating Setiap Bulan', markers=True, template='plotly_dark')
st.plotly_chart(average_rating_in_month_plot, theme='streamlit')

st.subheader("Pelanggan terbaik berdasarkan RFM")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df['recency'].mean(), 1)
    st.metric(label='Rata-rata Recency', value=avg_recency)

with col2:
    avg_frequency = round(rfm_df['frequency'].mean(), 1)
    st.metric(label='Rata-rata Frequency', value=avg_frequency)

with col3:
    avg_monetary = round(rfm_df['monetary'].mean(), 1)
    st.metric(label='Rata-rata Monetary', value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by='recency', ascending=False).head(), ax=ax[0], palette=colors)
ax[0].set_title("By Recency", fontsize=40, loc='center')
ax[0].set_xlabel("Customer ID", fontsize=20)
ax[0].set_ylabel("Recency", fontsize=20)
ax[0].tick_params(axis='x', labelsize=15, rotation=45)
ax[0].set_xticklabels(ax[0].get_xticklabels(), horizontalalignment='right', fontsize=14)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by='frequency', ascending=False).head(), ax=ax[1], palette=colors)
ax[1].set_title("By Frequency", fontsize=40, loc='center')
ax[1].set_xlabel("Customer ID", fontsize=20)
ax[1].set_ylabel("Frequency", fontsize=20)
ax[1].tick_params(axis='x', labelsize=15, rotation=45)
ax[0].set_xticklabels(ax[1].get_xticklabels(), horizontalalignment='right', fontsize=14)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by='monetary', ascending=False).head(), ax=ax[2], palette=colors)
ax[2].set_title("By Monetary", fontsize=40, loc='center')
ax[2].set_xlabel("Customer ID", fontsize=20)
ax[2].set_ylabel("Monetary", fontsize=20)
ax[2].tick_params(axis='x', labelsize=15, rotation=45)
ax[0].set_xticklabels(ax[2].get_xticklabels(), horizontalalignment='right', fontsize=14)

fig.suptitle("RFM Analysis Customer", fontsize=50)
st.pyplot(fig)