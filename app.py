import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
from vega_datasets import data
from state_Codes import us_state_to_abbrev

df_1br_city = pd.read_csv('Datasets/City/oneBedRoom_City.csv')
df_2br_city = pd.read_csv('Datasets/City/TwoBedRoom_City.csv')
df_3br_city = pd.read_csv('Datasets/City/ThreeBedRoom_City.csv')
df_4br_city = pd.read_csv('Datasets/City/FourBedRoom_City.csv')
df_5br_city = pd.read_csv('Datasets/City/fivePlusBedRoom_City.csv')
df_single_home_city = pd.read_csv('Datasets/City/singleFamily_City.csv')
df_all_homes_city = pd.read_csv('Datasets/City/AllHomes_City.csv')

df = df_all_homes_city

st.subheader('Line Chart for Median Sales Prices of Houses')
st.write("This visulaization provides information on Sale prices for different type of homes in many cities of United States over the past 20 years.")

selected_home_type = st.selectbox('Select Home Type', ('All Homes', 'Single Family Homes', 'One Bed Room Homes', 'Two Bed Room Homes',
                                                       'Three Bed Room Homes', 'Four Bed Room Homes', 'Five Plus Bed Room Homes'))

if selected_home_type == 'Single Family Homes':
    df = df_single_home_city
elif selected_home_type == 'One Bed Room Homes':
    df = df_1br_city
elif selected_home_type == 'Two Bed Room Homes':
    df = df_2br_city
elif selected_home_type == 'Three Bed Room Homes':
    df = df_3br_city
elif selected_home_type == 'Four Bed Room Homes':
    df = df_4br_city
elif selected_home_type == 'Five Plus Bed Room Homes':
    df = df_5br_city

df2 = df.drop(['RegionID', 'SizeRank', 'RegionType', 'StateName'], axis=1)
df2 = df2.set_index('RegionName')


cities_list = df['RegionName'].tolist()
cities_list.remove("United States")

city_list = []
for term in cities_list[1:]:
    city_list.append(term.split(', '))

city_state_dict = dict(city_list)
cities_list = list(city_state_dict.keys())
states_list = list(set(city_state_dict.values()))

# Creating a city list based on a state chosen


def get_city_list(state):
    spec_city_list = []
    for element in city_state_dict:
        if city_state_dict[element] == state:
            spec_city_list.append(element)

    return spec_city_list


col1, col2 = st.columns(2)
selected_state = col1.selectbox('Select First State:', states_list,index=1)
list_cities = get_city_list(selected_state)
selected_city = col2.multiselect('Select Cities in the first state:', list_cities, list_cities[:2])

col_state2, col_city2 = st.columns(2)
selected_state2 = col_state2.selectbox('Select Second State:', states_list)
list_cities2 = get_city_list(selected_state2)
selected_city2 = col_city2.multiselect('Select Cities in second state:', list_cities2, list_cities2[:2])

df2 = df2.transpose()
df2.reset_index(inplace=True)
df2.rename(columns={'index': 'Date'}, inplace=True)

# st.write(df2)

city_data = [(city + ', ' + selected_state) for city in selected_city]
city_data = city_data + [(city + ', ' + selected_state2) for city in selected_city2]
line_chart = alt.Chart(df2).mark_line().transform_fold(city_data).encode(x='Date:T',
                                                                         y=alt.Y(
                                                                             'value:Q', title='Sales Prices'),
                                                                         color='key:N').properties(
    width=700,
    height=500
).interactive()
st.write(line_chart)

# Choropleth Map
st.subheader('Choropleth Map of Zillow Housing Prices in the US')
st.write("This visulaization gives insights into housing prices in different states of United States over the past 10 years. You can select any year or month from the below dropdown to view the average housing prices.")

df_all_homes_states = pd.read_csv("Datasets/States/sale_prices_state.csv")
df_all_homes_states['StateName'] = df_all_homes_states['RegionName'].map(
    us_state_to_abbrev)

state_codes = [1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
               29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 55, 56]
