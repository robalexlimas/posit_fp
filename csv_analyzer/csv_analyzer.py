from log.logger import logger
from utils.args import args
from utils.utils import abs_error, convert_to_float, relative_error, max_bit_changed, bits_chaged, error_distance, relative_error_distance

import pandas as pd
import os, re


class CSV_Complete(object):
    def __init__(self, file, chunksize=10 ** 6):
        self.__file = file.split('.csv')[0]
        filepath = os.path.join(args.results_folder, file)
        self.__path = filepath
        logger.info(f'Reading {self.__path}')
        self.__df = pd.read_csv(self.__path)
        self.__chunksize = chunksize
        self.__clean()
    
    def __clean(self):
        logger.info(f'Cleaning {self.__path}')
        stimuli = self.__stimuli_to_analyze()
        net_list = self.__get_net_locations()
        del self.__df
        self.__clean_csv(stimuli, net_list)


    def __clean_csv(self, stimuli, net_list):
        csv_folder = os.path.join(
            args.results_folder,
            self.__file
        )
        os.makedirs(csv_folder, exist_ok=True)
        clean_csv = os.path.join(
            args.results_folder,
            self.__file,
            self.__file + '_clean.csv'
        )
        logger.info(f'Saving csv file clean {clean_csv}')
        iterator = pd.read_csv(self.__path, chunksize=self.__chunksize)
        for chunk in iterator:
            for sti in stimuli:
                df = chunk.loc[(chunk['stimuli'] == sti) & (chunk['time'] == stimuli[sti])]
                df.drop(df[df['stimuli'] == 0].index, inplace=True)
                
                if not df.empty:
                    df.drop(['strobe'], axis=1, inplace=True)

                    df['golden_float'] = df.apply(
                        lambda d: convert_to_float(
                            d['golden'], d['format']
                        ),
                        axis=1
                    )
                    df['faulty_float'] = df.apply(
                        lambda d: convert_to_float(
                            d['faulty'], d['format']
                        ),
                        axis=1
                    )

                    df.dropna(inplace=True)
                    
                    df['bits_changed_num'] = df['bit_changed'].apply(
                        bits_chaged
                    )
                    df['bit_changed_num'] = df['bit_changed'].apply(
                        max_bit_changed
                    )

                    df['relative'] = df.apply(
                        lambda d: relative_error(
                            d['golden_float'], d['faulty_float']
                        ), axis=1
                    )
                    df['abs'] = df.apply(
                        lambda d: abs_error(
                            d['golden_float'], d['faulty_float']
                        ), axis=1
                    )
                    df['error_distance'] = df.apply(
                        lambda d: error_distance(
                            d['golden_float'], d['faulty_float']
                        ), axis=1
                    )
                    df['relative_error_distance'] = df.apply(
                        lambda d: relative_error_distance(
                            d['golden_float'], d['faulty_float']
                        ), axis=1
                    )

                    df['block_name'] = df['fault_location'].apply(
                        self.__build_block_name
                    )

                    for i, net in enumerate(net_list):
                        idxs = df[df['fault_location'] == net].index
                        df.loc[idxs, 'id'] = i

                    df.to_csv(
                        clean_csv,
                        mode='a',
                        index=False,
                        header=(not os.path.exists(clean_csv))
                    )


    def __get_net_locations(self):
        df = self.__df.loc[:, ['stimuli', 'fault_location']]
        df = df[df['stimuli'] == '0']
        net_list = df.groupby(
            by=['fault_location']
        ).count().reset_index()
        net_list = net_list['fault_location'].to_numpy()
        net_list.sort()
        net_list = list(set(net_list))
        logger.info(f'Net list for {self.__file}\n{dict(enumerate(net_list))}')
        return net_list
    
    
    def __build_block_name(self, block_name):
        pattern = r'U\d'
        name = []
        block_name = block_name.split('.')
        for split in block_name:
            if not re.findall(pattern, split):
                name.append(split)
            else:
                break
        for i, part in enumerate(name):
            if 'reg' in part:
                name[i] = 'Reg'
                return '.'.join(name[0: i+1])
            if 'tile_' in part:
                tile_num = part.split('_')[1]
                name[i] = f'Title{tile_num}'
                return '.'.join(name[0: i+1])
            if 'Compressor' in part:
                name[i] = 'Compressor'
                return '.'.join(name[0: i+1])
            if 'mult_' in part:
                name[i] = 'Mult'
                return '.'.join(name[0: i+1])
        name = '.'.join(name)
        return name


    def __stimuli_to_analyze(self):
        stimuli = {}
        df = self.__df.loc[:, ['stimuli', 'time']]
        df.drop(
            df[df['time'] == '--'].index,
            inplace=True
        )
        df = df.groupby(
            by=['stimuli', 'time']
        ).count().reset_index()
        df_temp = df.groupby(
            by=['stimuli']
        ).count().reset_index()
        df_temp.drop(
            df_temp[df_temp['time'] < 2].index,
            inplace=True
        )
        df_temp = df_temp['stimuli'].to_numpy()
        for _, row in df.iterrows():
            if row['stimuli'] in df_temp:
                if not row['stimuli'] in stimuli.keys():
                    stimuli[row['stimuli']] = row['time']
                else:
                    time = int(row['time'].split('ns')[0])
                    stimuli_time = int(stimuli[row['stimuli']].split('ns')[0])
                    if time < stimuli_time:
                        stimuli[row['stimuli']] = row['time']
        logger.info(f'Stimuli to analyze for {self.__path}\n{stimuli}')
        del df
        del df_temp
        return stimuli
