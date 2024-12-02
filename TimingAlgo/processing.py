import numpy as np

weights = np.array([5, 5, 10])  # Adjust as necessary

def cost_function(a, b):
    # Apply weights to onset time difference, pitch, and duration to prioritize onset time
    note1 = np.array(a)
    note2 = np.array(b)

    if(a[0] == 0 and b[0] != 0):
        return 1000000
    
    return np.sum(weights * np.abs(note1 - note2))

def process(sheet_music, audio_data, threshold=100, local_constraint=None):
    n = len(sheet_music)
    m = len(audio_data)
    
    cost_matrix = np.full((n + 1, m + 1), np.inf)
    cost_matrix[0, 0] = 0  # Starting point

    # Fill cost matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            
            cost = cost_function(sheet_music[i - 1], audio_data[j - 1])

            

            cost_matrix[i, j] = cost + min(
                cost_matrix[i - 1, j],      # Insertion
                cost_matrix[i, j - 1],      # Deletion
                cost_matrix[i - 1, j - 1]   # Match
            )


            
    i, j = n, m
    alignment_path = []
    while i > 0 or j > 0:
        if cost_matrix[i, j] == np.inf:  
            if i > 0:
                i -= 1
            elif j > 0:
                j -= 1
            continue
        
        alignment_path.append((i - 1, j - 1))
        
        if i > 0 and j > 0 and cost_matrix[i - 1, j - 1] <= cost_matrix[i - 1, j] and cost_matrix[i - 1, j - 1] <= cost_matrix[i, j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or cost_matrix[i - 1, j] <= cost_matrix[i, j - 1]):
            i -= 1
        else:
            j -= 1

    alignment_path.reverse()

    total_cost = cost_matrix[n, m]

    return total_cost, alignment_path


