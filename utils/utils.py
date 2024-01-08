from utils.args import args
from utils.formats import get_custom_format


from ast import literal_eval


import numpy as np


def convert_to_float(v, format):
    if not 'nan' in v:
        v = '0x' + v
        CustomData = get_custom_format(format + '32')
        data = CustomData(0.0)
        d_t = data.from_bits(literal_eval(v))
        t = float(d_t)
        return t
    return np.nan


def convert_hex_to_bin(v):
    return bin(literal_eval('0x' + v)).replace('0b', '')


def max_bit_changed(value):
    if '.' in str(value):
        value = str(str(value).split('.')[0])
    if not 'nan' in value:
        value_bin = convert_hex_to_bin(value)
        size = len(value_bin)
        missing = args.bits - size
        value_bin = '0' * missing + value_bin
        pos = args.bits - 1
        for bin_data in value_bin:
            if not bin_data == '1':
                pos -= 1
            else:
                return pos
    else:
        return np.nan
    

def bits_chaged(value):
    if '.' in str(value):
        value = str(str(value).split('.')[0])
    if not 'nan' in value:
        value_bin = convert_hex_to_bin(value)
        size = len(value_bin)
        missing = args.bits - size
        value_bin = '0' * missing + value_bin
        value_bin = value_bin[::-1]
        indexes = [
            index for index in range(len(value_bin))
            if value_bin.startswith('1', index)
        ]
        return indexes
    

def relative_error(real, fault):
    return np.abs(np.abs(real - fault) / real) * 100.0


def abs_error(real, fault):
    return np.abs(real - fault)


def num_bits_changed(bits_):
    return len(bits_)

def error_distance(golden, corrupted):
    return np.abs(corrupted - golden)


def squared_error(golden, corrupted):
    return (corrupted - golden) ** 2


def relative_error_distance(golden, corrupted):
    golden_div = 1.0 if golden == 0.0 else golden
    return (np.abs(corrupted - golden) / golden_div)


def mean_error_distance(error_distances):
    return np.mean(error_distances)


def mean_relative_error_distance(relative_errors):
    return np.mean(relative_errors)


def mean_squared_error(squared_errors):
    return np.mean(squared_errors)


def worst_case_error(error_distances):
    return np.max(error_distances)
