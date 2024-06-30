# Vehicle Routing Problem with Pickup and Delivery




This VRP specifies a set of loads to be completed efficiently by an unbounded number of drivers.

Each load has a pickup location and a dropoff location, each specified by a Cartesian point. A driver completes a load by driving to the pickup location, picking up the load, driving to the dropoff, and dropping off the load. The time required to drive from one point to another, in minutes, is the Euclidean distance between them. That is, to drive from `(x1, y1)` to `(x2, y2)` takes `sqrt((x2-x1)^2 + (y2-y1)^2)` minutes.

Each driver starts and ends his shift at a depot located at `(0,0)`. A driver may complete multiple loads on his shift, but may not exceed 12 hours of total drive time. That is, the total Euclidean distance of completing all his loads, including the return to `(0,0)`, must be less than `12*60`.

A VRP solution contains a list of drivers, each of which has an ordered list of loads to be completed. All loads must be assigned to a driver.

The total cost of a solution is given by the formula:

	 total_cost = 500*number_of_drivers + total_number_of_driven_minutes 

## Environment Setup

```commandline
# Clone the repo
git clone git@github.com:oreccb/vrppd.git
cd vrppd

# Create a virtual environment with something like this (adpated to your version of python). I used python 3.9
virtualenv --python=/Library/Frameworks/Python.framework/Versions/3.9/bin/python3.9 venv
source venv/bin/activate
pip install -r ./requirements.txt

# Run on a single problem
python3 main.py ./training_problems/problem1.txt

# Visualize a solution
python3 main.py ./training_problems/problem1.txt --visualize

# Run evaluation on training set
python3 evaluateShared.py --cmd "python3 main.py" --problemDir "./training_problems/"
```

## Approaches

### Baseline Clarke and Wright
The baseline solver uses the Clarke and Wright Savings algorithm slightly adapted for the pickup and delivery variant of the vehicle routing problem where the distance matrix is not symmetric since the order matters in the order of handling loads because of the requirement to pick it up and drop it off somewhere else vs just traversing a set of dropoff points.

Result:
```
# Running: python3 main.py ./training_problems/problem1.txt
mean cost: 44270.4103171508
mean run time: 766.927170753479ms
```

### Clarke and Wright with randomness

I tried to see if adding some randomness in how the savings list is processed could reduce the cost with enough attempts at the solution. This worked to a small degree on the training set but greatly increases the run time. 

Result:
```
python3 main.py --random-swap-factor=0.4 ./training_problems/problem1.txt --random-swap-factor=0.4 
mean cost: 43666.36985363955
mean run time: 26415.309476852417ms
```

## References

- [Notes](https://www2.isye.gatech.edu/~mgoetsch/cali/VEHICLE/TSP/TSP007__.HTM) from Professor Goetschalckx at Georgia Tech about TSP.
- This section of [Urban Opoerations Reasearch book](https://web.mit.edu/urban_or_book/www/book/chapter6/6.4.12.html) from MIT had a great description of the Clarke and Wright Savings algorithm.


