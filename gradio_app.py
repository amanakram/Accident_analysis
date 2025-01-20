import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
import json
from io import StringIO
API_URL="https://api.data.gov.in/resource/2297dfd8-2ba7-49a6-b53f-8796568d4753?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=csv"
API_KEY="579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
response = requests.get(API_URL, params={ "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b": API_KEY})



# Load data
def load_data():
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
        else:
            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    except Exception as e:
        gr.Markdownint("Oops, Error reading the data, please try after sometime...")
    #data = pd.read_csv(file)
    highlights = {
        "Total States/UTs": data['States/UTs'].nunique(),
        "Total Records": len(data),
        "Time Period": f"{data.columns[1]} to {data.columns[-1]}"
    }
    return data, highlights

# Plot: Total accidents per year
def plot_total_accidents(data):
    yearly_totals = data.drop('States/UTs', axis=1).sum()
    fig = px.line(
        x=yearly_totals.index,
        y=yearly_totals.values,
        labels={'x': 'Year', 'y': 'Total Accidents'},
        title="Total Accidents Across All States/UTs (2008-2016)"
    )
    return fig

# Plot: Trends for top 5 states/UTs (scatter plot)
def plot_top5_trends(data):
    # Sort and filter top 5 states based on the 2016 accident data
    total_2016 = data[['States/UTs', '2016']].sort_values(by='2016', ascending=False)
    top_5_states = total_2016.head(5)['States/UTs'].values
    data_top_5 = data[data['States/UTs'].isin(top_5_states)]
    
    # Melt the data to prepare it for the scatter plot
    data_top_5_melted = data_top_5.melt(id_vars='States/UTs', var_name='Year', value_name='Accidents')
    
    # Plotting the scatter plot
    fig = px.scatter(
        data_top_5_melted,
        x='Year',
        y='Accidents',
        color='States/UTs',
        title="Accident Trends (2008-2016) for Top 5 States/UTs",
        template="plotly_dark",  # You can change the template
        range_y=[0, data_top_5_melted['Accidents'].max()*1.1]  # Sets Y-axis range to ensure better visibility of data
    )
    return fig

# Plot: Correlation heatmap
def plot_correlation(data):
    correlation = data.drop('States/UTs', axis=1).corr()
    fig = go.Figure(data=go.Heatmap(
        z=correlation.values,
        x=correlation.columns,
        y=correlation.columns,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        colorbar=dict(title="Correlation")
    ))
    fig.update_layout(
        title="Correlation Between Years",
        template="plotly_dark"
    )
    return fig

# Combine the analysis options
def analysis( analysis_type):
    data, highlights = load_data()
    
    if analysis_type == "Total Accidents per Year":
        return plot_total_accidents(data)
    elif analysis_type == "Top 5 States/UTs Trends":
        return plot_top5_trends(data)
    elif analysis_type == "Correlation Analysis":
        return plot_correlation(data)

# Main interface for displaying highlights
def main_interface():
    data, highlights = load_data()

    # Simple key insights with no background color
    insights = f"""
        <div style="font-size: 18px; padding: 15px; line-height: 1.5; color: black; border-radius: 10px;">
            <h4>📊 Key Insights:</h4>
            <ul>
                <li><b>Total States/UTs:</b> {highlights['Total States/UTs']}</li>
                <li><b>Total Records:</b> {highlights['Total Records']}</li>
                <li><b>Time Period:</b> {highlights['Time Period']}</li>
            </ul>
        </div>
    """
    return insights

# Launch Gradio app
with gr.Blocks(title="Accident Analysis App") as app:
    gr.Markdown("## 🚗 Welcome to the Accident Analysis App 🚦")
    #gr.Markdown("Upload your CSV file to explore the data interactively.")
    if response.status_code == 200:
        gr.Markdown("Data is successfully fetched from API")
    # File input and interactive analysis
    

    #file_input = gr.File(label="Upload CSV File")
    insights_output = gr.HTML()  # Display key insights
    analysis_selector = gr.Radio(
        label="Choose Analysis Type:",
        choices=["Total Accidents per Year", "Top 5 States/UTs Trends", "Correlation Analysis"],
        value="Total Accidents per Year"  # Default to the first option
    )
    analysis_output = gr.Plot()
    
    # Bind actions
    # file_input.change(main_interface, inputs=file_input, outputs=insights_output)
    analysis_selector.change(analysis, inputs=[analysis_selector], outputs=analysis_output)

#app.launch()
# app.launch(server_name="0.0.0.0", server_port=8080)
app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))


