import os
from pathlib import Path
import json
from types import SimpleNamespace
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
barPath = dataPath / "Bar.csv"
parametersPath = Path(os.environ["CSM_PARAMETERS_ABSOLUTE_PATH"])
parametersFile = parametersPath / "parameters.json"
if parametersFile.exists():
  with open(parametersFile, 'r') as f:
    parameters = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
  pValues = parameters.parametersValues
  stockParam = getValue(pValues, "stock")
  stock = stockParam.value
  restockQtyParam = getValue(pValues, "restock_qty")
  restock = restockQtyParam.value
  nbWaitersParam = getValue(pValues, "nb_waiters")
  nbWaiters = nbWaitersParam.value
  tempfile = NamedTemporaryFile('w+t', newline='', delete=False)
  with open(barPath, newline='') as csvfile:
    barReader = csv.reader(csvfile)
    barWriter = csv.writer(tempfile)
    line = 0
    for row in barReader:
      if line > 0:
        oldNbWaitersValue = row[0]
        row[0] = nbWaiters
        print(oldNbWaitersValue + "=>" + nbWaiters)
        oldRestockValue = row[1]
        row[1] = restock
        print(oldRestockValue + "=>" + restock)
        oldStockValue = row[2]
        row[2] = stock
        print(oldStockValue + "=>" + stock)
        print(row)
      barWriter.writerow(row)
      line = line + 1
  shutil.move(tempfile.name, barPath)
else:
  print(f"No parameters file in {parametersFile}")