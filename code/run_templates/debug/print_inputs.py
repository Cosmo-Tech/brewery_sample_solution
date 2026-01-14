import os
from cosmotech.coal.utils.configuration import Configuration
from pathlib import Path


def main():
    _conf = Configuration()

    param_path = Path(_conf.cosmotech.parameters_absolute_path)
    print(f"print {param_path.resolve()} content:")
    pf = os.listdir(param_path)
    print(pf)

    data_path = Path(_conf.cosmotech.dataset_absolute_path)
    print(f"print {data_path.resolve()} content:")
    df = os.listdir(data_path)
    print(df)
    for f in df:
        print(f)
        print((param_path / f).stat().st_size)


if __name__ == "__main__":
    main()
