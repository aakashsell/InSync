import numpy as np

def note_distance(note1, note2, pitch_weight=1.0, onset_weight=1.0, duration_weight=1.0):

    pitch_diff = abs(note1[0] - note2[0])
    onset_diff = abs(note1[1] - note2[1])
    duration_diff = abs(note1[2] - note2[2])
    
    return pitch_weight * pitch_diff + onset_weight * onset_diff + duration_weight * duration_diff


def process(array1, array2):
    n, m = len(array1), len(array2)
    cost = np.full((n + 1, m + 1), float('inf'))
    cost[0, 0] = 0 

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist = note_distance(array1[i - 1], array2[j - 1], 0, 1, 2)
            cost[i, j] = dist + min(cost[i - 1, j],    
                                    cost[i, j - 1],    
                                    cost[i - 1, j - 1])  

    dtw_distance = cost[n, m]

    i, j = n, m
    path = [(i - 1, j - 1)]
    while i > 1 or j > 1:
        if i == 1:
            j -= 1
        elif j == 1:
            i -= 1
        else:
            min_cost = min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])
            if min_cost == cost[i - 1, j - 1]:
                i -= 1
                j -= 1
            elif min_cost == cost[i, j - 1]:
                j -= 1
            else:
                i -= 1
        path.append((i - 1, j - 1))


    path.reverse()
    return dtw_distance, path
