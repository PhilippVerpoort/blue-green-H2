#!/usr/bin/env python
from pathlib import Path

from src.dump_params import dump_params
from src.load import load_inputs


DUMPDIR = Path(__file__).parent / 'dump'


# load required data and dump into Excel spreadsheet
def dump():
    # load inputs and outputs
    inputs = {}
    load_inputs(inputs)

    # set file path for dumping
    DUMPDIR.mkdir(parents=True, exist_ok=True)
    file_path = Path(__file__).parent / 'dump' / 'parameters.xlsx'

    # call dump function
    dump_params(inputs, file_path)


# call dump function when running as script
if __name__ == '__main__':
    dump()
