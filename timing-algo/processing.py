import numpy as np


def process(sequence_a, sequence_b):


    # Define gap element and gap penalty
    gap = (0, 0, 0)
    gap_penalty = 1.0

    # Distance function (Euclidean distance for 3D points)
    def euclidean_distance(point1, point2):
        return np.sqrt(sum((x - y) ** 2 for x, y in zip(point1, point2)))

    # Initialize ERP matrix
    m, n = len(sequence_a), len(sequence_b)
    erp_matrix = np.zeros((m + 1, n + 1))

    # Initialize first row and column with cumulative gap penalties
    for i in range(1, m + 1):
        erp_matrix[i][0] = erp_matrix[i - 1][0] + euclidean_distance(sequence_a[i - 1], gap)

    for j in range(1, n + 1):
        erp_matrix[0][j] = erp_matrix[0][j - 1] + euclidean_distance(gap, sequence_b[j - 1])

    # Fill the ERP matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match_cost = euclidean_distance(sequence_a[i - 1], sequence_b[j - 1])
            deletion_cost = erp_matrix[i - 1][j] + euclidean_distance(sequence_a[i - 1], gap)
            insertion_cost = erp_matrix[i][j - 1] + euclidean_distance(gap, sequence_b[j - 1])

            # Take the minimum of match, deletion, or insertion costs
            erp_matrix[i][j] = min(match_cost + erp_matrix[i - 1][j - 1], deletion_cost, insertion_cost)

    # The ERP distance between the two sequences
    erp_distance = erp_matrix[m][n]

    # Backtracking to retrieve the path
    i, j = m, n
    path = []

    while i > 0 or j > 0:
        current_cost = erp_matrix[i][j]
        if i > 0 and j > 0 and current_cost == erp_matrix[i - 1][j - 1] + euclidean_distance(sequence_a[i - 1], sequence_b[j - 1]):
            path.append((i - 1, j - 1))  # Match
            i -= 1
            j -= 1
        elif i > 0 and current_cost == erp_matrix[i - 1][j] + euclidean_distance(sequence_a[i - 1], gap):
            path.append((i - 1, None))  # Deletion (gap in sequence_b)
            i -= 1
        else:
            path.append((None, j - 1))  # Insertion (gap in sequence_a)
            j -= 1

    # Reverse the path to make it start-to-end
    path = path[::-1]

    print("ERP Distance:", erp_distance)
    print("Optimal Path:", path)
