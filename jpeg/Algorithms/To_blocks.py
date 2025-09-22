import numpy as np

def to_blocks(channel, N):
    h, w = channel.shape

    padded_h = ((h + N - 1) // N) * N
    padded_w = ((w + N - 1) // N) * N

    padded = np.zeros((padded_h, padded_w), dtype=channel.dtype)
    padded[:h, :w] = channel

    if w < padded_w:
        padded[:h, w:padded_w] = channel[:, w-1:w]

    if h < padded_h:
        padded[h:padded_h, :] = padded[h-1:h, :]

    blocks = []
    for i in range(0, padded_h, N):
        for j in range(0, padded_w, N):
            block = padded[i:i+N, j:j+N]
            blocks.append(block)

    return blocks