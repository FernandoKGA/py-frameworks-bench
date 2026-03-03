import json
import time
from uuid import uuid4

import uvloop
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import access_log
from tornado.web import Application, url, RequestHandler
from codecarbon import OfflineEmissionsTracker
from codecarbon.output import FileOutput, EmissionsData
from importlib.metadata import version, PackageNotFoundError

def save_versions_txt(lib, filepath="/results/version.txt"):
    with open(filepath, "w") as f:
        try:
            f.write(f"{lib}=={version(lib)}\n")
        except PackageNotFoundError:
            f.write(f"{lib}==NOT INSTALLED\n")

save_versions_txt("tornado")

class CustomOutput(FileOutput):
    def live_out(self, total: EmissionsData, delta: EmissionsData):
        self.out(total, delta)

tracker = OfflineEmissionsTracker(
    output_dir="/results",  # ou outro caminho acessível
    log_level="info",
    output_handlers=[CustomOutput(output_file_name="emissions.csv",output_dir="/results")],
)
tracker.start()

class SAVE(RequestHandler):

    async def get(self, part=None):
        tracker.stop()
        self.write("<b>SAVE OK</b>")
        self.add_header('x-time', f"{time.time()}")

class HTML(RequestHandler):

    async def get(self, part=None):
        self.write("<b>HTML OK</b>")
        self.add_header('x-time', f"{time.time()}")


class Upload(RequestHandler):

    async def post(self):
        if 'file' not in self.request.files:
            return self.set_status(400)
        data = self.request.files['file'][0]
        with open(f"/tmp/{uuid4().hex}", 'wb') as target:
            target.write(data['body'])

        self.set_header('content-type', 'text/plain')
        self.write(target.name)


class API(RequestHandler):

    async def put(self, user, record):
        if not self.request.headers.get('authorization'):
            return self.set_status(401)

        query = {n: v[0].decode() for n, v in self.request.arguments.items()}
        self.write({
            'params': {
                'user': int(user),
                'record': int(record),
            },
            'query': query,
            'data': json.loads(self.request.body),
        })


urls = [url(f"/route-{n}", HTML) for n in range(5)]
urls += [url(f"/route-dyn-{n}/(.*)", HTML) for n in range(5)]

app = Application(urls + [
    url('/html', HTML),
    url('/save', SAVE),
    url('/upload', Upload),
    url('/api/users/([^/]+)/records/(.+)', API),
])


# Start the application
if __name__ == '__main__':
    uvloop.install()
    server = HTTPServer(app)
    server.bind(8080, reuse_port=True)
    server.start()
    access_log.setLevel('ERROR')
    IOLoop.current().start()
