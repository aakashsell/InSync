import numpy as np

def note_distance(note1, note2, pitch_weight=1.0, onset_weight=10.0, duration_weight=5.0):
    pitch_diff = abs(note1[0] - note2[0])
    onset_diff = abs(note1[1] - note2[1])
    duration_diff = abs(note1[2] - note2[2])
    return onset_weight * onset_diff + pitch_weight * pitch_diff + duration_weight * duration_diff

def process(array1, array2):
    n, m = len(array1), len(array2)
    cost = np.full((n + 1, m + 1), float('inf'))
    cost[0, 0] = 0  # Start with no cost at the origin

    # Fill the cost matrix, enforcing each note in array1 to match at most once
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match_cost = note_distance(array1[i - 1], array2[j - 1], pitch_weight=1.0, onset_weight=10.0, duration_weight=5.0)
            cost[i, j] = match_cost + min(
                cost[i - 1, j - 1],  # Match (i-1, j-1)
                cost[i - 1, j]       # Skip in array2
            )

    dtw_distance = cost[n, m]

    # Trace back to find the optimal alignment path
    i, j = n, m
    path = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))  # Add the current position to the path
        if cost[i - 1, j - 1] <= cost[i - 1, j]:  # Prioritize match
            i -= 1
            j -= 1
        else:  # Skip in array2
            i -= 1

    path.reverse()

    # Ensure uniqueness in array1 indices
    unique_path = []
    used_indices = set()
    for i, j in path:
        if i not in used_indices:  # Only include unique indices for array1
            unique_path.append((i, j))
            used_indices.add(i)

    return dtw_distance, unique_path
