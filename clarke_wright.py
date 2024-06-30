from collections import defaultdict, deque
import logging
from evaluateShared import Point, VRP, Load
import utils
import numpy as np


class LoadSaving:
    """ Cost savings for clarke/wright algorithm """
    def __init__(self, current_load_id, next_load_id, savings):
        self.current_load_id = current_load_id
        self.next_load_id = next_load_id
        self.savings = savings

    def __str__(self):
        return f"S({self.current_load_id},{self.next_load_id}): {self.savings}"


class StaticState:
    """ Read only state to pass around """
    def __init__(self, vrp: VRP):
        self.vrp = vrp
        self.distance_constraint = 12 * 60
        depot = Point(0.0, 0.0)
        self.depot_id = 0
        self.dist_matrix = utils.create_distance_matrix(self.vrp, depot, self.depot_id)


class Truck:
    """ Represents a truck and its schedule/route """
    def __init__(self, ss: StaticState, load_id):
        self.ss = ss
        self.dist_matrix = ss.dist_matrix
        self.depot_id = ss.depot_id

        self.current_distance = (self.dist_matrix[self.depot_id, load_id]
                                + self.dist_matrix[load_id, load_id]
                                + self.dist_matrix[load_id, self.depot_id])
        self.load_ids = deque()
        self.load_ids.append(load_id)

    def __str__(self):
        return str(self.load_ids)

    def _new_add_right_dist(self, load_id):
        curr_last_load_id = self.load_ids[-1]
        return (self.current_distance
                + (-1.0 * self.dist_matrix[curr_last_load_id, self.depot_id])
                + self.dist_matrix[curr_last_load_id, load_id]
                + self.dist_matrix[load_id, load_id]
                + self.dist_matrix[load_id, self.depot_id])

    def _new_add_left_dist(self, load_id):
        curr_first_load_id = self.load_ids[0]
        return (self.current_distance
                + (-1.0 * self.dist_matrix[self.depot_id, curr_first_load_id])
                + self.dist_matrix[self.depot_id, load_id]
                + self.dist_matrix[load_id, load_id]
                + self.dist_matrix[load_id, curr_first_load_id])

    def add_load_right(self, load_id):
        new_dist = self._new_add_right_dist(load_id)
        if new_dist > self.ss.distance_constraint:
            raise Exception(f"Code error: Invalid truck when adding: {load_id}. new_dist: {new_dist}, current_distance: {self.current_distance}")
        self.current_distance = new_dist
        self.load_ids.append(load_id)

    def can_link_right(self, load_id):
        new_dist = self._new_add_right_dist(load_id)
        return new_dist <= self.ss.distance_constraint

    def add_load_left(self, load_id):
        new_dist = self._new_add_left_dist(load_id)
        if new_dist > self.ss.distance_constraint:
            raise Exception("Code error: Invalid truck!")
        self.current_distance = new_dist
        self.load_ids.appendleft(load_id)

    def can_link_left(self, load_id):
        new_dist = self._new_add_left_dist(load_id)
        return new_dist <= self.ss.distance_constraint

    def starting_load_id(self):
        return self.load_ids[0]

    def finishing_load_id(self):
        return self.load_ids[-1]

    def can_merge(self, truck):
        curr_last_load_id = self.load_ids[-1]
        next_truck_first_load_id = truck.load_ids[0]
        merged_dist = (((self.current_distance
                       + (-1.0 * self.dist_matrix[curr_last_load_id, self.depot_id]))
                       + truck.current_distance)
                       + (-1.0 * self.dist_matrix[self.depot_id, next_truck_first_load_id])
                       + self.dist_matrix[curr_last_load_id, next_truck_first_load_id])
        logging.debug(f"Checking for merge. Two total distances: {self.current_distance}, {truck.current_distance}. Merged: {merged_dist}")
        if merged_dist <= self.ss.distance_constraint:
            return True
        return False

    def merge(self, truck):
        for load_id in truck.load_ids:
            self.add_load_right(load_id)


