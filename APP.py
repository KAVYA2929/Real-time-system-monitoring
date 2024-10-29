import psutil
import GPUtil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)


# Function to get system metrics
def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    return cpu_percent, memory_info.percent, disk_usage.percent


# Function to get GPU metrics (if GPU is available)
def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            "id": gpu.id,
            "name": gpu.name,
            "load": gpu.load * 100,
            "memory_used": gpu.memoryUsed,
            "memory_total": gpu.memoryTotal,
            "temperature": gpu.temperature
        })
    return gpu_info


# Layout of the dashboard
app.layout = html.Div([
    html.H1("Real-Time System Monitoring", style={'textAlign': 'center'}),

    # Animated CPU Usage Graph
    dcc.Graph(id='cpu-graph', style={'height': '400px'}),

    # Animated Memory Usage Graph
    dcc.Graph(id='memory-graph', style={'height': '400px'}),

    # Animated Disk Usage Graph
    dcc.Graph(id='disk-graph', style={'height': '400px'}),

    # Animated GPU Usage Graph
    dcc.Graph(id='gpu-graph', style={'height': '400px'}),

    # Auto-refresh interval
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])


# Callback to update CPU usage graph
@app.callback(Output('cpu-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_cpu_graph(n):
    cpu_percent, _, _ = get_system_info()
    df = pd.DataFrame({
        'Time': [n],
        'CPU Usage (%)': [cpu_percent]
    })
    fig = px.line(df, x='Time', y='CPU Usage (%)', title='CPU Usage Over Time',
                  markers=True, line_shape='linear', color_discrete_sequence=['crimson'])
    fig.update_layout(xaxis_title='Time (s)', yaxis_title='CPU Usage (%)', transition_duration=500)
    return fig


# Callback to update Memory usage graph
@app.callback(Output('memory-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_memory_graph(n):
    _, memory_percent, _ = get_system_info()
    df = pd.DataFrame({
        'Time': [n],
        'Memory Usage (%)': [memory_percent]
    })
    fig = px.line(df, x='Time', y='Memory Usage (%)', title='Memory Usage Over Time',
                  markers=True, line_shape='linear', color_discrete_sequence=['blue'])
    fig.update_layout(xaxis_title='Time (s)', yaxis_title='Memory Usage (%)', transition_duration=500)
    return fig


# Callback to update Disk usage graph
@app.callback(Output('disk-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_disk_graph(n):
    _, _, disk_percent = get_system_info()
    df = pd.DataFrame({
        'Time': [n],
        'Disk Usage (%)': [disk_percent]
    })
    fig = px.line(df, x='Time', y='Disk Usage (%)', title='Disk Usage Over Time',
                  markers=True, line_shape='linear', color_discrete_sequence=['green'])
    fig.update_layout(xaxis_title='Time (s)', yaxis_title='Disk Usage (%)', transition_duration=500)
    return fig


# Callback to update GPU usage graph
@app.callback(Output('gpu-graph', 'figure'), Input('interval-component', 'n_intervals'))
def update_gpu_graph(n):
    gpu_info = get_gpu_info()
    if gpu_info:
        df = pd.DataFrame({
            'GPU': [gpu['name'] for gpu in gpu_info],
            'Load': [gpu['load'] for gpu in gpu_info],
            'Time': [n] * len(gpu_info)
        })
        fig = px.bar(df, x='GPU', y='Load', color='GPU', animation_frame='Time',
                     title='GPU Usage Over Time', labels={'Load': 'GPU Load (%)'})
        fig.update_layout(xaxis_title='GPU', yaxis_title='Load (%)', transition_duration=500)
    else:
        fig = go.Figure(go.Indicator(
            mode="number",
            value=0,
            title={'text': 'No GPU Detected'}
        ))
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

