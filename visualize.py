from evaluateShared import Load
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from numpy import linspace


def visualize(loads: list[Load], solution: list[list[int]]):
    pickup_coords = [(load.pickup.x, load.pickup.y, load.id) for load in loads]
    dropoff_coords = [(load.dropoff.x, load.dropoff.y) for load in loads]

    pickup_xs, pickup_ys, pickup_ids = zip(*pickup_coords)
    dropoff_xs, dropoff_ys = zip(*dropoff_coords)

    plt.figure(figsize=(10, 6))
    plt.scatter([0], [0], color='teal', label='Depot')

    plt.scatter(pickup_xs, pickup_ys, color='blue', label='Pickup')
    plt.scatter(dropoff_xs, dropoff_ys, color='red', label='Dropoff')

    num_trucks = len(solution)

    cm_subsection = linspace(0.0, 1.0, num_trucks)
    colors = [cm.jet(x) for x in cm_subsection]

    for i, schedule in enumerate(solution):
        truck_color = colors[i]
        for j in range(len(schedule)):
            load_idx = schedule[j] - 1
            plt.arrow(pickup_coords[load_idx][0], pickup_coords[load_idx][1], dropoff_coords[load_idx][0] - pickup_coords[load_idx][0], dropoff_coords[load_idx][1] - pickup_coords[load_idx][1],
                      head_width=4, head_length=2, fc=truck_color, ec=truck_color)
            plt.text(pickup_coords[load_idx][0], pickup_coords[load_idx][1], str(load_idx+1), fontsize=12, ha='right')

    plt.title('VRPPD Visualization')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)
    plt.show()
