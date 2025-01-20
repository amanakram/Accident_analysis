import requests
import pandas as pd
import json
from io import StringIO
API_URL="https://api.data.gov.in/resource/2297dfd8-2ba7-49a6-b53f-8796568d4753?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=csv"
API_KEY="579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
response = requests.get(API_URL, params={ "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b": API_KEY})
print("Response Status Code:", response.status_code)
if response.status_code == 200:
    print("Response Text Preview:")
    print(response.text[:500])
api_url = "https://api.data.gov.in/resource/2297dfd8-2ba7-49a6-b53f-8796568d4753?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=csv"
try:
    # Fetch the data from the API
    response = requests.get(api_url)
    
    # Check the status of the response
    if response.status_code == 200:
        print("Data fetched successfully!")
        
        # Print a preview of the raw CSV text
        print("Raw Data Preview:")
        print(response.text[:500])  # Display the first 500 characters of the response
        
        # Load the data into a pandas DataFrame
        data = pd.read_csv(StringIO(response.text))
        
        # Display the first few rows of the DataFrame
        print("\nDataFrame Preview:")
        print(data.head())
        
        # Save the data to a local CSV file
        csv_file_name = "Speed_Accidents_2008_2016.csv"
        data.to_csv(csv_file_name, index=False)
        print(f"\nData saved to {csv_file_name}")
    else:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
except Exception as e:
    print("An error occurred:", str(e))
import matplotlib.pyplot as plt
import seaborn as sns
# Load the saved CSV file
data = pd.read_csv("Speed_Accidents_2008_2016.csv")
# Check for missing values
print("\nMissing Values:")
print(data.isnull().sum())
import plotly.express as px

# Total accidents per state/UT in 2016
total_2016 = data[['States/UTs', '2016']].sort_values(by='2016', ascending=False)

# Plot: Top 10 states with most accidents in 2016
top_10_2016 = total_2016.head(10)

fig = px.bar(
    top_10_2016,
    x='2016',
    y='States/UTs',
    color='States/UTs',  # Assign color for better distinction
    orientation='h',     # Horizontal bar plot
    title="Top 10 States/UTs with Most Accidents in 2016",
    labels={'2016': 'Number of Accidents', 'States/UTs': 'States/UTs'},
    color_discrete_sequence=px.colors.sequential.Viridis
)

fig.update_layout(
    xaxis_title="Number of Accidents",
    yaxis_title="States/UTs",
    showlegend=False  # Remove legend if not needed
)
fig.show()

import plotly.express as px
import plotly.graph_objects as go

# 1. Total accidents per year (2008-2016)
yearly_totals = data.drop('States/UTs', axis=1).sum()

# Plot using plotly.graph_objects
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=yearly_totals.index,
    y=yearly_totals.values,
    mode='lines+markers',
    name='Accidents',
    line=dict(color='blue'),
    marker=dict(size=8)
))

# Update layout
fig.update_layout(
    title="Total Accidents Across All States/UTs (2008-2016)",
    xaxis_title="Year",
    yaxis_title="Number of Accidents",
    template='plotly_dark',  # Optional: choose a layout style
    xaxis=dict(tickmode='array'),
    yaxis=dict(tickformat=",.0f"),
    showlegend=False
)

# Show the plot
fig.show()
# 2. Trends for Top 5 States/UTs
top_5_states = total_2016.head(5)['States/UTs'].values
data_top_5 = data[data['States/UTs'].isin(top_5_states)]
data_top_5_melted = data_top_5.melt(id_vars='States/UTs', var_name='Year', value_name='Accidents')

# Plot using plotly.express
fig = px.line(
    data_top_5_melted, 
    x='Year', 
    y='Accidents', 
    color='States/UTs',
    markers=True,  # Add markers to the line plot
    title="Accident Trends (2008-2016) for Top 5 States/UTs",
    labels={"Year": "Year", "Accidents": "Number of Accidents"},
    template='plotly_dark'  # Optional: to choose a dark layout
)

# Show the plot
fig.show()

# 3. Correlation Analysis (Optional)
correlation = data.drop('States/UTs', axis=1).corr()

# Create a heatmap using plotly.graph_objects
fig = go.Figure(data=go.Heatmap(
    z=correlation.values, 
    x=correlation.columns, 
    y=correlation.columns,
    colorscale='RdBu',  # Optional color scale
    colorbar=dict(title="Correlation"),
    zmin=-1, zmax=1  # Set the color scale to range from -1 to 1
))

# Update the layout for better readability
fig.update_layout(
    title="Correlation Between Years",
    xaxis_title="Year",
    yaxis_title="Year",
    template='plotly_dark'  # Optional dark theme, can remove if not needed
)

# Show the plot
fig.show()
