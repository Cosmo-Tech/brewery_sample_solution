import os
from cosmotech.coal.utils.configuration import Configuration
from pathlib import Path


def main():
    _conf = Configuration()

    pf = os.listdir(_conf.cosmotech.dataset_absolute_path)
    print(pf)

    param_path = Path(_conf.cosmotech.parameters_absolute_path)
    df = os.listdir(param_path)
    print(df)
    for f in df:
        print(f)
        print((param_path / f).stat().st_size)


if __name__ == "__main__":
    main()
