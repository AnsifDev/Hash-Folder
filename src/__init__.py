import json
from os import path, system, mkdir
import gi

app_cache = path.abspath(".cache")
app_config = path.abspath(".config")

__filename = path.join(app_config, "app_config.json")

if path.exists(__filename):
    __file = open(__filename)
    __config = json.loads(__file.read())
    __file.close()
else:
    print("App configuration error: Configuration Missing")
    exit(1)

version_code = __config["current_runtime_env"]
# version_code = 20.04
print(version_code)

if version_code >= 22.04:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
else: gi.require_version("Gtk", "3.0")

if version_code >= 23.04:
    gi.require_version("Vte", "3.91")

def get_ui_file_path(filename: str, ui_path="src/ui"):
    match version_code:
        case 20.04: return path.join(ui_path, "focal", filename)
        case 22.04: return path.join(ui_path, "jammy", filename)
        case 23.04: return path.join(ui_path, "lunar", filename)
