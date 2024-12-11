import numpy as np
from itertools import product


weights = [100, 10, 100]  # Adjust as necessary
import numpy as np

def cost_function(a, b, w):
    note1, note2, w = np.array(a), np.array(b), np.array(w)
    if a[0] == 0 and b[0] != 0:
        return float('inf') 
    pitch_cost = abs(note1[0] - note2[0]) * w[0]
    onset_cost = abs(note1[1] - note2[1]) * w[1]
    duration_cost = abs(note1[2] - note2[2]) * w[2]


    return pitch_cost + onset_cost + duration_cost

def process(sheet_music, audio_data, weights=weights, threshold=100):
    n, m = len(sheet_music), len(audio_data)
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0

    # Fill cost matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = cost_function(sheet_music[i - 1], audio_data[j - 1], weights)
            cost_matrix[i, j] = cost + min(
                cost_matrix[i - 1, j],      # Insertion
                cost_matrix[i, j - 1],      # Deletion
                cost_matrix[i - 1, j - 1]   # Match
            )

    # Backtrack to find alignment path
    i, j = n, m
    alignment_path = []
    while i > 0 or j > 0:
        if cost_matrix[i, j] == np.inf:
            neighbors = [(i-1, j), (i, j-1), (i-1, j-1)]
            valid_neighbors = [(x, y) for x, y in neighbors if x >= 0 and y >= 0]
            i, j = min(valid_neighbors, key=lambda p: cost_matrix[p])
        else:
            if cost_matrix[i, j] != 2312:
                alignment_path.append((i - 1, j - 1))
            if i > 0 and j > 0 and cost_matrix[i - 1, j - 1] <= min(cost_matrix[i - 1, j], cost_matrix[i, j - 1]):
                i -= 1
                j -= 1
            elif i > 0 and (j == 0 or cost_matrix[i - 1, j] <= cost_matrix[i, j - 1]):
                i -= 1
            else:
                j -= 1

    alignment_path.reverse()
    total_cost = cost_matrix[n, m]
    return total_cost, alignment_path

def optimize_weights(sheet_music, audio_data):
    min_cost, best_weights, best_path = float('inf'), None, []

    from itertools import product
    for w1, w2, w3 in product(range(1, 10), range(1, 10), range(1, 10)):
        weights = [w1, w2, w3]
        total_cost, path = process(sheet_music, audio_data, weights)

        if total_cost < min_cost:
            min_cost, best_weights, best_path = total_cost, weights, path

    print(f"Best Weights: {best_weights}, Minimum Cost: {min_cost}")
    return min_cost, best_path
