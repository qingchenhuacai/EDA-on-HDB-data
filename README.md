## EDA-on-HDB-data
This project aims to analyze the housing market in Singapore using HDB (Housing and Development Board) resale and rental data. It includes exploratory data analysis (EDA) and visualization of various factors affecting housing prices.

## Introduction
The project consists of three main components:

EDA_WEB.py: This Python script contains functions for data visualization using Streamlit and Folium libraries. It enables users to explore the HDB resale and rental data interactively through a web application.
data_process.py: This module provides functions for data preprocessing, including reading data from CSV files, subsampling, statistical computations, and adding geographical information such as addresses and distances to MRT (Mass Rapid Transit) stations.
generate_dataframe.py: This script reads the original HDB resale and rental data files, preprocesses the data, and generates cleaned CSV files ready for analysis.

## Requirements
Python 3.x
Streamlit
Pandas
Folium
Geopy
Seaborn
Matplotlib
Numpy

## Usage
Run the Streamlit web application:
streamlit run EDA_WEB.py
