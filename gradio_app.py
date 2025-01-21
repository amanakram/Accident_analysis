import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
import json
from io import StringIO
import os

API_URL="https://api.data.gov.in/resource/2297dfd8-2ba7-49a6-b53f-8796568d4753?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=csv"
API_KEY="579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
response = requests.get(API_URL, params={ "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b": API_KEY})



def load_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = pd.read_csv(StringIO(response.text))
            highlights = {
                "Total States/UTs": data['States/UTs'].nunique(),
                "Total Records": len(data),
                "Time Period": f"{data.columns[1]} to {data.columns[-1]}"
            }
            return data, highlights
        else:
            raise ValueError(f"Error fetching data: {response.status_code}")
    except Exception as e:
        return None, {"error": str(e)}

# Predefined analysis functions
def plot_total_accidents(data):
    yearly_totals = data.drop('States/UTs', axis=1).sum()
    fig = px.line(
        x=yearly_totals.index,
        y=yearly_totals.values,
        labels={'x': 'Year', 'y': 'Total Accidents'},
        title="Total Accidents Across All States/UTs (2008-2016)"
    )
    return fig

def plot_top5_trends(data):
    total_2016 = data[['States/UTs', '2016']].sort_values(by='2016', ascending=False)
    top_5_states = total_2016.head(5)['States/UTs'].values
    data_top_5 = data[data['States/UTs'].isin(top_5_states)]
    data_top_5_melted = data_top_5.melt(id_vars='States/UTs', var_name='Year', value_name='Accidents')
    fig = px.scatter(
        data_top_5_melted,
        x='Year',
        y='Accidents',
        color='States/UTs',
        title="Accident Trends (2008-2016) for Top 5 States/UTs",
        template="plotly_dark",
        range_y=[0, data_top_5_melted['Accidents'].max() * 1.1]
    )
    return fig

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

# Analysis selector
def analysis(analysis_type):
    data, highlights = load_data()
    if "error" in highlights:
        return f"Error: {highlights['error']}"
    if analysis_type == "Total Accidents per Year":
        return plot_total_accidents(data)
    elif analysis_type == "Top 5 States/UTs Trends":
        return plot_top5_trends(data)
    elif analysis_type == "Correlation Analysis":
        return plot_correlation(data)

# Custom plot builder
def build_custom_plot(x_axis, y_axis, plot_type):
    data, _ = load_data()

    # Handle "All Years" and "All States" scenarios
    if x_axis == "All Years" and y_axis == "All States":
        melted_data = data.melt(id_vars="States/UTs", var_name="Year", value_name="Accidents")
        if plot_type == "Bar Plot":
            fig = px.bar(
                melted_data,
                x="Year",
                y="Accidents",
                color="States/UTs",
                title="Accidents Over All States and Years",
                template="plotly_dark"
            )
        else:
            fig = px.scatter(
                melted_data,
                x="Year",
                y="Accidents",
                color="States/UTs",
                title="Accidents Over All States and Years",
                template="plotly_dark"
            )
        return fig

    if x_axis == "All Years":
        melted_data = data.melt(id_vars="States/UTs", var_name="Year", value_name="Accidents")
        melted_data = melted_data[melted_data['States/UTs'] == y_axis]
        if plot_type == "Bar Plot":
            fig = px.bar(
                melted_data,
                x="Year",
                y="Accidents",
                title=f"Accidents for {y_axis} Over All Years",
                template="plotly_dark"
            )
        else:
            fig = px.scatter(
                melted_data,
                x="Year",
                y="Accidents",
                title=f"Accidents for {y_axis} Over All Years",
                template="plotly_dark"
            )
        return fig

    if y_axis == "All States":
        melted_data = data.melt(id_vars="States/UTs", var_name="Year", value_name="Accidents")
        melted_data = melted_data[melted_data['Year'] == x_axis]
        if plot_type == "Bar Plot":
            fig = px.bar(
                melted_data,
                x="States/UTs",
                y="Accidents",
                title=f"Accidents Across All States for {x_axis}",
                template="plotly_dark"
            )
        else:
            fig = px.scatter(
                melted_data,
                x="States/UTs",
                y="Accidents",
                title=f"Accidents Across All States for {x_axis}",
                template="plotly_dark"
            )
        return fig

    # Default plot
    if plot_type == "Bar Plot":
        fig = px.bar(
            data,
            x=x_axis,
            y=y_axis,
            title=f"Custom Plot: {y_axis} vs {x_axis}",
            template="plotly_dark"
        )
    else:
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            title=f"Custom Plot: {y_axis} vs {x_axis}",
            template="plotly_dark"
        )
    return fig

# Dropdown choices
def get_combined_choices():
    data, _ = load_data()
    years = data.columns[1:].tolist()
    states = data["States/UTs"].unique().tolist()
    return ["All Years", "All States"] + years + states

# Main Gradio interface
with gr.Blocks(title="Accident Analysis App") as app:
    gr.Markdown("## 🚗 Welcome to the Accident Analysis App 🚦")
    gr.Markdown("Analyze road accident data interactively using this app.")

    if requests.get(API_URL).status_code == 200:
        gr.Markdown("Data successfully fetched from API!")

    # Predefined plots
    insights_output = gr.HTML()
    analysis_selector = gr.Radio(
        label="Choose Analysis Type:",
        choices=["Total Accidents per Year", "Top 5 States/UTs Trends", "Correlation Analysis"],
        value="Total Accidents per Year"
    )
    analysis_output = gr.Plot()
    analysis_selector.change(analysis, inputs=[analysis_selector], outputs=analysis_output)

    # Custom plot section
    gr.Markdown("### Build Your Own Plot 🎨")
    combined_choices = get_combined_choices()

    x_axis_input = gr.Dropdown(label="X-Axis", choices=combined_choices, value="All Years")
    y_axis_input = gr.Dropdown(label="Y-Axis", choices=combined_choices, value="All States")
    plot_type_input = gr.Radio(label="Plot Type", choices=["Bar Plot", "Scatter Plot"], value="Bar Plot")
    custom_plot_output = gr.Plot()

    custom_plot_button = gr.Button("Generate Custom Plot")
    custom_plot_button.click(
        build_custom_plot,
        inputs=[x_axis_input, y_axis_input, plot_type_input],
        outputs=custom_plot_output
    )
app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))


