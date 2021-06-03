import os
from pathlib import Path
import glob
dataPath = Path(os.environ["CSM_DATASET_ABSOLUTE_PATH"])
files = glob.glob(str(dataPath / "**"), recursive=True)
print(files)