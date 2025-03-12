#!/usr/bin/env python3
import io
import json
import shutil
import zipfile
from pathlib import Path

import click
import requests
from tira.rest_api_client import Client
from tqdm import tqdm


def persist(output_dir, endpoint, force_refresh=False):
    out = output_dir / Path(endpoint[1:])
    if endpoint.endswith('/'):
        out = out / 'index.json'
    out.parent.mkdir(exist_ok=True, parents=True)

    if out.exists() and not force_refresh:
        return json.load(open(out, 'r'))

    tira = Client()
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

    extract_zip_from_url('https://github.com/tira-io/tira/releases/download/0.0.136-pt_artifacts-0.0.48/frontend-build.zip', output_dir)
    shutil.copyfile(output_dir / "index.html", output_dir / "404.html")

    persist(output_dir, "/api/role")
    persist(output_dir, "/info", force_refresh=True)
    persist(output_dir, "/.well-known/tira/client", force_refresh=True)
    persist(output_dir, "/v1/datasets/all", force_refresh=True)
    systems = persist(output_dir, "/v1/systems/all", force_refresh=True)

    SYSTEMS_TO_SAVE = set(['ir-benchmarks'])
    systems_to_load = []
    for system in systems:
        if system['type'] == 'Docker' and any(i in SYSTEMS_TO_SAVE for i in system['tasks']) and ('tira-ir-starter' in system["name"] or 'qpptk' in system["name"] or 'ows' in system["name"] or 'fschlatt' in system["name"]):
            systems_to_load.append(f'/v1/systems/{system["team"]}/{system["name"]}')

    for system in tqdm(systems_to_load):
        persist(output_dir, system)

    tasks = persist(output_dir, "/api/task-list", force_refresh=True)['context']['task_list']
    for task in tqdm(tasks, "Persist tasks"):
        task_id = task["task_id"]

        persist(output_dir, f'/api/task/{task_id}/')
        datasets = persist(output_dir, f'/api/datasets_by_task/{task_id}')['context']['datasets']
        persist(output_dir, f"/api/task/{task_id}/public-submissions")
        
        for dataset in json.loads(datasets).keys():
            persist(output_dir, f'/api/evaluations/{task_id}/{dataset}')


if __name__ == '__main__':
    main()

