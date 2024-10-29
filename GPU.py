import psutil
import GPUtil
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import collections

# Initialize the Dash app
app = dash.Dash(__name__)

# Historical data for bar plots and histograms
cpu_history = collections.deque(maxlen=100)
memory_history = collections.deque(maxlen=100)
disk_history = collections.deque(maxlen=100)
gpu_history = collections.deque(maxlen=100)


# Function to get system metrics
def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    return cpu_percent, memory_info.percent, disk_usage.percent


# Function to get GPU metrics (if GPU is available)
def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return None  # Return None if no GPUs are detected
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
    except Exception as e:
        print(f"Error detecting GPU: {e}")
        return None


# Layout of the dashboard with tabs and animated background
app.layout = html.Div([
    html.H1("🌐 Real-Time System Monitoring",
            style={'textAlign': 'center', 'color': '#ffffff', 'fontFamily': 'Arial', 'padding': '10px'}),

    dcc.Tabs([
        dcc.Tab(label='⚙️ CPU Usage', children=[
            dcc.Graph(id='cpu-graph', style={'height': '300px'}),
            dcc.Graph(id='cpu-bar-graph', style={'height': '300px'}),
            dcc.Graph(id='cpu-histogram', style={'height': '300px'}),  # New Histogram graph for CPU
        ]),

        dcc.Tab(label='🧠 Memory Usage', children=[
            dcc.Graph(id='memory-graph', style={'height': '300px'}),
            dcc.Graph(id='memory-bar-graph', style={'height': '300px'}),
            dcc.Graph(id='memory-histogram', style={'height': '300px'}),  # New Histogram graph for Memory
        ]),

        dcc.Tab(label='💾 Disk Usage', children=[
            dcc.Graph(id='disk-graph', style={'height': '300px'}),
            dcc.Graph(id='disk-bar-graph', style={'height': '300px'}),
            dcc.Graph(id='disk-histogram', style={'height': '300px'}),  # New Histogram graph for Disk
        ]),

        dcc.Tab(label='🎮 GPU Usage', children=[
            dcc.Graph(id='gpu-graph', style={'height': '300px'}),
            dcc.Graph(id='gpu-bar-graph', style={'height': '300px'}),
            dcc.Graph(id='gpu-histogram', style={'height': '300px'}),  # New Histogram graph for GPU
        ]),

    ], style={'color': '#ffffff', 'fontWeight': 'bold', 'fontSize': '18px'}),

    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
], style={'backgroundColor': '#1f1f1f', 'padding': '20px', 'fontFamily': 'Arial'})


# Callback to update CPU usage gauge
@app.callback(Output('cpu-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_cpu_graph(n):
    cpu_percent, _, _ = get_system_info()
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=cpu_percent,
            title={'text': 'CPU Usage (%)'},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': 'crimson'},
                   'steps': [{'range': [0, 50], 'color': '#FFDDC1'},
                             {'range': [50, 100], 'color': '#FF6F61'}]}
        )
    )
    figure.update_layout(transition_duration=500, paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Callback to update CPU bar plot (history)
@app.callback(Output('cpu-bar-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_cpu_bar_graph(n):
    cpu_percent, _, _ = get_system_info()
    cpu_history.append(cpu_percent)

    figure = go.Figure(
        go.Bar(x=list(range(len(cpu_history))), y=list(cpu_history),
               marker_color='crimson', name='CPU Usage (%)')
    )
    figure.update_layout(title='CPU Usage History', paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Callback to update CPU histogram
@app.callback(Output('cpu-histogram', 'figure'), [Input('interval-component', 'n_intervals')])
def update_cpu_histogram(n):
    # Plot the histogram of CPU usage values
    figure = go.Figure(
        go.Histogram(x=list(cpu_history), nbinsx=10, marker_color='crimson')
    )
    figure.update_layout(title='CPU Usage Distribution', paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Repeat similar callbacks for Memory, Disk, and GPU histograms

# Callback to update Memory histogram
@app.callback(Output('memory-histogram', 'figure'), [Input('interval-component', 'n_intervals')])
def update_memory_histogram(n):
    figure = go.Figure(
        go.Histogram(x=list(memory_history), nbinsx=10, marker_color='blue')
    )
    figure.update_layout(title='Memory Usage Distribution', paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Callback to update Disk histogram
@app.callback(Output('disk-histogram', 'figure'), [Input('interval-component', 'n_intervals')])
def update_disk_histogram(n):
    figure = go.Figure(
        go.Histogram(x=list(disk_history), nbinsx=10, marker_color='green')
    )
    figure.update_layout(title='Disk Usage Distribution', paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Callback to update GPU histogram
@app.callback(Output('gpu-histogram', 'figure'), [Input('interval-component', 'n_intervals')])
def update_gpu_histogram(n):
    gpu_info = get_gpu_info()

    if gpu_info:
        gpu_loads = [gpu['load'] for gpu in gpu_info]
        gpu_history.extend(gpu_loads)

        figure = go.Figure(
            go.Histogram(x=list(gpu_history), nbinsx=10, marker_color='rgba(255,99,71,0.6)')
        )
    else:
        # If no GPU is available, plot an empty graph
        figure = go.Figure(go.Indicator(
            mode="number",
            value=0,
            title={'text': 'No GPU Detected'},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))

    figure.update_layout(title='GPU Usage Distribution', paper_bgcolor='#1f1f1f', font_color='#ffffff')
    return figure


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


