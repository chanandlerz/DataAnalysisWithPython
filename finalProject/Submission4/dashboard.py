import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from scipy.stats import linregress
from scipy.stats import ttest_ind
sns.set(style='dark')

def create_rfm_df(df,day_df):

    reference_date = day_df['dteday'].max()

    rfm_df = df.groupby('instant').agg({
    'dteday': lambda x: (reference_date - x.max()).days, 
    'instant': 'count', 
    'cnt': 'sum'         
    })

    rfm_df.rename(columns={'dteday': 'recency', 'instant': 'frequency', 'cnt': 'monetary'}, inplace=True)

    print("rfm_df: ", rfm_df)

    return rfm_df

def create_relation_tempcnt(df):
    temp_cnt_df = df[['instant','temp','cnt']]

    return temp_cnt_df

def create_relation_holidayvsnon(df):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(x='holiday', y='cnt', data=df, ax=ax)
    
    ax.set_title("Bike Rentals on Holiday vs Non-Holiday")
    ax.set_xlabel("Holiday (1 = Holiday, 0 = Non-Holiday)")
    ax.set_ylabel("Total Rentals")
    ax.set_xticklabels(['Non-Holiday', 'Holiday'])

    st.pyplot(fig)


    holiday_rentals = df[df['holiday'] == 1]['cnt']
    non_holiday_rentals = df[df['holiday'] == 0]['cnt']

    t_stat, p_value = ttest_ind(holiday_rentals, non_holiday_rentals)

    st.write(f"T-statistic: {t_stat}")
    st.write(f"P-value: {p_value}")

    if p_value < 0.05:
        st.write("There is a significant correlation between holiday and bike rentals (reject the null hypothesis).")
    else:
        st.write("There is no significant correlation between holiday and bike rentals (fail to reject the null hypothesis).")

def calculate_churn_risk(rfm_df, recency_threshold=90, frequency_threshold=1):
    """
    Menentukan jumlah pelanggan yang berisiko churn berdasarkan RFM analysis.
    
    Args:
        rfm_df (DataFrame): DataFrame hasil RFM analysis.
        recency_threshold (int): Ambang batas hari sejak transaksi terakhir untuk dikategorikan sebagai churn.
        frequency_threshold (int): Ambang batas jumlah transaksi minimum.
    
    Returns:
        int: Jumlah pelanggan berisiko churn.
    """
    churn_customers = rfm_df[
        (rfm_df['recency'] > recency_threshold) & (rfm_df['frequency'] <= frequency_threshold)
    ]
    return churn_customers.shape[0]

# finalProject/Submission3/data/day.csv
day_df = pd.read_csv("data/day.csv")
# day_df = pd.read_csv("/home/nadia/Documents/DICODING/DataAnalysis with Python/finalProject/Submission3/data/day.csv")

day_df["dteday"] = pd.to_datetime(day_df['dteday'])

day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)


min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

start_date = min_date
end_date = max_date

with st.sidebar:
    # logo disini nnti
    st.image("data/bicycle.png",width=150)
    # st.image("/home/nadia/Documents/DICODING/DataAnalysis with Python/finalProject/Submission3/data/bicycle.png",width=150)

    st.write("This is bike-sharing rent data from 2011 to 2012")

    date_range = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1: 
        start_date = date_range[0]
        end_date = max_date
    else:
        st.error("Please select both start and end dates.")

    
main_df = day_df[(day_df["dteday"]>= str(start_date)) & (day_df["dteday"] <= str(end_date))]

rfm_df = create_rfm_df(main_df, day_df)

temp_cnt_df = create_relation_tempcnt(main_df)


st.header('Bike-sharing rental')

st.subheader('RFM Analysis')

col1, col2 = st.columns(2)

with col1:
    recent = rfm_df.recency.min()
    st.metric("Recency: ", value=recent)

with col2:
    total_rents = rfm_df.monetary.sum()
    st.metric("Rent total: ", value=total_rents)

fig,ax = plt.subplots(figsize=(16,8))
ax.plot(
    rfm_df['recency'],
    rfm_df['monetary'],
    marker='o',
    linewidth=2,
    color="#222f5b"
)

ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


