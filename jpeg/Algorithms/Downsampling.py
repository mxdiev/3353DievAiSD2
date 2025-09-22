import numpy as np

def downsmpl(channel):
    factor = 2
    h, w = channel.shape
    new_h, new_w = h // factor, w // factor
    downsampled_ch = np.zeros((new_h, new_w))

    for i in range(new_h):
        for j in range(new_w):
            block = channel[i*factor:(i+1)*factor,
                          j*factor:(j+1)*factor]
            downsampled_ch[i, j] = np.mean(block)

    return downsampled_ch


def downsampling(ycbcr):
    y = ycbcr[:, :, 0]
    cb = ycbcr[:, :,  1]
    cr = ycbcr[:, :, 2]

    cb_ch = downsmpl(cb)
    cr_ch = downsmpl(cr)

    compressed_image = {
        'y' : y,
        'cb' : cb_ch,
        'cr' : cr_ch
    }

    return compressed_image