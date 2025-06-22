from django.core.asgi import get_asgi_application
from django.conf import settings
from importlib.metadata import version, PackageNotFoundError

def save_versions_txt(lib, filepath="/results/version.txt"):
    with open(filepath, "w") as f:
        try:
            f.write(f"{lib}=={version(lib)}\n")
        except PackageNotFoundError:
            f.write(f"{lib}==NOT INSTALLED\n")

save_versions_txt("django")

from . import views

settings.configure(
    SECRET_KEY='nosecret',
    DEBUG=False,
    ROOT_URLCONF = views,
)

app = get_asgi_application()
