from evaluateShared import Point, VRP
import math
import numpy as np


def distance(p1: Point, p2: Point):
    x_diff = p1.x - p2.x
    y_diff = p1.y - p2.y
    return math.sqrt(x_diff*x_diff + y_diff*y_diff)


def create_distance_matrix(vrp: VRP, depot: Point, depot_id: int):
    num_loads = len(vrp.loads) + 1
    distance_matrix = np.zeros((num_loads, num_loads))

    # depot to first load pickup
    for load in vrp.loads:
        distance_matrix[depot_id, load.id] = distance(depot, load.pickup)
    # final load dropoff to depot
    for load in vrp.loads:
        distance_matrix[load.id, depot_id] = distance(load.dropoff, depot)
    # distances to traverse from one load to another
    for load_i in vrp.loads:
        for load_j in vrp.loads:
            # Note that the distance for the load is stored on the diagonal
            distance_matrix[load_i.id, load_j.id] = distance(load_i.dropoff, load_j.pickup)
    return distance_matrix


def get_schedule_distance(schedule: list[int], distance_matrix):
    distance = 0.0
    depot = 0
    current = depot
    for i in range(len(schedule)):
        next = schedule[i]
        distance += distance_matrix[current, next]
        distance += distance_matrix[next, next]
        current = next

    distance += distance_matrix[current, depot]
    return distance


def get_solution_cost(schedules: list[list[int]], distance_matrix, expected_loads):
    total_driven_minutes = 0.0
    total_loads = 0
    for idx, schedule in enumerate(schedules):
        total_loads += len(schedule)
        schedule_minutes = get_schedule_distance(schedule, distance_matrix)
        if schedule_minutes > 12 * 60:
            raise Exception("schedule idx " + str(idx) + " is invalid: driver runs for " + str(schedule_minutes) + " minutes")
        total_driven_minutes += schedule_minutes
    if total_loads != expected_loads:
        raise Exception(f"Should have {expected_loads}, got: {total_loads}!!")
    return 500 * len(schedules) + total_driven_minutes
