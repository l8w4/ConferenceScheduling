import gurobipy as gp
from gurobipy import GRB

# Data
num_presentations = 10
num_days = 3
num_time_slots = 3
capacity = 50  # Example: maximum number of participants for each session

# Presentation lengths (minutes)
presentation_lengths = [20, 15, 30, 25, 20, 25, 30, 20, 15, 30]

# Time slot lengths for each day (minutes)
time_slot_lengths = [180, 240, 240]

# Similarity scores (example)
similarity_scores = [[1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.3, 0.5, 0.7, 0.9],
                     [0.8, 1.0, 0.7, 0.5, 0.3, 0.2, 0.4, 0.6, 0.8, 0.9],
                     [0.6, 0.7, 1.0, 0.9, 0.8, 0.5, 0.4, 0.6, 0.7, 0.8],
                     [0.4, 0.5, 0.9, 1.0, 0.9, 0.6, 0.5, 0.7, 0.8, 0.9],
                     [0.2, 0.3, 0.8, 0.9, 1.0, 0.7, 0.6, 0.8, 0.9, 0.9],
                     [0.1, 0.2, 0.5, 0.6, 0.7, 1.0, 0.9, 0.8, 0.9, 0.8],
                     [0.3, 0.4, 0.4, 0.5, 0.6, 0.9, 1.0, 0.9, 0.8, 0.7],
                     [0.5, 0.6, 0.6, 0.7, 0.8, 0.8, 0.9, 1.0, 0.9, 0.8],
                     [0.7, 0.8, 0.7, 0.8, 0.9, 0.9, 0.8, 0.9, 1.0, 0.9],
                     [0.9, 0.9, 0.8, 0.9, 0.9, 0.8, 0.7, 0.8, 0.9, 1.0]]

# Create model
m = gp.Model("ConferenceScheduling")

# Decision variables
x = m.addVars(num_presentations, num_days, num_time_slots, vtype=GRB.BINARY, name="x")

# Constraint: Each presentation is assigned to only one session
for i in range(num_presentations):
    m.addConstr(sum(x[i, j, k] for j in range(num_days) for k in range(num_time_slots)) == 1)

# Constraint: Total duration of presentations in a day does not exceed the time slot length
for j in range(num_days):
    for k in range(num_time_slots):
        m.addConstr(gp.quicksum(presentation_lengths[i] * x[i, j, k] for i in range(num_presentations)) <= time_slot_lengths[k])

# Constraint: Assign sessions based on similarity scores
for j in range(num_days):
    for k in range(num_time_slots):
        for i1 in range(num_presentations):
            for i2 in range(i1 + 1, num_presentations):
                m.addConstr(similarity_scores[i1][i2] * (x[i1, j, k] + x[i2, j, k]) <= 1)

# Constraint: Session capacity
for j in range(num_days):
    for k in range(num_time_slots):
        m.addConstr(gp.quicksum(presentation_lengths[i] * x[i, j, k] for i in range(num_presentations)) <= capacity)

# Objective function: Balance conference sessions
objective = gp.quicksum(x[i, j, k] for i in range(num_presentations) 
                                           for j in range(num_days) 
                                           for k in range(num_time_slots))
m.setObjective(objective, GRB.MAXIMIZE)

# Optimize the model
m.optimize()

# Get the optimal solution
if m.status == GRB.OPTIMAL:
    print("Optimal solution found!")

    # Print the results
    for j in range(num_days):
        for k in range(num_time_slots):
            print(f"Day {j + 1}, Time Slot {k + 1}:")
            for i in range(num_presentations):
                if x[i, j, k].x > 0:
                    print(f"Presentation {i + 1} - Duration: {presentation_lengths[i]} minutes")
else:
    print("Optimal solution could not be found.")
