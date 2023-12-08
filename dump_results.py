#!/usr/bin/env python
from pathlib import Path

from src.dump_results import dump_results
from src.load import load_inputs
from src.proc import process_inputs


# load required data and dump into Excel spreadsheet
def dump():
    # load inputs and outputs
    inputs = {}
    outputs = {}
    load_inputs(inputs)
    process_inputs(inputs, outputs)

    # set file path for dumping
    file_path = Path(__file__).parent / 'dump' / 'results.xlsx'

    # call dump function
    print('Exporting results to spreadsheet...')
    dump_results(inputs, outputs, file_path)


# call dump function when running as script
if __name__ == '__main__':
    dump()
