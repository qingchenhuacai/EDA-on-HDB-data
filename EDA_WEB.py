import streamlit as st
import pandas as pd
import data_process as datap
import folium
from geopy.geocoders import Nominatim
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def filter_data(df, selected_year):
    if selected_year:
        df = df[df['year'].isin(selected_year)]
    return df



def show_map_with_mrt(df1, df2):
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=11)

    
    marker_cluster_hdb = MarkerCluster(
        name='HDB',
        icon_create_function=lambda cluster: folium.DivIcon(
            html=f"<div>Avg Price: {np.mean([child['price_per_sqm'] for child in cluster['child_markers']]):.2f} SGD</div>"
        )
    ).add_to(m)    
    marker_cluster_mrt = MarkerCluster(name='MRT Station').add_to(m)


    # Add HDB data to map
    for idx, row in df1.iterrows():
        if not pd.isnull(row['lat']) and not pd.isnull(row['lng']):
            popup_text = f"{row['street_name']} Block {row['block']}, Price per sqm: {row['price_per_sqm']} SGD"
            folium.Marker(
                location=[row['lat'], row['lng']],
                popup=popup_text,
                icon=folium.Icon(color='blue', icon='fa fa-home')
            ).add_to(marker_cluster_hdb)


    # Add MRT data to map
    for idx, row in df2.iterrows():
        if not pd.isnull(row['lat']) and not pd.isnull(row['lng']):
            popup_text = f"{row['station_name']}"
            folium.Marker(location=[row['lat'], row['lng']],
                          popup=popup_text,
                          icon=folium.Icon(color='red', icon='subway')).add_to(marker_cluster_mrt)

    folium.LayerControl().add_to(m)

    folium_static(m)


###############################################################################################################
#method for figues
def scatter_plot(df, x_col, y_col, x_label, y_label):
    fig, ax = plt.subplots(figsize=(15, 6))
    df = df.sort_values(by=x_col)
    sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45) 
    return fig

def line_plot(df, x_col, y_col, x_label, y_label):
    fig, ax = plt.subplots(figsize=(15, 6))
    df = df.sort_values(by=x_col)
    sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    return fig

def box_plot(df, x_col, y_col, x_label, y_label):
    fig, ax = plt.subplots(figsize=(15, 6))
    df = df.sort_values(by=x_col)
    sns.boxplot(data=df, x=x_col, y=y_col, ax=ax)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    
    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df, x_col, y_col)
    ax.plot([], [], label=f'{max_label} Has Highest Avg Price: {max_value:.2f} SGD', marker='None', markersize=5)
    ax.plot([], [], label=f'{min_label} Has Lowest Avg Price: {min_value:.2f} SGD', marker='None', markersize=5)
    legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True, ncol=2)
    for line in legend.get_lines():
        line.set_visible(False)

    return fig

def bar_plot(df, x_col, y_col, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(15, 6))
    df = df.sort_values(by=x_col)
    sns.barplot(data=df, x=x_col, y=y_col, ci=None, ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df, x_col, y_col)
    ax.plot([], [], label=f'Highest Avg Price: {max_value:.2f} SGD', color='blue', marker='o', markersize=5)
    ax.plot([], [], label=f'Lowest Avg Price: {min_value:.2f} SGD', color='orange', marker='o', markersize=5)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), fancybox=True, shadow=True, ncol=2)

    return fig

#####################################################################################################################
#methods of all Pages
    
