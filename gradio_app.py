import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
def load_data(file):
    data = pd.read_csv(file)
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
def analysis(file, analysis_type):
    data, highlights = load_data(file)
    
    if analysis_type == "Total Accidents per Year":
        return plot_total_accidents(data)
    elif analysis_type == "Top 5 States/UTs Trends":
        return plot_top5_trends(data)
    elif analysis_type == "Correlation Analysis":
        return plot_correlation(data)

# Main interface for displaying highlights
def main_interface(file):
    data, highlights = load_data(file)

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
    gr.Markdown("Upload your CSV file to explore the data interactively.")
    
    # File input and interactive analysis
    file_input = gr.File(label="Upload CSV File")
    insights_output = gr.HTML()  # Display key insights
    analysis_selector = gr.Radio(
        label="Choose Analysis Type:",
        choices=["Total Accidents per Year", "Top 5 States/UTs Trends", "Correlation Analysis"],
        value="Total Accidents per Year"  # Default to the first option
    )
    analysis_output = gr.Plot()
    
    # Bind actions
    file_input.change(main_interface, inputs=file_input, outputs=insights_output)
    analysis_selector.change(analysis, inputs=[file_input, analysis_selector], outputs=analysis_output)

#app.launch()
app.launch(server_name="0.0.0.0", server_port=8080)

