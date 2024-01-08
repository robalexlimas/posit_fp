from csv_analyzer.csv_analyzer import CSV_Complete
from draw.draw import Draw
from utils.args import args

from multiprocessing import Pool

import os


def list_csv(path):
    files = os.listdir(path)
    files = list(
        filter(
            lambda file: file.endswith('csv'),
            files
        )
    )
    return files


xlim_a = float(10 ** (-16))
xlim_b = float(10 ** 48)
xlim = (xlim_a, xlim_b)

ylim_a = float(10 ** (-16))
ylim_b = float(10 ** 48)
ylim = (ylim_a, ylim_b)


def call_pool(file):
    CSV_Complete(file)
    draw = Draw(file)
    draw.save_abs(ylim=ylim)
    draw.save_bit_field_accumulative()
    draw.save_relative(ylim=ylim)
    draw.save_bit_field()
    draw.save_block_location(xlim=xlim)
    draw.save_block_location(stuckat='1', xlim=xlim)
    draw.save_block_location(stuckat='0', xlim=xlim)
    draw.save_block_location_relative(xlim=xlim)
    draw.save_block_location_relative(stuckat='1', xlim=xlim)
    draw.save_block_location_relative(stuckat='0', xlim=xlim)


def main():
    files = list_csv(args.results_folder)
    with Pool(processes=args.workers) as pool:
        results = pool.map_async(call_pool, files)
        results.wait()


if __name__ == '__main__':
    main()
