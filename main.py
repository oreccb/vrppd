import sys
import argparse
from evaluateShared import loadProblemFromFile
from visualize import visualize
import clarke_wright
import utils
import logging
import time


def print_solution(solution):
    for truck in solution:
        print(truck)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument("input_path", help='path to input file with problem')
    parser.add_argument("--random-swap-factor", dest='random_swap_factor', required=False, type=float)
    parser.add_argument("--visualize", required=False, action='store_true')
    args = parser.parse_args()

    vrp_problem = loadProblemFromFile(args.input_path)
    # make a usability tweak to the problem data and turn ids from strings to ints
    for load in vrp_problem.loads:
        load.id = int(load.id)

    logging.debug(vrp_problem)

    if args.random_swap_factor:
        solution, cost = clarke_wright.Solver(vrp_problem).solve()
        #print(f"Initial Solution Cost: {cost}")
        t_end = time.time() + 25  # run for ~25 seconds, really should just time the first solve to tune this better
        while time.time() < t_end:
            tmp_solution, tmp_cost = clarke_wright.Solver(vrp_problem, random_swap_factor=args.random_swap_factor).solve()
            if tmp_cost < cost:
                solution = tmp_solution
                cost = tmp_cost
                #print(f"Better Solution Cost: {cost}")
    else:
        solution, cost = clarke_wright.Solver(vrp_problem).solve()

    print_solution(solution)
    #logging.warning(f"Solution Cost: {cost}")

    if args.visualize:
        visualize(vrp_problem.loads, solution)