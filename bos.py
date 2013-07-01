"""BOS format writer"""
import csv
import os


ENCODING_STRING = "Het BOS is extreem gaaf ! NS Rules !"
LEN_ENC_STR = len(ENCODING_STRING)


def xor_c(a):
    return bytearray([b^ord(ENCODING_STRING[i % LEN_ENC_STR]) for i, b in enumerate(bytearray(a))])


def make_runfile(module_name):
    with open('%s.run' % module_name, 'w') as f:
        f.write('some dummy content')


def remove_runfile(module_name):
    os.remove('%s.run' % module_name)


class BosFile(object):
    """BOS format file writer. 

    Behaves somewhat like csv.writer and uses its functions. Sorts its rows by
    date.
    """
    def __init__(self, filename):
        self.filename = filename
        self.rows = []
        self.temp_filename = 'tmp.csv'  # storage in plain csv

    def __enter__(self):
        return self

    def header(self):
        basename = os.path.basename(self.filename)
        return basename.split('.')[0]  # i.e. DS_RD_GW_HT

    def add_row(self, date_str, time_str, value):
        self.rows.append([date_str, time_str, '%0.5f' % value])

    def __exit__(self, a, b, c):
        rows_sorted = self.rows
        rows_sorted.sort()
        # add header
        rows_sorted.insert(0, ['DATE', 'TIME', self.header()])

        # write csv
        with open(self.temp_filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(rows_sorted)

        # convert csv to bin
        with open(self.temp_filename, 'rb') as input_csv:
            csv_bytes = input_csv.read()

        with open(self.filename, 'wb') as output_bin:
            output_bin.write(xor_c(csv_bytes))