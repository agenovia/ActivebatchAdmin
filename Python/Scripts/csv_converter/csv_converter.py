import io
import re
from os import scandir

import pandas as pd
from pandas.errors import ParserError


def csv_converter(filename):
    newlines = []
    regex = re.compile('(?<!=)\"')  # negative lookbehind with = as the element and " as the match

    with open(filename, 'r') as infile:
        for idx, line in enumerate(infile):
            if idx == 0:  # leave header unchanged
                newline = line
            elif idx == 1:  # this is the second row of dashes; discard
                continue
            else:
                # funky stuff to make the delimiters correct; data is unclean
                newline = regex.sub('', line).replace(',', '').replace('="', ',')

            newlines.append(newline)

    # stuff into a file-like object in memory
    file_obj = io.StringIO()
    file_obj.writelines(newlines)
    file_obj.seek(0)

    try:
        df = pd.read_csv(file_obj, delimiter=',')
        df.to_excel(filename.replace('.csv', '.xlsx'), index=False)
    except ParserError as e:
        print(e)
        print(filename)
        print(newlines[4])
        raise


def convert_files(filepath):
    for file in scandir(filepath):
        if file.name.endswith('.csv'):
            csv_converter(file.path)


if __name__ == '__main__':
    pass
