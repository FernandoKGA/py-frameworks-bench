import time
from uuid import uuid4

from baize.asgi import (HTMLResponse, JSONResponse, PlainTextResponse, Request, Response, Router,
                        request_response)
from baize.exceptions import HTTPException
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import FileOutput, EmissionsData
from importlib.metadata import version, PackageNotFoundError

def save_versions_txt(lib, filepath="/results/version.txt"):
    with open(filepath, "w") as f:
        try:
            f.write(f"{lib}=={version(lib)}\n")
        except PackageNotFoundError:
            f.write(f"{lib}==NOT INSTALLED\n")

save_versions_txt("baize")

class CustomOutput(FileOutput):
    def live_out(self, total: EmissionsData, delta: EmissionsData):
        self.out(total, delta)

tracker = OfflineEmissionsTracker(
    output_dir="/results",  # ou outro caminho acessível
    log_level="info",
    output_handlers=[CustomOutput(output_file_name="emissions.csv",output_dir="/results")],
)
tracker.start()

routes = []

# first add ten more routes to load routing system
# ------------------------------------------------
for n in range(5):
    routes.append((f"/route-{n}", HTMLResponse("ok")))
    routes.append((f"/route-dyn-{n}/{{part}}", HTMLResponse("ok")))


# then prepare endpoints for the benchmark
# ----------------------------------------
@request_response
async def html(request: Request) -> Response:
    """Return HTML content and a custom header."""
    content = "<b>HTML OK</b>"
    headers = {"x-time": f"{time.time()}"}
    return HTMLResponse(content, headers=headers)

@request_response
async def save(request: Request) -> Response:
    """Return HTML content and a custom header."""
    tracker.stop()
    content = "<b>Saved OK</b>"
    headers = {"x-time": f"{time.time()}"}
    return HTMLResponse(content, headers=headers)


@request_response
async def upload(request: Request) -> Response:
    """Load multipart data and store it as a file."""
    if request.method != "POST":
        return Response(405)

    try:
        formdata = await request.form
    except HTTPException as exc:
        return Response(exc.status_code, exc.headers)

    if "file" not in formdata:
        return PlainTextResponse("ERROR", status_code=400)

    filepath = f"/tmp/{uuid4().hex}"
    await formdata["file"].asave(filepath)

    return PlainTextResponse(filepath)


@request_response
async def api(request: Request) -> Response:
    """Check headers for authorization, load JSON/query data and return as JSON."""
    if request.method != "PUT":
        return Response(405)

    if request.headers.get("authorization") is None:
        return PlainTextResponse("ERROR", status_code=401)

    return JSONResponse(
        {
            "params": request.path_params,
            "query": dict(request.query_params),
            "data": await request.json,
        }
    )


app = Router(
    ("/html", html),
    ("/save", save),
    ("/upload", upload),
    ("/api/users/{user:int}/records/{record:int}", api),
    *routes,
)
