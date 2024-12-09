import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
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

def create_monthly_spring_df(df):
    spring_df = df[df.season ==1][["instant","dteday","casual","registered","cnt"]] 

    monthly_spring_df = spring_df.resample(rule='M', on='dteday').agg({
    "cnt" : "sum"
    })

    monthly_spring_df = monthly_spring_df.reset_index()
    monthly_spring_df['YearMonth'] = monthly_spring_df['dteday'].dt.strftime('%Y-%B')

    monthly_spring_df = monthly_spring_df[monthly_spring_df['cnt'] > 0]

    monthly_spring_df['Month_num'] = monthly_spring_df['dteday'].dt.month + 12 * (monthly_spring_df['dteday'].dt.year - monthly_spring_df['dteday'].dt.year.min())
    slope, intercept, r_value, p_value, std_err = linregress(monthly_spring_df['Month_num'], monthly_spring_df['cnt'])
    monthly_spring_df['Regression'] = slope * monthly_spring_df['Month_num'] + intercept

    return monthly_spring_df

def create_monthly_summer_df(df):
    summer_df = df[df.season ==2][["instant","dteday","casual","registered","cnt"]] 

    monthly_summer_df = summer_df.resample(rule='M', on='dteday').agg({
    "cnt" : "sum"
    })

    monthly_summer_df = monthly_summer_df.reset_index()
    monthly_summer_df['YearMonth'] = monthly_summer_df['dteday'].dt.strftime('%Y-%B')

    monthly_summer_df = monthly_summer_df[monthly_summer_df['cnt'] > 0]


    monthly_summer_df['Month_num'] = monthly_summer_df['dteday'].dt.month + 12 * (monthly_summer_df['dteday'].dt.year - monthly_summer_df['dteday'].dt.year.min())
    slope, intercept, r_value, p_value, std_err = linregress(monthly_summer_df['Month_num'], monthly_summer_df['cnt'])
    monthly_summer_df['Regression'] = slope * monthly_summer_df['Month_num'] + intercept

    return monthly_summer_df


def create_monthly_fall_df(df):
    fall_df = df[df.season ==3][["instant","dteday","casual","registered","cnt"]] 

    monthly_fall_df = fall_df.resample(rule='M', on='dteday').agg({
    "cnt" : "sum"
    })

    monthly_fall_df = monthly_fall_df.reset_index()
    monthly_fall_df['YearMonth'] = monthly_fall_df['dteday'].dt.strftime('%Y-%B')

    monthly_fall_df = monthly_fall_df[monthly_fall_df['cnt'] > 0]


    monthly_fall_df['Month_num'] = monthly_fall_df['dteday'].dt.month + 12 * (monthly_fall_df['dteday'].dt.year - monthly_fall_df['dteday'].dt.year.min())
    slope, intercept, r_value, p_value, std_err = linregress(monthly_fall_df['Month_num'], monthly_fall_df['cnt'])
    monthly_fall_df['Regression'] = slope * monthly_fall_df['Month_num'] + intercept

    return monthly_fall_df


def create_monthly_winter_df(df):
    winter_df = df[df.season ==4][["instant","dteday","casual","registered","cnt"]] 

    monthly_winter_df = winter_df.resample(rule='M', on='dteday').agg({
    "cnt" : "sum"
    })

    monthly_winter_df = monthly_winter_df.reset_index()
    monthly_winter_df['YearMonth'] = monthly_winter_df['dteday'].dt.strftime('%Y-%B')

    monthly_winter_df = monthly_winter_df[monthly_winter_df['cnt'] > 0]


    monthly_winter_df['Month_num'] = monthly_winter_df['dteday'].dt.month + 12 * (monthly_winter_df['dteday'].dt.year - monthly_winter_df['dteday'].dt.year.min())
    slope, intercept, r_value, p_value, std_err = linregress(monthly_winter_df['Month_num'], monthly_winter_df['cnt'])
    monthly_winter_df['Regression'] = slope * monthly_winter_df['Month_num'] + intercept

    return monthly_winter_df

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


day_df = pd.read_csv("data/day.csv")

day_df["dteday"] = pd.to_datetime(day_df['dteday'])

day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)


min_date = day_df['dteday'].min()
max_date = day_df['dteday'].max()

with st.sidebar:
    # logo disini nnti
    st.image("data/bicycle.png",width=150)

    st.write("This is bike-sharing rent data from 2011 to 2012")

    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


main_df = day_df[(day_df["dteday"]>= str(start_date)) & (day_df["dteday"] <= str(end_date))]

rfm_df = create_rfm_df(main_df, day_df)

monthly_spring_df = create_monthly_spring_df(main_df)
monthly_summer_df = create_monthly_summer_df(main_df)
monthly_fall_df = create_monthly_fall_df(main_df)
monthly_winter_df = create_monthly_winter_df(main_df)


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

st.subheader('Monthly Bike-Rent by Season')

col3, col4 = st.columns(2)

col5, col6 = st.columns(2)

tab1, tab2, tab3, tab4 = st.tabs(["Spring", "Summer", "Fall", "Winter"])

# with tab1:
    # tab1.write("this is tab 1")
    # tab2.write("this is tab 2")

with tab1:
    fig = plt.figure(figsize=(10,5))
    plt.plot(monthly_spring_df["YearMonth"], monthly_spring_df["cnt"], marker='o', linewidth=2, color='#222f5b', label='Total Rentals')
    plt.plot(monthly_spring_df["YearMonth"], monthly_spring_df['Regression'], color='red', linestyle='--', label='Linear Regression')
    plt.title("Total Rent Bikes per Month in Spring")
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(visible=True)
    plt.show()
    st.pyplot(fig)

with tab2:
    fig = plt.figure(figsize=(10,5))
    plt.plot(monthly_summer_df["YearMonth"], monthly_summer_df["cnt"], marker='o', linewidth=2, color='#222f5b', label='Total Rentals')
    plt.plot(monthly_summer_df["YearMonth"], monthly_summer_df['Regression'], color='red', linestyle='--', label='Linear Regression')
    plt.title("Total Rent Bikes per Month in Summer")
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(visible=True)
    plt.show()
    st.pyplot(fig)

with tab3:
    fig = plt.figure(figsize=(10,5))
    plt.plot(monthly_fall_df["YearMonth"], monthly_fall_df["cnt"], marker='o', linewidth=2, color='#222f5b', label='Total Rentals')
    plt.plot(monthly_fall_df["YearMonth"], monthly_fall_df['Regression'], color='red', linestyle='--', label='Linear Regression')
    plt.title("Total Rent Bikes per Month in Fall")
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(visible=True)
    plt.show()
    st.pyplot(fig)

with tab4:
    fig = plt.figure(figsize=(10,5))
    plt.plot(monthly_winter_df["YearMonth"], monthly_winter_df["cnt"], marker='o', linewidth=2, color='#222f5b', label='Total Rentals')
    plt.plot(monthly_winter_df["YearMonth"], monthly_winter_df['Regression'], color='red', linestyle='--', label='Linear Regression')
    plt.title("Total Rent Bikes per Month in Winter")
    plt.xlabel("Month")
    plt.ylabel("Total Rentals")
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(visible=True)
    plt.show()
    st.pyplot(fig)

st.subheader("Bike Rentals on Holiday vs Non-Holiday")
relation_holidayvsnon = create_relation_holidayvsnon(main_df)

st.caption("Final Project Nadia Putri Natali Lubis")