def show_univariate_analysis(df1,df2):
    st.markdown("<h1 style='color: black; font-size: 24px'>Relationship Between Price and Various Factors</h1>", unsafe_allow_html=True)

    selected_year = st.multiselect("CHOOSE YEARS", options=sorted(df1['year'].unique()), default=1990)
    df_filtered = filter_data(df1, selected_year)
    df_filtered_rent = filter_data(df2, selected_year)

    st.markdown("<h2 style='color: black; font-size: 20px'>Resale Price per Square Meter vs. Flat Type</h2>", unsafe_allow_html=True)
    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df_filtered, 'flat_type', 'price_per_sqm')
    st.write(f"Highest Avg Price Flat Type: {max_label} with {max_value:.2f} SGD")
    st.write(f"Lowest Avg Price Flat Type: {min_label} with {min_value:.2f} SGD")
    box_fig_flattype = box_plot(df_filtered, 'flat_type', 'price_per_sqm', 'Flat Type', 'Price per Sqm')
    st.pyplot(box_fig_flattype)
    st.markdown("<h2 style='color: black; font-size: 20px'>Monthly Rental Price vs. Flat Type</h2>", unsafe_allow_html=True)
    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df_filtered_rent, 'flat_type', 'monthly_rent')
    st.write(f"Highest Avg Price Flat Type: {max_label} with {max_value:.2f} SGD")
    st.write(f"Lowest Avg Price Flat Type: {min_label} with {min_value:.2f} SGD")
    box_fig_flattype = box_plot(df_filtered_rent, 'flat_type', 'monthly_rent', 'Flat Type', 'Monthly Rent Price')
    st.pyplot(box_fig_flattype)


    st.markdown("<h2 style='color: black; font-size: 20px'>Resale Price per Square Meter vs. Remaining Lease</h2>", unsafe_allow_html=True)
    correlation_coefficient = df_filtered['remaining_lease'].corr(df_filtered['price_per_sqm'])
    st.write(f"Correlation Coefficient: {correlation_coefficient:.2f}")
    scatter_plot_remaiinlease = scatter_plot(df_filtered, 'remaining_lease', 'price_per_sqm', 'Remaining Lease', 'Price per Sqm')
    st.pyplot(scatter_plot_remaiinlease)

    st.markdown("<h2 style='color: black; font-size: 20px'>Resale Price per Square Meter vs. Town</h2>", unsafe_allow_html=True)
    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df_filtered, 'town', 'price_per_sqm')
    st.write(f"Highest Avg Price Town: {max_label} with {max_value:.2f} SGD")
    st.write(f"Lowest Avg Price Town: {min_label} with {min_value:.2f} SGD")
    box_fig_town = box_plot(df_filtered, 'town', 'price_per_sqm', 'Town', 'Price per Sqm')
    st.pyplot(box_fig_town)
    st.markdown("<h2 style='color: black; font-size: 20px'>Monthly Rental Price vs. Town</h2>", unsafe_allow_html=True)
    max_label, min_label, max_value, min_value = datap.max_min_avg_price(df_filtered_rent, 'town', 'monthly_rent')
    st.write(f"Highest Avg Price Town: {max_label} with {max_value:.2f} SGD")
    st.write(f"Lowest Avg Price Town: {min_label} with {min_value:.2f} SGD")
    box_fig_town = box_plot(df_filtered_rent, 'town', 'monthly_rent', 'Town', 'Monthly Rent Price')
    st.pyplot(box_fig_town)

    sns.set_style('ticks')



def show_popular_neighborhood(df1,df2):
    st.markdown("<h1 style='color: black; font-size: 24px'>The Town With the Highest HDB Transactions</h1>", unsafe_allow_html=True)
    st.subheader('Popular Neighborhood Map')

    selected_year = st.multiselect("CHOOSE YEARS", options=sorted(df1['year'].unique()), default=1990)
    df_filtered = filter_data(df1, selected_year)

    popular_neighborhood = df_filtered['town'].value_counts().idxmax()
    st.write(f"The most popular town is {popular_neighborhood}")

    df_filtered = df_filtered[df_filtered['town'] == popular_neighborhood]
    df_filtered_sampled = datap.data_subsample(df_filtered)
    show_map_with_mrt(df_filtered_sampled,df2)