class Solver:
    def __init__(self, vrp: VRP, random_swap_factor=None):
        self.vrp = vrp
        self.ss = StaticState(vrp)
        self.depot_id = self.ss.depot_id
        self.dist_matrix = self.ss.dist_matrix
        self.random_swap_factor = random_swap_factor
        logging.debug("distance matrix: \n" + str(self.dist_matrix))

    def solve(self):
        trucks = self.run_clarke_wright()

        solution = [list(truck.load_ids) for truck in trucks]
        expected_loads = len(self.dist_matrix) - 1
        cost = utils.get_solution_cost(solution, self.dist_matrix, expected_loads)
        return solution, cost

    def run_clarke_wright(self):
        trucks = []
        truck_by_load: dict = {}

        savings_list = self.create_savings()
        savings_list.sort(key=lambda x: x.savings, reverse=True)
        if self.random_swap_factor is not None:
            for i in range(len(savings_list)-1):
                # randomly decide to swap savings items
                if np.random.rand() < self.random_swap_factor:
                    savings_list[i], savings_list[i+1] = savings_list[i+1], savings_list[i]

        for s in savings_list:
            curr_truck = truck_by_load.get(s.current_load_id)
            next_truck = truck_by_load.get(s.next_load_id)
            if not curr_truck and not next_truck:
                # Neither load is claimed so try to assign a new truck
                new_truck = Truck(self.ss, s.current_load_id)
                if new_truck.can_link_right(s.next_load_id):
                    new_truck.add_load_right(s.next_load_id)
                    truck_by_load[s.current_load_id] = new_truck
                    truck_by_load[s.next_load_id] = new_truck
                    trucks.append(new_truck)
                    logging.info(f"Bootstrapped Truck with loads: {s.current_load_id}, {s.next_load_id}. Dist: {new_truck.current_distance}")
                else:
                    logging.info(f"Cant bootstrap new Truck with loads: {s.current_load_id}, {s.next_load_id}")
            elif curr_truck and not next_truck:
                # One truck has the curr/first load,
                #  if it can extend its route to handle the next load in the savings, do so
                if curr_truck.finishing_load_id() == s.current_load_id and curr_truck.can_link_right(s.next_load_id):
                    curr_truck.add_load_right(s.next_load_id)
                    truck_by_load[s.next_load_id] = curr_truck
                    logging.info(f"Extended Truck route with loads: {s.current_load_id}, {s.next_load_id}. Dist: {curr_truck.current_distance}")
            elif not curr_truck and next_truck:
                # One truck has the next/last load in the savings,
                # if it can prepend its route to handle the first load in the savings, do so
                if next_truck.starting_load_id() == s.next_load_id and next_truck.can_link_left(s.current_load_id):
                    next_truck.add_load_left(s.current_load_id)
                    truck_by_load[s.current_load_id] = next_truck
                    logging.info(f"Prepended Truck route with loads: {s.current_load_id}, {s.next_load_id}. Dist: {next_truck.current_distance}")
            else:
                # Both loads have already been assigned. See if we can merge truck routes
                #  Can only do this for S(i,j) if i is ending the route and j is starting the route
                if curr_truck != next_truck and curr_truck.finishing_load_id() == s.current_load_id and next_truck.starting_load_id() == s.next_load_id:
                    if curr_truck.can_merge(next_truck):
                        logging.info(f"Merging the Truck ending with load: {s.current_load_id} with the one starting with: {s.next_load_id}")
                        for load_id in next_truck.load_ids:
                            truck_by_load[load_id] = curr_truck
                        curr_truck.merge(next_truck)
                        trucks.remove(next_truck)

        # Find loads that have not been assigned and create single routes
        for load_id in range(1, len(self.dist_matrix)):
            if load_id not in truck_by_load:
                new_truck = Truck(self.ss, load_id)
                trucks.append(new_truck)
                logging.warning(f"Bootstrapped Truck with single load: {load_id}, distance: {new_truck.current_distance}")

        return trucks

    def create_savings(self):
        # I need to slightly modify the clarke/wright savings formula to incorporate pickup/dropoff correctly
        #  since the distance matrix is not symmetric
        # Full Formula:  S(i,j) = d(D, i_p) + d(i_p, i_d) + d(i_d, D) + d(D, j_p) + d(j_p, j_d) + d(j_d, D) -
        #             (d(D, i_p) + d(i_p, i_d) + d(i_d, j_p) + d(j_p, j_d) + d(j_d, D))
        # Simplifies to: S(i,j) = d(i_d, D) + d(D, j_p) - d(i_d, j_p)
        savings_list = []
        num_loads = len(self.dist_matrix)
        for i in range(1, num_loads):
            for j in range(1, num_loads):
                if i == j:
                    continue
                savings = self.dist_matrix[i, self.depot_id] + self.dist_matrix[self.depot_id, j] - self.dist_matrix[i, j]
                savings_list.append(LoadSaving(i, j, savings))

        return savings_list

    def local_search_improvement(self, trucks, truck_by_load):
        """
        Maybe I can run a variant of clarke/wright after I create the initial solution.
        I would iterate over every load i
            iterate over every truck
            for load j in truck (if not i)
                determine cost savings by swapping i and j (and maybe add/remove from truck)
        Notes: I will have to build a few functions to Truck:
        clone, substitute_load, remove_load_left, remove_load_right
        """
        num_loads = len(self.dist_matrix)
        for i in range(1, num_loads):
            for j in range(1, num_loads):
                if i == j:
                    i_truck = truck_by_load.get(i)
                    j_truck = truck_by_load.get(j)
                    i_truck_clone = i_truck.clone()
                    j_truck_clone = j_truck.clone()

                    i_truck_clone.substitute(i, j)
                    j_truck_clone.substitute(j, i)
                    # TODO check if solution is better
                    # TODO still working on this
