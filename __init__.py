from csv_analyzer.csv_analyzer import CSV_Complete
from draw.draw import Draw
from utils.args import args

from multiprocessing import Pool

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def list_csv(path):
    files = os.listdir(path)
    files = list(
        filter(
            lambda file: file.endswith('csv'),
            files
        )
    )
    return files


def call_pool(file):
    CSV_Complete(file)
    draw = Draw(file)
    draw.save_abs()
    draw.save_bit_field_accumulative()
    draw.save_heatp_map()
    draw.save_heatp_map('0')
    draw.save_heatp_map('1')
    draw.save_relative()
    draw.save_bit_field()
    draw.save_block_location()
    draw.save_block_location('1')
    draw.save_block_location('0')
    draw.save_error_density()


def main():
    files = list_csv(args.results_folder)
    with Pool(processes=args.workers) as pool:
        results = pool.map_async(call_pool, files)
        results.wait()


if __name__ == '__main__':
    main()
