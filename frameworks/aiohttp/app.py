import time
from uuid import uuid4

from aiohttp.web import (
    RouteTableDef, Application, Response, json_response, HTTPBadRequest, HTTPUnauthorized)

from importlib.metadata import version, PackageNotFoundError
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import FileOutput, EmissionsData

def save_versions_txt(lib, filepath="/results/version.txt"):
    with open(filepath, "w") as f:
        try:
            f.write(f"{lib}=={version(lib)}\n")
        except PackageNotFoundError:
            f.write(f"{lib}==NOT INSTALLED\n")

save_versions_txt("aiohttp")


routes = RouteTableDef()


# first add ten more routes to load routing system
# ------------------------------------------------
async def req_ok(request):
    return Response(text='ok')

for n in range(5):
    routes.get(f"/route-{n}")(req_ok)
    routes.get(f"/route-dyn-{n}/{{part}}")(req_ok)


# then prepare endpoints for the benchmark
# ----------------------------------------
@routes.get('/html')
async def html(request):
    """Return HTML content and a custom header."""
    content = "<b>HTML OK</b>"
    headers = {'x-time': f"{time.time()}"}
    return Response(text=content, content_type="text/html", headers=headers)

@routes.get('/save')
async def save(request):
    """Return HTML content and a custom header."""
    tracker.stop()
    content = "<b>SAVED OK</b>"
    headers = {'x-time': f"{time.time()}"}
    return Response(text=content, content_type="text/html", headers=headers)


@routes.post('/upload')
async def upload(request):
    """Load multipart data and store it as a file."""
    if not request.headers['content-type'].startswith('multipart/form-data'):
        raise HTTPBadRequest()

    reader = await request.multipart()
    data = await reader.next()
    if data.name != 'file':
        raise HTTPBadRequest()

    with open(f"/tmp/{uuid4().hex}", 'wb') as target:
        target.write(await data.read())

    return Response(text=target.name, content_type="text/plain")


@routes.put(r'/api/users/{user:\d+}/records/{record:\d+}')
async def api(request):
    """Check headers for authorization, load JSON/query data and return as JSON."""
    if not request.headers.get('authorization'):
        raise HTTPUnauthorized()

    return json_response({
        'params': {
            'user': int(request.match_info['user']),
            'record': int(request.match_info['record']),
        },
        'query': dict(request.query),
        'data': await request.json(),
    })

class CustomOutput(FileOutput):
    def live_out(self, total: EmissionsData, delta: EmissionsData):
        self.out(total, delta)

tracker = OfflineEmissionsTracker(
    output_dir="/results",  # ou outro caminho acessível
    log_level="info",
    output_handlers=[CustomOutput(output_file_name="emissions.csv",output_dir="/results")],
)
tracker.start()
app = Application()
app.add_routes(routes)
