#!/usr/bin/env python
import sys

from webapp import webapp


# get list of figs to plot from command line args and call webapp.export()
def export():
    if len(sys.argv) > 1:
        fig_names = sys.argv[1:]
    else:
        fig_names = None

    webapp.export(fig_names, export_formats=['png', 'svg', 'pdf'])


# call export function when running as script
if __name__ == '__main__':
    export()
