from log.logger import logger
from utils.args import args


from ast import literal_eval


import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


sns.set(
    font='Times New Roman',
    font_scale=3
)
sns.set_theme(style='whitegrid', palette='pastel')


class Draw(object):
    def __init__(self, filename):
        self.__filename = filename.split('.csv')[0]
        self.__results = os.path.join(
            args.results_folder,
            filename.split('.csv')[0]
        )
        self.__path = os.path.join(
            args.results_folder,
            filename.split('.csv')[0],
            filename.split('.csv')[0] + '_clean.csv'
        )
        logger.info(f'Paths\n{self.__path}\n{self.__results}')
        self.__df = pd.read_csv(self.__path)

    
    def save_abs(self):
        logger.info(f'Saving absolute error for {self.__filename}')
        fig, ax = self.__create_fig()
        boxplot = sns.boxplot(
            data=self.__df,
            x='bit_changed_num',
            y='abs',
            ax=ax
        )
        ax.set(
            xlabel='Bit',
            ylabel='Absolute Error'
        )
        ax.set_yscale('log')
        ax.grid(False)
        boxplot.invert_xaxis()
        self.__save(fig, f'abs')

    
    def save_relative(self):
        logger.info(f'Saving relative error for {self.__filename}')
        fig, ax = self.__create_fig()
        boxplot = sns.boxplot(
            data=self.__df,
            x='bit_changed_num',
            y='relative',
            ax=ax
        )
        ax.set(
            xlabel='Bit',
            ylabel='Relative Error'
        )
        ax.set_yscale('log')
        ax.grid(False)
        boxplot.invert_xaxis()
        self.__save(fig, f'relative')
        del boxplot

    
    def save_bit_field_accumulative(self):
        logger.info(f'Saving bit field acumulative for {self.__filename}')
        bit_changes = self.__df.groupby(
            by=['bit_changed_num']
        ).count()
        bit_changes = bit_changes.reset_index().loc[:, ['classification', 'format']]
        bit_changes['format'] = bit_changes['format'] / bit_changes['format'].sum()
        bit_changes['index'] = bit_changes.index

        fig, ax = self.__create_fig()
        barplot = sns.barplot(
            data=bit_changes,
            x='index',
            y='format',
            ax=ax
        )
        ax.set(
            xlabel='Bit',
            ylabel='Bit field'
        )
        ax.set_yscale('log')
        ax.grid(False)
        barplot.invert_xaxis()
        self.__save(fig, f'accumulative')
        del bit_changes
        del barplot
    

    def save_bit_field(self):
        logger.info(f'Saving bit field for {self.__filename}')
        bit_changes = self.__df.loc[:, ['bits_changed_num', 'format']]
        bit_changes['total'] = bit_changes['bits_changed_num'].apply(
            lambda bits: len(literal_eval(bits))
        )
        bit_changes = bit_changes.groupby(
            by=['total']
        ).count()
        bit_changes = bit_changes.reset_index()
        bit_changes['format'] = bit_changes['format'] / bit_changes['format'].sum()
        bit_changes['index'] = bit_changes.index

        fig, ax = self.__create_fig()
        barplot = sns.barplot(
            data=bit_changes,
            x='index',
            y='format',
            ax=ax
        )
        ax.set(
            xlabel='Bit',
            ylabel='Bit field'
        )
        ax.grid(False)
        self.__save(fig, f'bit_field')
        del bit_changes
        del barplot

    def save_heatp_map(self, stuckat=None):
        logger.info(f'Saving heatmap for {self.__filename}')
        fault_stimuli = self.__heat_map_data(stuckat)
        fig, ax = self.__create_fig()

        hist = fault_stimuli.reset_index().pivot(
            index='id', 
            columns='stimuli', 
            values='format'
        )
        hist.sort_index(level=1, ascending=True, inplace=True)

        histogram = sns.heatmap(
            hist,
            cmap='seismic',
            ax=ax,
            vmin=0,
            vmax=1,
            cbar=False
        )
        histogram.set_xlabel('Stimuli')
        histogram.set_ylabel('Net location')
        histogram.grid(False)

        filename = f'heat_map' if not stuckat else f'heat_map_{stuckat}'
        self.__save(fig, filename)
        del histogram
        del hist
        del fault_stimuli


    def save_block_location(self, stuckat=None):
        logger.info(f'Saving block location for {self.__filename}')
        fault_stimuli = self.__block_data(stuckat)
        fig, ax = self.__create_fig()

        scatter = sns.scatterplot(
            data=fault_stimuli,
            x='abs',
            y='block_name',
            ax=ax
        )
        ax.set_xscale('log', base=2)
        scatter.set_xlabel('Absolute error')
        scatter.set_ylabel('Block location')
        scatter.grid(False)

        filename = f'block_location' if not stuckat else f'block_location_{stuckat}'
        self.__save(fig, filename)
        del scatter
        del fault_stimuli


    def save_error_density(self):
        logger.info(f'Saving density distribution error for {self.__filename}')
        fig, ax = self.__create_fig()

        displot = sns.kdeplot(
            data=self.__df,
            x='abs',
            hue='stuckat'
        )

        ax.set_xscale('log', base=2)
        displot.set_xlabel('Absolute error')
        displot.set_ylabel('Density')
        displot.grid(False)

        filename = f'density_stuckat'
        self.__save(fig, filename)

        fig, ax = self.__create_fig()
        displot = sns.kdeplot(
            data=self.__df,
            x='abs'
        )

        ax.set_xscale('log', base=2)
        displot.set_xlabel('Absolute error')
        displot.set_ylabel('Density')
        displot.grid(False)

        filename = f'density'
        self.__save(fig, filename)
        del displot


    def __block_data(self, stuckat=None):
        if stuckat:
            fault_stimuli = self.__df[self.__df['stuckat'] == int(stuckat)]
        else:
            fault_stimuli = self.__df
        fault_stimuli = fault_stimuli.groupby(
            by=['block_name', 'abs'], as_index=False
        ).count()
        return fault_stimuli

    
    def __heat_map_data(self, stuckat=None):
        if stuckat:
            fault_stimuli = self.__df[self.__df['stuckat'] == int(stuckat)]
        else:
            fault_stimuli = self.__df
        fault_stimuli = fault_stimuli.groupby(
            by=['id', 'stimuli'], as_index=False
        ).count()
        fault_stimuli['id'] = fault_stimuli['id'].apply(int)
        return fault_stimuli


    def __create_fig(self):
        fig, ax = plt.subplots(figsize=(9, 6))
        fig.tight_layout(pad=10)
        return fig, ax


    def __save(self, fig, filename):
        fig.savefig(
            f'{self.__results}/{filename}.pdf', format='pdf'
        )
        fig.savefig(
            f'{self.__results}/{filename}.jpg', format='jpg'
        )
    