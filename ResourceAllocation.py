import random

# Sample data input
locations = [
    {'name': 'Location A', 'priority': 3, 'need': {'food': 50, 'water': 40, 'medical': 20}, 'distance': 10, 'accessibility': 2},
    {'name': 'Location B', 'priority': 2, 'need': {'food': 40, 'water': 30, 'medical': 10}, 'distance': 150, 'accessibility': 3},
    {'name': 'Location C', 'priority': 3, 'need': {'food': 30, 'water': 20, 'medical': 5}, 'distance': 200, 'accessibility': 4},
]
resources = {'food': 100, 'water': 90, 'medical': 50}
transportation_limits = {'food': 50, 'water': 50, 'medical': 20}
vehicle_info = {'number_of_vehicles': 3, 'capacity': {'food': 50, 'water': 50, 'medical': 20}, 'average_speed': 50}


# Function to sort locations by priority and accessibility
def sort_by_priority_and_accessibility(locations):
    return sorted(locations, key=lambda loc: (loc['priority'], -loc['accessibility']), reverse=True)

# Function to evaluate the quality of a solution (objective is to maximize satisfaction and priority coverage)
def evaluate_solution(solution):
    total_score = 0
    for location in solution:
        for resource_type, allocated in location['allocated'].items():
            satisfaction = allocated / location['need'][resource_type]
            total_score += satisfaction * location['priority']
    return total_score

# Function to generate a neighboring solution for the current allocation
def generate_neighbor(solution):
    neighbor = [loc.copy() for loc in solution]
    loc1, loc2 = random.sample(neighbor, 2)
    resource_type = random.choice(list(loc1['allocated'].keys()))
    amount_to_swap = min(loc1['allocated'][resource_type], loc2['need'][resource_type] - loc2['allocated'][resource_type])
    loc1['allocated'][resource_type] -= amount_to_swap
    loc2['allocated'][resource_type] += amount_to_swap
    return neighbor

# Function to adjust allocations based on transportation limits
def adjust_for_transportation_limits(solution, transportation_limits):
    for location in solution:
        for resource_type, allocated in location['allocated'].items():
            if allocated > transportation_limits[resource_type]:
                location['allocated'][resource_type] = transportation_limits[resource_type]

# Function to reallocate any excess resources
def reallocate_excess_resources(solution, remaining_resources):
    for location in solution:
        for resource_type in remaining_resources:
            need = location['need'][resource_type] - location['allocated'][resource_type]
            allocated = min(need, remaining_resources[resource_type])
            location['allocated'][resource_type] += allocated
            remaining_resources[resource_type] -= allocated

# Function to calculate the delivery sequence and time estimates
def calculate_delivery_sequence_and_times(locations, vehicle_info):
    # Sort by priority and accessibility for delivery sequence
    sorted_locations = sorted(locations, key=lambda loc: (loc['priority'], loc['distance']))
    sequence = []
    total_time = 0
    
    for location in sorted_locations:
        travel_time = location['distance'] / vehicle_info['average_speed']
        sequence.append({'location': location['name'], 'estimated_delivery_time': total_time + travel_time})
        total_time += travel_time

    return sequence

# Main function for resource allocation
def allocate_resources(locations, resources, transportation_limits, vehicle_info, max_iterations=1000):
    # Step 1: Sort locations by priority and accessibility
    sorted_locations = sort_by_priority_and_accessibility(locations)
    
    # Step 2: Initialize allocation based on priority
    for location in sorted_locations:
        location['allocated'] = {}
        for resource_type in resources:
            allocated = min(location['need'][resource_type], resources[resource_type])
            location['allocated'][resource_type] = allocated
            resources[resource_type] -= allocated

    # Step 3: Improve solution iteratively using greedy + heuristic approach
    current_solution = sorted_locations
    for _ in range(max_iterations):
        neighbor_solution = generate_neighbor(current_solution)
        if evaluate_solution(neighbor_solution) > evaluate_solution(current_solution):
            current_solution = neighbor_solution

    # Step 4: Adjust for transportation constraints
    adjust_for_transportation_limits(current_solution, transportation_limits)
    
    # Step 5: Reallocate any excess resources left after initial distribution
    reallocate_excess_resources(current_solution, resources)
    
    # Step 6: Determine delivery sequence and estimated delivery times
    delivery_sequence = calculate_delivery_sequence_and_times(current_solution, vehicle_info)

    # Step 7: Compile final output for allocation and delivery plan
    final_plan = {
        'allocations': [
            {
                'location': loc['name'],
                'allocated_resources': loc['allocated'],
                'fulfilled': all(loc['allocated'][rtype] == loc['need'][rtype] for rtype in loc['need'])
            } for loc in current_solution
        ],
        'delivery_sequence': delivery_sequence
    }
    
    return final_plan




final_allocation_plan = allocate_resources(locations, resources, transportation_limits, vehicle_info)

for allocation in final_allocation_plan['allocations']:
    location_name = allocation['location']
    allocated = allocation['allocated_resources']
    fulfilled = "Fully Fulfilled" if allocation['fulfilled'] else "Not Fully Fulfilled"
    print(f"{location_name}: {allocated}, Status: {fulfilled}")

print("\nDelivery Sequence:")
for step in final_allocation_plan['delivery_sequence']:
    print(f"Location: {step['location']}, Estimated Delivery Time: {step['estimated_delivery_time']} hours")
