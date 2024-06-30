import sys
import argparse
from evaluateShared import loadProblemFromFile
from visualize import visualize
import clarke_wright
import logging
import time


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
    parser.add_argument("--local-search-iterations", dest='local_search_iterations', required=False, type=int)
    parser.add_argument("--visualize", required=False, action='store_true')
    args = parser.parse_args()

    vrp_problem = loadProblemFromFile(args.input_path)
    # make a usability tweak to the problem data and turn ids from strings to ints
    for load in vrp_problem.loads:
        load.id = int(load.id)

    logging.debug(vrp_problem)

    if args.random_swap_factor:
        solution, cost = clarke_wright.Solver(vrp_problem, local_search_iterations=args.local_search_iterations).solve()
        logging.warning(f"Initial Solution Cost: {cost}")
        t_end = time.time() + 20  # approx run for ~20 seconds
        while time.time() < t_end:
            tmp_solution, tmp_cost = clarke_wright.Solver(vrp_problem,
                                                          random_swap_factor=args.random_swap_factor,
                                                          local_search_iterations=args.local_search_iterations).solve()
            if tmp_cost < cost:
                solution = tmp_solution
                cost = tmp_cost
                logging.warning(f"Better Solution Cost: {cost}")
    else:
        solution, cost = clarke_wright.Solver(vrp_problem, local_search_iterations=args.local_search_iterations).solve()
        logging.warning(f"Solution Cost: {cost}")

    for truck in solution:
        print(truck)

    if args.visualize:
        visualize(vrp_problem.loads, solution)
