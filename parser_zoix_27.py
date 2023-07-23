import json, os, sys
from ast import literal_eval


"""
example json structure
{
    data: {
        version: X.X,
        date: xx-xx-xxxxx,
        user: name.lastname,
        funtional_block: XXXXX,
        filename: XXXX
    },
    general: {
        type fault: #,
        ...
        total: #
    }
    faults: [
        {
            descriptor: PositAdder.FractionNormalizer.U239.A1,
            golden: XXXXX,
            faulty: XXXXX,
            changes: XXXX,
            classification: ND,
            fault: 0,
            strobe: XXXXX,
            time: XXXX
        },
        {
            descriptor: PositAdder.FractionNormalizer.U239.A1,
            golden: XXXXX,
            faulty: XXXXX,
            changes: XXXX,
            classification: ND,
            strobe: XXXXX,
            time: XXXX
        },
        ...
    ]
}
"""


class TextFileManager():
    def __init__(self, path):
        self.__lines = []
        if path:
            self.__filename = path.split('/')[-1]
            with open(path, 'r') as file:
                lines = file.readlines()
            self.__lines = self.__cleaner(lines)

    def __cleaner(self, lines):
        lines = [line.strip().replace('\n', '') for line in lines]
        lines = list(filter(lambda line: len(line) > 0, lines))
        return lines

    @property
    def lines(self):
        return self.__lines

    @lines.setter
    def lines(self, lines):
        if len(lines) > 0:
            self.__lines = self.__cleaner(lines)

    @property
    def filename(self):
        return self.__filename


id = {}
counter = 0


