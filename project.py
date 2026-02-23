# project.py


import pandas as pd
import numpy as np
from pathlib import Path

###
from collections import deque
from shapely.geometry import Point
###

import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
pd.options.plotting.backend = 'plotly'

import geopandas as gpd

import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------
# QUESTION 1
# ---------------------------------------------------------------------


def create_detailed_schedule(schedule, stops, trips, bus_lines):
    merged = schedule.merge(stops, on = 'stop_id').merge(trips, on = 'trip_id').set_index('trip_id')
    merged = merged[merged['route_id'].isin(bus_lines)]
    merged['route_id'] = pd.Categorical(merged['route_id'], categories=bus_lines, ordered=True)
    stop_count = merged.groupby('trip_id')['stop_sequence'].max().reset_index()
    stop_count.rename(columns={'stop_sequence': 'num_stops'}, inplace=True)
    combined = merged.merge(stop_count, on='trip_id')
    final_df = combined.sort_values(by=['route_id','num_stops','stop_sequence']).drop(columns='num_stops')
    return final_df.set_index('trip_id')


def visualize_bus_network(bus_df):
    san_diego_boundary_path = 'data/data_city/data_city.shp'
    san_diego_city_bounds = gpd.read_file(san_diego_boundary_path)
    san_diego_city_bounds = san_diego_city_bounds.to_crs("EPSG:4326")
    san_diego_city_bounds['lon'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.x)
    san_diego_city_bounds['lat'] = san_diego_city_bounds.geometry.apply(lambda x: x.centroid.y)
    fig = go.Figure()
    fig.add_trace(go.Choroplethmapbox(
        geojson=san_diego_city_bounds.__geo_interface__,
        locations=san_diego_city_bounds.index,
        z=[1] * len(san_diego_city_bounds),
        colorscale="Greys",
        showscale=False,
        marker_opacity=0.5,
        marker_line_width=1,
    ))
    colors = px.colors.qualitative.Plotly
    color_map = {route: colors[i] for i, route in enumerate(bus_df['route_id'].unique())}
    for id in bus_df['route_id'].unique():
        route_data = bus_df[bus_df['route_id'] == id]
        fig.add_trace(go.Scattermapbox(
            lon=route_data['stop_lon'],
            lat=route_data['stop_lat'],
            mode='markers',
            marker=dict(color=color_map[id], 
                        size=10),
            name=f"Bus Line {id}",
            text=route_data['stop_name']
        ))
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center={"lat": bus_df['stop_lat'].mean(), "lon": bus_df['stop_lon'].mean()},
            zoom=10,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


# ---------------------------------------------------------------------
# QUESTION 2
# ---------------------------------------------------------------------



def find_neighbors(station_name, detailed_schedule):
    contains_station = detailed_schedule[detailed_schedule['stop_name'] == station_name]
    next_stop_seq = []
    index = []
    neighbors = []
    for i in range(len(contains_station)):
        next_stop_seq.append(contains_station['stop_sequence'].iloc[i] + 1)
        index.append(contains_station.index[i])
        result = detailed_schedule[(detailed_schedule.index == index[i]) & (detailed_schedule['stop_sequence'] == next_stop_seq[i])]
        if len(result) > 0:
            neighbors.append(result.iloc[0]['stop_name'])
    return np.unique(neighbors)

def bfs(start_station, end_station, detailed_schedule):
    if start_station not in detailed_schedule['stop_name'].values:
        return f"Start station {start_station} not found."
    if end_station not in detailed_schedule['stop_name'].values:
        return f"End station {end_station} not found."
    station_queue = [start_station]
    visited = [start_station]
    parent = {start_station: None} 
    stop_sequence = {start_station: 1} 
    while station_queue:
        current_station = station_queue.pop(0)
        if current_station == end_station:
            path = []
            while current_station != None:
                path.append(current_station)
                current_station = parent[current_station]
            path.reverse()
            result = []
            stop_num = 1  
            for station in path:
                station_details = detailed_schedule[detailed_schedule['stop_name'] == station].iloc[0]
                result.append({
                    'stop_name': station,
                    'stop_lat': station_details['stop_lat'],
                    'stop_lon': station_details['stop_lon'],
                    'stop_num': stop_num
                })
                stop_num += 1
            return pd.DataFrame(result)
        neighbors = find_neighbors(current_station, detailed_schedule)
        for neighbor in neighbors:
            if neighbor not in visited:
                visited.append(neighbor) 
                parent[neighbor] = current_station
                stop_sequence[neighbor] = stop_sequence[current_station] + 1
                station_queue.append(neighbor)
    return "No path found."