state_abv = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
             'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

dict = {state_abv[i]: state_codes[i] for i in range(len(state_abv))}
df_all_homes_states['id'] = df_all_homes_states['StateName'].map(dict)

df_new = df_all_homes_states.drop(['SizeRank', 'RegionType'], axis=1)

date_values = list(df_new[1:].columns.values)

# Creating a date list based on a year chosen


def return_date_list(year):
    date_list = []
    for date in date_values:
        if str(year) in date:
            date_list.append(date)

    return date_list


col_year, col_month = st.columns(2)
year_selection = col_year.selectbox('Select Year:', [
                                    '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013'])

if year_selection:
    list_month_dates = return_date_list(year_selection)
    month_selection = col_month.selectbox(
        'Select Month:', list_month_dates)
    df_final = round(df_new.groupby(['StateName', 'id', 'RegionName'])[
                     month_selection].mean(), 2).reset_index()

label = 'Housing Prices ($)'
df_final.rename(columns={month_selection: label,
                'StateName': 'State Name'}, inplace=True)
# st.write(df_final)

states = alt.topo_feature(data.us_10m.url, 'states')

choropleth_map = alt.Chart(states).mark_geoshape().encode(
    color=label + ':Q',
    tooltip=['RegionName:O', label + ':Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_final, 'id', ['RegionName', label])
).project(
    type='albersUsa'
).properties(
    width=750,
    height=600
)

st.write(choropleth_map)

# Bar Chart for appreciation

st.subheader("Bar Chart for Percentage appreciation in different cities")
st.write("This bar Chart shows the percentage of appreciation of Home values across differnt cities of the United states in the past 10 years")


col_state_bar, col_year_bar = st.columns(2)
selected_state_bar = col_state_bar.selectbox('Select State: ', states_list)
selected_year_bar = col_year_bar.selectbox('Select Year :', [
                                    '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013'])


list_cities_bar = get_city_list(selected_state_bar)

df_tst = df_all_homes_city.iloc[1:, :]

df_tst = df_tst.drop(
    ['RegionID', 'SizeRank', 'RegionType'], axis=1)
list_month_dates = return_date_list(int(selected_year_bar))
list_month_dates_last_year = return_date_list(int(selected_year_bar)-1)
df_curent_year = round(df_tst.groupby(['RegionName'])[
                list_month_dates].mean(), 2).reset_index()
df_last_year = round(df_tst.groupby(['RegionName'])[
                list_month_dates_last_year].mean(), 2).reset_index()
df_regions = df_tst["RegionName"]
df_regions = pd.DataFrame(df_regions)
df_regions.insert(0,"StateName",df_tst["StateName"])
df_curent_year = df_curent_year.loc[:, df_curent_year.columns !=
                      'RegionName'].mean(axis=1, skipna=True)
df_last_year = df_last_year.loc[:, df_last_year.columns !=
                      'RegionName'].mean(axis=1, skipna=True)

df_regions['House Value Mean current year'] = df_curent_year
df_regions['House Value Mean last year'] = df_last_year
df_regions = df_regions.dropna()

list_percentages  = []

def calculate_percent(row):
    percentage_change = (int(
        row['House Value Mean current year'])/int(row['House Value Mean last year'])-1)*100
    list_percentages.append(percentage_change)
    #print(row['percent change'])

df_final_percent = pd.DataFrame()
df_final_percent['RegionName','percent change'] = []


# st.write(df_final_percent)
df_regions.apply(calculate_percent, axis=1)
# df_regions.apply(filter_selected_state_cities,axis=1)
df_regions.insert(4,"percentage change",list_percentages)

city_data_bar = [(city + ', ' + selected_state_bar) for city in list_cities_bar]
#st.write(df_regions)


df_selected = df_regions[df_regions['StateName'] == selected_state_bar]


bar_chart = alt.Chart(df_selected).mark_bar().encode(
    x='percentage change:Q',
    y="RegionName:O"
).properties(height=500)

st.write(bar_chart)



