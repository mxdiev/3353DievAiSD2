import numpy as np

def zigzag(matrix: np.ndarray) -> list:
    n = len(matrix)
    result = []
    for s in range(2 * n - 1):
        if s < n:
            if s % 2 == 0:
                x_start = s
                y_start = 0
            else:
                x_start = 0
                y_start = s
        else:
            if s % 2 == 0:
                x_start = n - 1
                y_start = s - n + 1
            else:
                x_start = s - n + 1
                y_start = n - 1
        for d in range(abs(y_start - x_start) + 1):
            if s % 2 == 0:
                x = x_start - d
                y = y_start + d
            else:
                x = x_start + d
                y = y_start - d
            if x < n and y < n:
                result.append(matrix[x, y])
    return result


def inverse_zigzag(zigzag_list: list, n: int) -> np.ndarray:
    matrix = np.zeros((n, n), dtype=type(zigzag_list[0]))
    index = 0

    for s in range(2 * n - 1):
        if s < n:
            if s % 2 == 0:
                x_start = s
                y_start = 0
            else:
                x_start = 0
                y_start = s
        else:
            if s % 2 == 0:
                x_start = n - 1
                y_start = s - n + 1
            else:
                x_start = s - n + 1
                y_start = n - 1

        for d in range(abs(y_start - x_start) + 1):
            if s % 2 == 0:
                x = x_start - d
                y = y_start + d
            else:
                x = x_start + d
                y = y_start - d

            if x < n and y < n:
                if index < len(zigzag_list):
                    matrix[x, y] = zigzag_list[index]
                    index += 1
                else:
                    break

    return matrix