from Huffman_table import DC_luma_Huffman, DC_chr_Huffman
import numpy as np

def coef_category(value):
    int_value = int(round(float(value)))

    if int_value == 0:
        return 0, ""

    abs_value = abs(int_value)
    category = int(np.ceil(np.log2(abs_value + 1)))

    if int_value > 0:
        amplitude = int_value
    else:
        amplitude = int_value + (1 << category) - 1

    amplitude_bits = bin(amplitude)[2:].zfill(category)
    return category, amplitude_bits


def dc_coding(y_array: [], is_luma):
    dc_coef = []
    dc_coef.append(y_array[0][0])
    for i in range(1, len(y_array)):
        dc_coef.append(y_array[i][0] - y_array[i - 1][0])

    huffman_table = DC_luma_Huffman if is_luma else DC_chr_Huffman
    bitstream = ""

    for dc in dc_coef:
        category, amplitude_bits = coef_category(dc)
        bitstream += huffman_table[category] + amplitude_bits

    return bitstream

def decode_dc_coefficients(bitstream, num_blocks, is_luma):
    huffman_table = DC_luma_Huffman if is_luma else DC_chr_Huffman
    reverse_huffman = {v: k for k, v in huffman_table.items()}

    delta_dc = np.zeros(num_blocks)
    current_pos = 0

    for i in range(num_blocks):
        found = False
        for code_len in range(1, 13):
            if current_pos + code_len > len(bitstream):
                break
            code = bitstream[current_pos:current_pos + code_len]
            if code in reverse_huffman:
                category = reverse_huffman[code]
                current_pos += code_len
                found = True
                break

        # Декодирование значения
        if category == 0:
            delta_dc[i] = 0
            continue

        amplitude_bits = bitstream[current_pos:current_pos + category]
        current_pos += category
        amplitude = int(amplitude_bits, 2)

        if amplitude < (1 << (category - 1)):
            delta_dc[i] = amplitude - (1 << category) + 1
        else:
            delta_dc[i] = amplitude

    # Восстановление DC
    dc_coeffs = np.zeros(num_blocks)
    dc_coeffs[0] = delta_dc[0]
    for i in range(1, num_blocks):
        dc_coeffs[i] = dc_coeffs[i - 1] + delta_dc[i]

    return dc_coeffs
