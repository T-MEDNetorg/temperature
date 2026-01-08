import excel_writer as ew
import os

directory = os.fsencode('../src/input_files/Subidos/')

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".txt"):
        print('Gotta do ' + filename)
        er = ew.ExcelReport('../src/input_files/Subidos/' + filename)
        er.excel_writer()

    else:
        print('not doable ' + filename)

