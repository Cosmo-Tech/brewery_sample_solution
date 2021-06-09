import os
from pathlib import Path
import logging
import csv
from tempfile import NamedTemporaryFile
import shutil
import glob


def getValue(values, searchId):
    for v in values:
        if searchId == v.parameterId:
            return v
    logging.warning("Parameter not found")


dataPath = Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])
files = glob.glob(str(dataPath / "**"), recursive=True)
print(files)
barPath = dataPath / "demobrewery/Bar.csv"
parametersPath = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
parametersFile = parametersPath / "parameters.csv"
if parametersFile.exists():
    stock = 0
    restock = 0
    nbWaiters = 0
    with open(parametersFile, 'r') as csvfile:
        parametersReader = csv.reader(csvfile)
        print('Start reading parameters.csv file')
        for row in parametersReader:
            print(row)
            if row[0] == 'stock':
                print('stock read', row[1])
                stock = row[1]
            if row[0] == 'restock_qty':
                print('restock_qty read', row[1])
                restock = row[1]
            if row[0] == 'nb_waiters':
                print('nb_waiters read', row[1])
                nbWaiters = row[1]

    tempfile = NamedTemporaryFile('w+t', newline='', delete=False)

    with open(barPath, newline='') as barFile:
        barReader = csv.reader(barFile)
        barWriter = csv.writer(tempfile)
        line = 0
        for row in barReader:
            if line > 0:
                oldNbWaitersValue = row[0]
                row[0] = nbWaiters
                print(oldNbWaitersValue, "=>", nbWaiters)
                oldRestockValue = row[1]
                row[1] = restock
                print(oldRestockValue, "=>", restock)
                oldStockValue = row[2]
                row[2] = stock
                print(oldStockValue, "=>", stock)
            barWriter.writerow(row)
            line = line + 1
    tempfile.close()
    shutil.move(tempfile.name, barPath)
else:
    print(f"No parameters file in {parametersFile}")
