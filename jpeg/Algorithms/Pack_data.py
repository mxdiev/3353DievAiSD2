import json
import struct
import numpy as np

def pack_data(image_size, quality,
              luma_dc_coded, luma_ac_coded, cb_dc_coded, cb_ac_coded, cr_dc_coded, cr_ac_coded):

    def bits_to_bytes(bits):
        padding = (8 - len(bits) % 8) % 8
        bits += '0' * padding
        return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)), padding, len(bits)

    # Упаковываем DC компоненты
    luma_dc_bytes, luma_dc_pad, luma_dc_len = bits_to_bytes(luma_dc_coded)
    cb_dc_bytes, cb_dc_pad, cb_dc_len = bits_to_bytes(cb_dc_coded)
    cr_dc_bytes, cr_dc_pad, cr_dc_len = bits_to_bytes(cr_dc_coded)

    #AC
    luma_ac_bytes = []
    luma_ac_len = []
    for bits in luma_ac_coded:
        bytes_data, pad, bitlen = bits_to_bytes(bits)
        luma_ac_bytes.append(bytes_data)
        luma_ac_len.append(bitlen)

    cb_ac_bytes = []
    cb_ac_len = []
    for bits in cb_ac_coded:
        bytes_data, pad, bitlen = bits_to_bytes(bits)
        cb_ac_bytes.append(bytes_data)
        cb_ac_len.append(bitlen)

    cr_ac_bytes = []
    cr_ac_len = []
    for bits in cr_ac_coded:
        bytes_data, pad, bitlen = bits_to_bytes(bits)
        cr_ac_bytes.append(bytes_data)
        cr_ac_len.append(bitlen)

    # Метаданные
    meta = {
        'image_size': image_size,
        'quality': quality,
        'dc_info': {
            'Y': {'padding': luma_dc_pad, 'bitlen': luma_dc_len},
            'Cb': {'padding': cb_dc_pad, 'bitlen': cb_dc_len},
            'Cr': {'padding': cr_dc_pad, 'bitlen': cr_dc_len}
        },
        'ac_info': {
            'Y': { 'bitlens': luma_ac_len},
            'Cb': {'bitlens': cb_ac_len},
            'Cr': {'bitlens': cr_ac_len}
        }
    }

    meta_json = json.dumps(meta).encode('utf-8')
    meta_len = len(meta_json)

    packed = (
            struct.pack('I', meta_len) +
            meta_json +
            luma_dc_bytes +
            cb_dc_bytes +
            cr_dc_bytes +
            b''.join(luma_ac_bytes) +
            b''.join(cb_ac_bytes) +
            b''.join(cr_ac_bytes)
    )

    return packed

def unpacking_data(packed):
    meta_len = struct.unpack('I', packed[:4])[0]
    meta_json = packed[4:4 + meta_len]
    meta = json.loads(meta_json.decode('utf-8'))

    data = packed[4 + meta_len:]
    pos = 0

    def read_dc_component(component):
        info = meta['dc_info'][component]
        byte_len = (info['bitlen'] + 7) // 8
        bytes_data = data[pos:pos + byte_len]
        bits = ''.join(f'{byte:08b}' for byte in bytes_data)
        if info['padding'] > 0:
            bits = bits[:-info['padding']]
        return bits, byte_len

    luma_dc_bits, luma_dc_len = read_dc_component('Y')
    pos += luma_dc_len

    cb_dc_bits, cb_dc_len = read_dc_component('Cb')
    pos += cb_dc_len

    cr_dc_bits, cr_dc_len = read_dc_component('Cr')
    pos += cr_dc_len

    def read_ac_components(component):
        nonlocal pos
        ac_bits = []
        for bitlen in meta['ac_info'][component]['bitlens']:
            byte_len = (bitlen + 7) // 8
            bytes_data = data[pos:pos + byte_len]
            bits = ''.join(f'{byte:08b}' for byte in bytes_data)
            padding = (8 - bitlen % 8) % 8
            if padding > 0:
                bits = bits[:-padding]
            ac_bits.append(bits)
            pos += byte_len
        return ac_bits

    luma_ac_bits = read_ac_components('Y')

    cb_ac_bits = read_ac_components('Cb')

    cr_ac_bits = read_ac_components('Cr')

    return {
        'image_size': tuple(meta['image_size']),
        'quality': meta['quality'],
        'luma_dc': luma_dc_bits,
        'luma_ac': luma_ac_bits,
        'cb_dc': cb_dc_bits,
        'cb_ac': cb_ac_bits,
        'cr_dc': cr_dc_bits,
        'cr_ac': cr_ac_bits
    }

def pack_data_Y(image_size, quality,
              luma_dc_coded, luma_ac_coded):

    def bits_to_bytes(bits):
        padding = (8 - len(bits) % 8) % 8
        bits += '0' * padding
        return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)), padding, len(bits)

    luma_dc_bytes, luma_dc_pad, luma_dc_len = bits_to_bytes(luma_dc_coded)

    luma_ac_bytes = []
    luma_ac_len = []
    for bits in luma_ac_coded:
        bytes_data, pad, bitlen = bits_to_bytes(bits)
        luma_ac_bytes.append(bytes_data)
        luma_ac_len.append(bitlen)

    # Метаданные
    meta = {
        'image_size': image_size,
        'quality': quality,
        'dc_info': {
            'Y': {'padding': luma_dc_pad, 'bitlen': luma_dc_len},
        },
        'ac_info': {
            'Y': {'bitlens': luma_ac_len},
        }
    }

    meta_json = json.dumps(meta).encode('utf-8')
    meta_len = len(meta_json)

    packed = (
            struct.pack('I', meta_len) +
            meta_json +
            luma_dc_bytes +
            b''.join(luma_ac_bytes)
    )

    return packed

def unpacking_data_Y(packed):
    meta_len = struct.unpack('I', packed[:4])[0]
    meta_json = packed[4:4 + meta_len]
    meta = json.loads(meta_json.decode('utf-8'))

    data = packed[4 + meta_len:]
    pos = 0

    # Читаем DC компоненты
    def read_dc_component(component):
        info = meta['dc_info'][component]
        byte_len = (info['bitlen'] + 7) // 8
        bytes_data = data[pos:pos + byte_len]
        bits = ''.join(f'{byte:08b}' for byte in bytes_data)
        if info['padding'] > 0:
            bits = bits[:-info['padding']]
        return bits, byte_len

    luma_dc_bits, luma_dc_len = read_dc_component('Y')
    pos += luma_dc_len

    def read_ac_components(component):
        nonlocal pos
        ac_bits = []
        for bitlen in meta['ac_info'][component]['bitlens']:
            byte_len = (bitlen + 7) // 8
            bytes_data = data[pos:pos + byte_len]
            bits = ''.join(f'{byte:08b}' for byte in bytes_data)
            padding = (8 - bitlen % 8) % 8
            if padding > 0:
                bits = bits[:-padding]
            ac_bits.append(bits)
            pos += byte_len
        return ac_bits

    luma_ac_bits = read_ac_components('Y')

    return {
        'image_size': tuple(meta['image_size']),
        'quality': meta['quality'],
        'luma_dc': luma_dc_bits,
        'luma_ac': luma_ac_bits
    }