def show_price_trend(df1,df2):
    st.markdown("<h1 style='color: black; font-size: 24px'>Price Trend</h1>", unsafe_allow_html=True)
    
    towns = df1['town'].unique().tolist()
    selected_town = st.selectbox("Select a town", towns)
    df_filtered1 = df1[df1['town'] == selected_town]
    st.markdown("<h2 style='color: black; font-size: 20px'>Resale Price Trend</h2>", unsafe_allow_html=True)
    monthly_trend1 = df_filtered1.groupby('year')['resale_price'].mean()
    st.line_chart(monthly_trend1)
    #line_fig_years = line_plot(monthly_trend1, 'year', 'price_per_sqm', 'Year', 'Price per Sqm')
    #st.pyplot(line_fig_years)   

    #selected_year = st.multiselect("CHOOSE YEARS", options=sorted(df1['year'].unique()), default=1990)
    #df_filtered1 = filter_data(df1, selected_year)
    
    #st.subheader('Resale Price Trend Over Different Months:')
    #monthly_trend1 = df_filtered1.groupby('month')['resale_price'].mean()
    #st.line_chart(monthly_trend1)
    #line_fig_months = line_plot(monthly_trend1, 'month', 'price_per_sqm', 'Month', 'Price per Sqm')
    #st.pyplot(line_fig_months)   

    #selected_year = st.multiselect("CHOOSE YEARS", options=sorted(df2['year'].unique()), default=2021)
    #df_filtered2 = filter_data(df2, selected_year)

    df_filtered2 = df2[df2['town'] == selected_town]
    st.markdown("<h2 style='color: black; font-size: 20px'>Rent Price Trend</h2>", unsafe_allow_html=True)
    monthly_trend2 = df_filtered2.groupby('rent_approval_date')['monthly_rent'].mean()
    st.line_chart(monthly_trend2)
    #line_fig_months_rent = line_plot(monthly_trend2, 'month', 'monthly_rent', 'Month', 'Monthly Rental Price')
    #st.pyplot(line_fig_months_rent) 


def show_MRT_distance(df1,df2):
    st.markdown("<h1 style='color: black; font-size: 24px'>Price and Distance to MRT</h1>", unsafe_allow_html=True)
    towns = df1['town'].unique().tolist()
    selected_town = st.selectbox("Select a town", towns)
    selected_year = st.multiselect("CHOOSE YEARS", options=sorted(df1['year'].unique()), default=2000)
    df1 = filter_data(df1, selected_year)
    df_filtered = df1[df1['town'] == selected_town]

    df_filtered = df_filtered[df_filtered['mrt_dist'] != float('inf')]

    corr_coefficient = df_filtered['price_per_sqm'].corr(df_filtered['mrt_dist'])
    st.write(f"Correlation coefficient between price and distance to MRT in {selected_town} is {corr_coefficient:.2f}")

    fig = scatter_plot(df_filtered, 'price_per_sqm', 'mrt_dist', 'Price Per Sqm', 'MRT Distance')
    st.pyplot(fig)
    
    df_filtered_sampled = datap.data_subsample(df_filtered)
    show_map_with_mrt(df_filtered_sampled,df2)

######################################################################################################################
def main():

    # set font size
    st.markdown("<h1 style='text-align: center; color: black; font-size: 26px'>\
                Exploring Singapore HDB Price Data !</h1>", unsafe_allow_html=True)
    #st.markdown("<h2 style='color: black; font-size: 20px'>Subheader</h2>", unsafe_allow_html=True)
    #st.markdown("<p style='font-size: 18px;'>Normal text</p>", unsafe_allow_html=True)

    # load data
    df_resale = datap.get_hdb_resale_df()
    df_rent = datap.get_hdb_rent_df()
    df_mrt = datap.get_mrt_location()
    df_resale_mrt = datap.get_hdb_resale_mrt_df()

    #choose PAGESs
    selected_page = st.sidebar.radio("CHOOSE A PAGE", ["Univariate Analysis","Price Trend",\
                                                       "Popular Neighborhood", "Relationship between MRT Distance and Price"])
 
    if selected_page == "Univariate Analysis":
        show_univariate_analysis(df_resale,df_rent)
    elif selected_page == "Popular Neighborhood":
        show_popular_neighborhood(df_resale,df_mrt)
    elif selected_page == "Price Trend":
        show_price_trend(df_resale,df_rent)
    elif selected_page == "Relationship between MRT Distance and Price":
        show_MRT_distance(df_resale_mrt,df_mrt)
        
if __name__ == "__main__":
    main()