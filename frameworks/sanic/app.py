import time
from uuid import uuid4

from sanic import Sanic
from sanic.response import html, json, text
from sanic.exceptions import Unauthorized, InvalidUsage
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import FileOutput, EmissionsData
from importlib.metadata import version, PackageNotFoundError

def save_versions_txt(lib, filepath="/results/version.txt"):
    with open(filepath, "w") as f:
        try:
            f.write(f"{lib}=={version(lib)}\n")
        except PackageNotFoundError:
            f.write(f"{lib}==NOT INSTALLED\n")

save_versions_txt("sanic")

class CustomOutput(FileOutput):
    def live_out(self, total: EmissionsData, delta: EmissionsData):
        self.out(total, delta)

tracker = OfflineEmissionsTracker(
    output_dir="/results",  # ou outro caminho acessível
    log_level="info",
    output_handlers=[CustomOutput(output_file_name="emissions.csv",output_dir="/results")],
)
tracker.start()

app = Sanic("benchmark")


# first add ten more routes to load routing system
# ------------------------------------------------
async def req_ok(request, part=None):
    return html('ok')


for n in range(5):
    app.route(f"/route-{n}")(html)
    app.route(f"/route-dyn-{n}/<part>")(req_ok)


# then prepare endpoints for the benchmark
# ----------------------------------------
@app.route('/html')
async def view_html(request):
    """Return HTML content and a custom header."""
    content = "<b>HTML OK</b>"
    headers = {'x-time': f"{time.time()}"}
    return html(content, headers=headers)

@app.route('/save')
async def view_save(request):
    """Return HTML content and a custom header."""
    tracker.stop()
    content = "<b>SAVED OK</b>"
    headers = {'x-time': f"{time.time()}"}
    return html(content, headers=headers)


@app.route('/upload', methods=['POST'])
async def upload(request):
    """Load multipart data and store it as a file."""
    if 'file' not in request.files:
        raise InvalidUsage('ERROR')

    with open(f"/tmp/{uuid4().hex}", 'wb') as target:
        target.write(request.files['file'][0].body)
    return text(target.name)


@app.route('/api/users/<user:int>/records/<record:int>', methods=['PUT'])
async def api(request, user, record):
    """Check headers for authorization, load JSON/query data and return as JSON."""
    if request.headers.get('authorization') is None:
        raise Unauthorized('ERROR')
    return json({
        'params': {'user': user, 'record': record},
        'query': dict(request.query_args),
        'data': request.json
    })