class ZoixParser(TextFileManager):
    def __init__(self, path, format, range, app, save):
        TextFileManager.__init__(self, path)
        self.__data = {
            'version': '',
            'date': '',
            'user': '',
            'funtional_block': '',
            'filename': self.filename,
            'strobe': {
                'name': '',
                'bits': 0
            }
        }
        self.__save = save
        self.__format = format
        self.__range = range
        self.__app = '_'.join(app.split('_')[:-1])
        self.__stimuli = app.split('_')[-1]
        self.__faults = []
        self.__classification = {}
        self.__parser()

    def __parser(self):
        if not self.__save:
            print('format,range,app,stimuli,id,fault_location,stuckat,classification,golden,faulty,bit_changed,strobe,time')
        fault_detected = False
        start_faults = False
        global id
        global counter
        for idx in range(len(self.lines)):
                line = self.lines[idx]
                if not '#' in line:
                    if 'Version' in line:
                        self.__data['version'] = line.split('"')[1]
                    elif 'Date' in line:
                        self.__data['date'] = line.split('"')[1]
                    elif 'User' in line:
                        self.__data['user'] = line.split('"')[1]
                    elif 'FunctionalBlocks' in line:
                        self.__data['funtional_block'] = self.lines[idx + 2].split(' ')[2]
                    elif 'StrobeData' in line:
                        self.__data['strobe']['name'] = self.lines[idx + 3].split(' ')[1].replace('"', '').replace(';', '')
                        self.__data['strobe']['bits'] = self.lines[idx + 3].split('[')[-1][:-3]
                    elif 'FaultList' in line:
                        start_faults = True
                    elif start_faults and not fault_detected and not '[' in line:
                        classification = line.split(' ')[0]
                        if classification == '--':
                            classification = self.__faults[-1]['classification']
                        fault = {
                                'descriptor': line.split(' ')[3].replace('"', '').replace('}', ''),
                                'golden': '',
                                'faulty': '',
                                'changes': '',
                                'classification': classification,
                                'strobe': self.__data['strobe']['name'],
                                'fault': line.split(' ')[1],
                                'time': '--'
                        }
                        if not line.split(' ')[3].replace('"', '').replace('}', '') in id.keys():
                            id[line.split(' ')[3].replace('"', '').replace('}', '')] = counter
                            counter += 1
                        if not 'CLK' in line.split(' ')[3].replace('"', '').replace('}', ''):
                            self.__faults.append(fault)
                            if not self.__save:
                                print(
                                    '{},{},{},{},{},{},{},{},{},{},{},{},{}'.
                                    format(
                                        self.__format,
                                        self.__range,
                                        self.__app,
                                        self.__stimuli,
                                        id[line.split(' ')[3].replace('"', '').replace('}', '')],
                                        line.split(' ')[3].replace('"', '').replace('}', ''),
                                        line.split(' ')[1],
                                        classification,
                                        '',
                                        '',
                                        '',
                                        self.__data['strobe']['name'],
                                        '--'
                                    )
                                )
                            if not classification in self.__classification:
                                self.__classification[classification] = 1
                            else:
                                self.__classification[classification] += 1
                    elif '[' in line and 'ns' in line:
                        fault_detected = True
                        time = line[1:-1]
                        golden_aux = []
                        faulty_aux = []
                    elif fault_detected and 'GM:' in line:
                        golden_aux.append(line.split('GM:')[-1].strip())
                    elif fault_detected and 'FM:' in line:
                        if ']' in line:
                            faulty_aux.append(line.split('FM:')[-1][:-2].strip())
                        else:
                            faulty_aux.append(line.split('FM:')[-1].strip())
                    elif fault_detected and len(line.split(' ')) > 1:
                        golden = ''.join(golden_aux)
                        faulty = ''.join(faulty_aux)
                        faulty_result = ''
                        for l, letter in enumerate(faulty):
                            if letter == '.':
                                faulty_result += golden[l]
                            else:
                                faulty_result += letter
                        fault_hexa = '0x' + faulty_result
                        golden_hexa = '0x' + golden
                        try:
                            bit_change = (hex(literal_eval(golden_hexa) ^ literal_eval(fault_hexa)))
                        except:
                            bit_change = ''
                        bit_change = bit_change.replace('L', '')
                        classification = line.split(' ')[0]
                        if classification == '--':
                            classification = self.__faults[-1]['classification']
                        fault = {
                                'descriptor': line.split(' ')[3].replace('"', '').replace('}', ''),
                                'golden': golden,
                                'faulty': faulty_result,
                                'changes': bit_change[2:],
                                'classification': classification,
                                'strobe': self.__data['strobe']['name'],
                                'fault': line.split(' ')[1],
                                'time': time
                        }
                        if not line.split(' ')[3].replace('"', '').replace('}', '') in id.keys():
                            id[line.split(' ')[3].replace('"', '').replace('}', '')] = counter
                            counter += 1
                        if not 'CLK' in line.split(' ')[3].replace('"', '').replace('}', ''):
                            if not classification in self.__classification:
                                self.__classification[classification] = 1
                            else:
                                self.__classification[classification] += 1
                            self.__faults.append(fault)
                            if not self.__save:
                                print(
                                    '{},{},{},{},{},{},{},{},{},{},{},{},{}'.
                                    format(
                                        self.__format,
                                        self.__range,
                                        self.__app,
                                        self.__stimuli,
                                        id[line.split(' ')[3].replace('"', '').replace('}', '')],
                                        line.split(' ')[3].replace('"', '').replace('}', ''),
                                        line.split(' ')[1],
                                        classification,
                                        golden,
                                        faulty_result,
                                        bit_change[2:],
                                        self.__data['strobe']['name'],
                                        time
                                    )
                                )
    
    def save(self, file_name):
        classification = self.__classification
        classification['total'] = sum([classification[fault] for fault in classification])
        data = {
            'data': self.__data,
            'general': self.__classification,
            'faults': self.__faults
        }
        with open(file_name, 'w') as json_file:
            json.dump(data, json_file)


def main(args):
    save = False
    path_dir = os.getcwd()
    if len(args) > 1:
        results_folder = os.path.join(path_dir, args[1])
    else:
        results_folder = os.path.join(path_dir, 'FP_add_GL_16_0.1')
    #formats = ['float', 'posit']
    formats = os.listdir(results_folder)
    for format in formats:
        path_format = os.path.join(results_folder, format)
        ranges = os.listdir(path_format)
        for range_ in ranges:
            path_apps = os.path.join(path_format, range_)
            apps = os.listdir(path_apps)
            for app in apps:
                path_app = os.path.join(path_apps, app)
                file_name = '{}_{}_{}'.format(format, range_, app)
                txt_file = os.path.join(path_app, 'saf_dic_long.txt')
                results_dir = os.path.join(path_app, '{}.json'.format(file_name))
                file = ZoixParser(txt_file, format, range_, app, save)
                if save:
                    file.save(results_dir)


if __name__ == '__main__':
    args = sys.argv
    main(args)
