#!/usr/bin/env python3
import click
from pathlib import Path
from tira.rest_api_client import Client
from tqdm import tqdm
import requests
import zipfile
import io
import json


def persist(output_dir, endpoint):
    tira = Client()
    out = output_dir / Path(endpoint[1:])
    if endpoint.endswith('/'):
        out = out / 'index.json'
    out.parent.mkdir(exist_ok=True, parents=True)

    response = tira.json_response(endpoint)

    with open(out, 'w') as f:
        f.write(json.dumps(response))

    return response

def extract_zip_from_url(url: str, to: Path) -> None:
    with requests.get(url, stream=True) as req:
        with zipfile.ZipFile(io.BytesIO(req.content)) as zip_ref:
            zip_ref.extractall(to)


@click.command('create-static-page')
@click.argument('output_dir', type=Path)
def main(output_dir: Path):
    print(output_dir)

    extract_zip_from_url('https://github.com/tira-io/tira/releases/latest/download/frontend-build.zip', output_dir)
    tasks = persist(output_dir, "/api/task-list")['context']['task_list']
    for task in tqdm(tasks, 'Persist tasks'):
        datasets = persist(output_dir, f'/api/datasets_by_task/{task["task_id"]}')

if __name__ == '__main__':
    main()

