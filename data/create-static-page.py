#!/usr/bin/env python3
import click
from pathlib import Path
from tira.rest_api_client import Client
from tqdm import tqdm
import json


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

def persist(output_dir, endpoint):
    tira = Client()
    out = output_dir / Path(endpoint[1:])
    out.mkdir(exist_ok=True, parents=True)

    response = tira.json_response(endpoint)

    with open(out / 'index.json', 'w') as f:
        f.write(json.dumps(response))

    return response

@click.command('create-static-page')
@click.argument('output_dir', type=Path)
def main(output_dir: Path):
    output_dir.mkdir(exist_ok=True, parents=True)
    with open(output_dir / 'index.html', 'w') as f:
        f.write(html())

    (output_dir / 'tira-data').mkdir(exist_ok=True, parents=True)
    with open(output_dir / 'tira-data' / 'index.html', 'w') as f:
        f.write(html())
    print(output_dir)
    tasks = persist(output_dir, "/api/task-list")['context']['task_list']
    for task in tqdm(tasks, 'Persist tasks'):
        datasets = persist(output_dir, f'/api/datasets_by_task/{task["task_id"]}')

if __name__ == '__main__':
    main()

