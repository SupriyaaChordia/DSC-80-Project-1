# MTS Bus Network and Wait-Time Analysis

Exploring San Diego bus connectivity and passenger waiting through schedule data, mapping, and simulation.

[View implementation](https://github.com/SupriyaaChordia/DSC-80-Project-1/blob/main/project.py) · [Analytics portfolio](https://supriyaachordia.github.io/portfolio/)

## Overview

This project combines transit schedule data with geographic visualization and simulation to examine two aspects of a rider's experience: how stops connect and how arrival timing affects waiting.

## What the implementation does

| Component | Method | Output |
| --- | --- | --- |
| Detailed schedules | Merge schedule, stop, and trip tables; filter selected routes | Ordered stop sequences with route and location information |
| Network visualization | Plot stops by route over a San Diego boundary map | Interactive Plotly map with stop-name hover labels |
| Route connectivity | Build directed next-stop relationships and apply breadth-first search | A path with the fewest stop-to-stop edges between two stops |
| Bus-arrival simulation | Sample a fixed number of arrivals uniformly between 6 a.m. and midnight | Arrival times and intervals between buses |
| Passenger waiting | Simulate passenger arrivals and calculate time until the next bus | Wait-time table and a one-hour visualization |

## Analytical decisions

**Use stop order to model direction.** Adjacent stops within a trip define which stop can be reached next. Breadth-first search then finds a path minimizing the number of stop-to-stop transitions.

**Separate connectivity from waiting.** A path describes network reachability; the simulation explores how timing can affect a passenger's experience. Treating these as separate components makes their assumptions easier to inspect.

**Make the simulation assumptions explicit.** Bus arrivals are sampled over a fixed daily window. Passenger arrivals are sampled from 6 a.m. through the final simulated bus arrival, and waiting is calculated against the next bus.

## Outputs and product implications

The code produces route maps, path tables, and simulated waiting visualizations. These can support exploration of network connectivity and timing assumptions. The reviewed source does not include saved numerical findings or evidence of an improvement to MTS operations.

For a rider-facing planning tool, the next step would be to connect these components with departure times, transfer rules, and service availability so that suggested routes reflect an actual trip.

## Limitations and next steps

- Breadth-first search minimizes stop transitions, rather than travel time, waiting, or transfers.
- Connectivity is aggregated across trips; a returned path does not establish that the journey is feasible at a particular departure time.
- Simulated arrivals are not observed MTS reliability data and do not model congestion or bus bunching.
- Add schedule-aware routing and compare simulated waiting with observed service data.

## Tools and reproduction

Python, Pandas, NumPy, GeoPandas, Shapely, and Plotly.

The repository's `project.py` provides functions to call from a notebook or Python session. Schedule construction requires schedule, stop, and trip tables; network mapping also expects `data/data_city/data_city.shp` and its companion shapefile assets. Runtime execution was not validated as part of this documentation review.