st.subheader('Daily Bike-Rent by Temperature')

fig, ax = plt.subplots(1, 2, figsize=(12, 5))

temp_cnt_df['temp'].plot(kind='hist', ax=ax[0], title='Temperature Distribution')
ax[0].set_xlabel('Temperature')

temp_cnt_df['cnt'].plot(kind='hist', ax=ax[1], title='Count of Bike Rentals')
ax[1].set_xlabel('Bike Rentals')

# Display the plot in Streamlit
st.pyplot(fig)


# fig,ax = plt.scatter(x=temp_cnt_df['temp'],y=temp_cnt_df['cnt'])
# ax.plot(temp_cnt_df['temp'],temp_cnt_df['cnt'])
# st.pyplot(fig)

# menambahkan manual grouping 
def categorize_temp(temp):
    if temp < 0.3:
        return 'Cold'
    elif temp <= 0.6:
        return 'Normal'
    else:
        return 'Hot'

def categorize_weather(weather):
    return 'Good' if weather in [1, 2] else 'Bad'

def categorize_season(season):
    return 'Cold' if season in [3,4] else 'Hot'

def categorize_humidity(hum):
    if hum < 0.4:
        return 'Dry'
    elif hum <= 0.7:
        return 'Normal'
    else:
        return 'Humid'

def categorize_day(holiday, workingday):
    if holiday == 1:
        return 'Holiday'
    elif workingday == 1:
        return 'Working Day'
    else:
        return 'Weekend'

main_df['Temp_Group'] = main_df['temp'].apply(categorize_temp)
main_df['Weather_Group'] = main_df['weathersit'].apply(categorize_weather)
main_df['Season_Group'] = main_df['season'].apply(categorize_season)
main_df['Humidity_Group'] = main_df['hum'].apply(categorize_humidity)
main_df['Day_Type'] = main_df.apply(lambda x: categorize_day(x['holiday'], x['workingday']), axis=1)

df_temp = main_df.groupby('Temp_Group')[['cnt']].sum().reset_index()
df_weather = main_df.groupby('Weather_Group')[['cnt']].sum().reset_index()
df_season = main_df.groupby('Season_Group')[['cnt']].sum().reset_index()
df_humidity = main_df.groupby('Humidity_Group')[['cnt']].sum().reset_index()
df_day = main_df.groupby('Day_Type')[['cnt']].sum().reset_index()

st.title("Bike Rental Grouping")

tabs = st.tabs(["Temperature", "Weather", "Season", "Humidity", "Day Type"])

tabs[0].write(df_temp)
tabs[1].write(df_weather)
tabs[2].write(df_season)
tabs[3].write(df_humidity)
tabs[4].write(df_day)

fig_temp = px.bar(df_temp, x='Temp_Group', y='cnt', title='Rentals by Temperature', color='Temp_Group')
fig_weather = px.bar(df_weather, x='Weather_Group', y='cnt', title='Rentals by Weather', color='Weather_Group')
fig_season = px.bar(df_season, x='Season_Group', y='cnt', title='Rentals by Season', color='Season_Group')
fig_humidity = px.bar(df_humidity, x='Humidity_Group', y='cnt', title='Rentals by Humidity', color='Humidity_Group')
fig_day = px.bar(df_day, x='Day_Type', y='cnt', title='Rentals by Day Type', color='Day_Type')

tabs[0].plotly_chart(fig_temp)
tabs[1].plotly_chart(fig_weather)
tabs[2].plotly_chart(fig_season)
tabs[3].plotly_chart(fig_humidity)
tabs[4].plotly_chart(fig_day)

###


fig,ax = plt.subplots(figsize=(16,8))
ax.scatter(x=temp_cnt_df['temp'],y=temp_cnt_df['cnt'])
st.pyplot(fig)

st.write("There is a positive correlation between temperature and bike-sharing rent count.")



st.subheader("Bike Rentals on Holiday vs Non-Holiday")
relation_holidayvsnon = create_relation_holidayvsnon(main_df)

st.caption("Final Project Nadia Putri Natali Lubis")
