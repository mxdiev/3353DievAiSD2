def rle_encode(list_ac: list[int]):
    rle = []
    zero_count = 0

    for ac in list_ac:
        if ac == 0:
            zero_count += 1
        else:
            rle.append((zero_count, ac))
            zero_count = 0

    # Добавляем EOB
    if zero_count > 0:
        rle.append((0, 0))

    return rle

def rle_decode(rle_pairs: list[tuple[int, int, int]]) -> list[int]:
    ac_coefs = []
    for run, amplitude in rle_pairs:
        if run == 0 and amplitude == 0:  # EOB
            ac_coefs.extend([0] * (64 - len(ac_coefs)))
            break
        ac_coefs.extend([0] * run)
        ac_coefs.append(amplitude)
    return ac_coefs