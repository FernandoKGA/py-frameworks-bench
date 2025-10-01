import csv
import datetime as dt
import re
import statistics as st
from collections import OrderedDict, namedtuple
from pathlib import Path
import jinja2
import json

NOW = dt.datetime.utcnow()
BASEDIR = Path(__file__).parent.parent
FRAMEWORKS_DIR = BASEDIR / 'frameworks'
RESULTS_DIR = BASEDIR.glob("results_*")  # agora vai varrer todas as pastas de resultados
README = BASEDIR / 'README.md'
README_TEMPLATE = jinja2.Template((BASEDIR / 'render/README.md').read_text())
PAGES_HOME = BASEDIR / 'docs/index.md'
PAGES_HOME_TEMPLATE = jinja2.Template((BASEDIR / 'render/pages/index.md').read_text())
PAGES_RESULTS = BASEDIR / f"docs/_posts/{ NOW.strftime('%Y-%m-%d') }-results.md"
PAGES_RESULTS_TEMPLATE = jinja2.Template((BASEDIR / 'render/pages/results.md').read_text())

Result = namedtuple('Result', ['name', 'req', 'lt50', 'lt75', 'lt90', 'lt_avg', 'es', 'er', 'et'])

def load_csv(path: Path):
    with path.open() as csvfile:
        return [Result(name, round(int(req) / 15), *row) for name, req, *row in csv.reader(csvfile)]

def parse_version(name):
    base = name.split("-")[0]  # ex: fastapi from fastapi-0_110_0
    folder = FRAMEWORKS_DIR / name
    req_file = folder / 'requirements.txt'
    if not req_file.exists():
        return ''
    content = req_file.read_text()
    match = re.search(rf"{base}==([^\s]+)", content)
    return match.group(1) if match else ''

def render():
    results_html, results_upload, results_api = [], [], []

    for result_dir in RESULTS_DIR:
        name = result_dir.name.replace("results_", "")
        html_path = result_dir / "logs" / "html.csv"
        upload_path = result_dir / "logs" / "upload.csv"
        api_path = result_dir / "logs" / "api.csv"
        if not (html_path.exists() and upload_path.exists() and api_path.exists()):
            print(f"⚠️  Ignorando {result_dir} (faltam arquivos)")
            continue
        html = load_csv(html_path)
        upload = load_csv(upload_path)
        api = load_csv(api_path)
        if html and upload and api:
            results_html.append(html[0]._replace(name=name.replace("_", ".")))
            results_upload.append(upload[0]._replace(name=name.replace("_", ".")))
            results_api.append(api[0]._replace(name=name.replace("_", ".")))

    combined_results = [
        Result(
            r1.name, (r1.req + r2.req + r3.req) * 15,
            st.mean(map(float, [r1.lt50, r2.lt50, r3.lt50])),
            st.mean(map(float, [r1.lt75, r2.lt75, r3.lt75])),
            st.mean(map(float, [r1.lt90, r2.lt90, r3.lt90])),
            st.mean(map(float, [r1.lt_avg, r2.lt_avg, r3.lt_avg])),
            r1.es + r2.es + r3.es,
            r1.er + r2.er + r3.er,
            r1.et + r2.et + r3.et,
        )
        for r1, r2, r3 in zip(results_html, results_upload, results_api)
    ]

    ctx = dict(
        now=NOW,
        results_html=sorted(results_html, key=lambda res: res.name, reverse=False),
        results_upload=sorted(results_upload, key=lambda res: res.name, reverse=False),
        results_api=sorted(results_api, key=lambda res: res.name, reverse=False),
        results=sorted(combined_results, key=lambda res: res.name, reverse=False),
        versions={
            res.name: parse_version(res.name)
            for res in results_html
        },
    )

    render_template(README_TEMPLATE, README, **ctx)
    render_template(PAGES_HOME_TEMPLATE, PAGES_HOME, **ctx)
    render_template(PAGES_RESULTS_TEMPLATE, PAGES_RESULTS, **ctx)
    do_json(combined_results)

def render_template(template, target, **ctx):
    with open(target, 'w') as target_file:
        target_file.write(template.render(**ctx))

def do_json(results):
    json_result = {}
    name_file = ""
    for result in results:
        name, version = result.name.split(".", 1)
        json_result[version] = result.req
        name_file = name

    with open(f"docs/_posts/{name_file}.json", 'w') as target_file:
        target_file.write(json.dumps(OrderedDict(sorted(json_result.items()))))

if __name__ == '__main__':
    render()
