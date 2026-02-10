from cosmotech.coal.utils.configuration import Configuration
from pathlib import Path

# Function 'tree' retrived from StackOverflow
#   modified to print file size
# Source - https://stackoverflow.com/a/59109706
# Posted by Aaron Hall, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-15, License - CC BY-SA 4.0


def tree(dir_path: Path, prefix: str = ''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # prefix components:
    space =  '    '
    branch = '│   '
    # pointers:
    tee =    '├── '
    last =   '└── '

    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        size = ""
        if path.is_file():
            size = f": {path.stat().st_size}o"
        yield prefix + pointer + path.name + size
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)


def dprint(line):
    pre = '[debug]'
    print(f"{pre} {line}")


def main():
    _conf = Configuration()

    param_path = Path(_conf.cosmotech.parameters_absolute_path)
    dprint("parameter.json:")
    with open(param_path / "parameters.json") as f:
        print(f.read())

    dprint(f"Printing {param_path.resolve()} content:")
    for line in tree(param_path):
        dprint(line)

    data_path = Path(_conf.cosmotech.dataset_absolute_path)
    dprint(f"Printng {data_path.resolve()} content:")
    for line in tree(data_path):
        dprint(line)


if __name__ == "__main__":
    main()