# ---------------------------------------------------------------------
# QUESTION 3
# ---------------------------------------------------------------------


def simulate_bus_arrivals(tau, seed=12):
    
    np.random.seed(seed) # Random seed -- do not change
    start = 360
    end = 1440
    total_buses = int((end - start) / tau)
    arrival_time = sorted(np.random.uniform(start, end, total_buses))
    intervals = np.diff([start] + arrival_time)
    times = [f"{int(t // 60):02}:{int(t % 60):02}:{int((t - int(t)) * 60):02}" for t in arrival_time]
    bus_arrivals = pd.DataFrame({
        'Arrival Time': times,
        'Interval': intervals
    })
    return bus_arrivals

# ---------------------------------------------------------------------
# QUESTION 4
# ---------------------------------------------------------------------


def simulate_wait_times(arrival_times_df, n_passengers):
    bus_arrival = [int(t[:2]) * 60 + int(t[3:5]) + int(t[6:8]) / 60 for t in arrival_times_df['Arrival Time']]
    start = 360 
    end = bus_arrival[-1]
    passenger_arrival = sorted(start + (end - start) * np.random.rand(n_passengers))
    wait_times = []
    i = 0 
    for passenger_time in passenger_arrival:
        while bus_arrival[i] < passenger_time:
            i += 1
        wait = bus_arrival[i] - passenger_time
        wait_times.append({
            'Passenger Arrival Time': f"{int(passenger_time // 60):02}:{int(passenger_time % 60):02}:{int((passenger_time % 1) * 60):02}",
            'Bus Arrival Time': arrival_times_df['Arrival Time'].iloc[i],
            'Bus Index': i,
            'Wait Time': wait,
        })
    return pd.DataFrame(wait_times)

def visualize_wait_times(wait_times_df, timestamp):
    timestamp = timestamp.time()
    start_time_minutes = timestamp.hour * 60 + timestamp.minute + timestamp.second / 60
    wait_times_df['Bus Arrival Time'] = pd.to_datetime(wait_times_df['Bus Arrival Time'])
    wait_times_df['Passenger Arrival Time'] = pd.to_datetime(wait_times_df['Passenger Arrival Time'])
    wait_times_df['Bus Arrival Time'] = (wait_times_df['Bus Arrival Time'].dt.hour * 60 + wait_times_df['Bus Arrival Time'].dt.minute) - start_time_minutes
    wait_times_df['Passenger Arrival Time'] = (wait_times_df['Passenger Arrival Time'].dt.hour * 60 + wait_times_df['Passenger Arrival Time'].dt.minute) - start_time_minutes
    filtered = wait_times_df[(wait_times_df['Bus Arrival Time'] >= 0) & (wait_times_df['Bus Arrival Time'] < 60)]
    bus = filtered['Bus Arrival Time']
    passanger = filtered['Passenger Arrival Time']
    wait = filtered['Wait Time']
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bus, 
        y=[0] * len(bus),
        mode='markers',
        marker=dict(color='blue', size=10),
        name = 'Bus',
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=passanger, 
        y=wait,
        mode='markers',
        marker=dict(color='red', size=5),
        name = 'Passanger',
        showlegend= True
    ))
    for p, w in zip(passanger, wait):
        fig.add_trace(go.Scatter(
            x=[p, p],
            y=[0, w], 
            mode='lines',
            line=dict(color='red', dash='dot'),
            showlegend=False,
        ))
    fig.update_layout(
        title='Passenger Wait Times',
        xaxis=dict(
            range=[0, 60],
        ),
        yaxis= dict(
            range=[0, 25],
        ),
        yaxis_title='Wait Time (minutes)',
    )
    return fig