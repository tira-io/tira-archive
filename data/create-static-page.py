#!/usr/bin/env python3
import click
from pathlib import Path


def html():
        return f"""
<!DOCTYPE html>
<html>
<head>
<title>data.tira.io</title>
</head>
<body>
<h1>data.tira.io</h1>
Data api for <a href="https://tira.io">TIRA.io</a> (currently in alpha).
</body>
</html>"""


@click.command('create-static-page')
@click.argument('output_dir', type=Path)
def main(output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)
    with open(output_dir / 'index.html', 'w') as f:
        f.write(html())

    (output_dir / 'tira-data').mkdir(exist_ok=True, parents=True)
    with open(output_dir / 'tira-data' / 'index.html', 'w') as f:
        f.write(html())

if __name__ == '__main__':
    main()

