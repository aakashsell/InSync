import numpy as np

def calculate_distance(a, b, onset_weight=2000.0, pitch_weight=0.0, duration_weight=1.0):
    # Apply weights to onset time difference, pitch, and duration to prioritize onset time
    pitch_diff = abs(a[0] - b[0]) * pitch_weight
    onset_diff = abs(a[1] - b[1]) * onset_weight
    duration_diff = abs(a[2] - b[2]) * duration_weight
    
    return pitch_diff + onset_diff + duration_diff

def process(array1, array2, threshold=10.0):
    n, m = len(array1), len(array2)
    cost = np.inf * np.ones((n + 1, m + 1))  # Initialize cost matrix
    cost[0, 0] = 0.0  # Starting point should be 0,0
    
    path = []  # To track the alignment path

    # DP to calculate cost and track valid matches
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate distance
            distance = calculate_distance(array1[i - 1], array2[j - 1])
            
            # Skip points in array2 if the distance is too large (extraneous)
            if distance > threshold:
                continue  # Skip extraneous points in array2
            
            # Otherwise, calculate cost and update cost matrix
            cost[i, j] = min(cost[i - 1, j - 1], cost[i, j - 1], cost[i - 1, j]) + distance

    # Reconstruct the path (this part can be modified based on the alignment logic)
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        
        # Check where the minimum cost came from to decide the path
        if cost[i, j] == cost[i - 1, j - 1] + calculate_distance(array1[i - 1], array2[j - 1]):
            i -= 1
            j -= 1
        elif cost[i, j] == cost[i, j - 1] + calculate_distance(array1[i - 1], array2[j - 1]):
            j -= 1
        else:
            i -= 1

    path.reverse()  # Reverse to get the correct path order
    
    return cost[n, m], path
