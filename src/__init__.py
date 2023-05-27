import json
from os import path, system, mkdir
import gi

app_cache_path = path.abspath(".cache")
app_config_path = path.abspath(".config")

__filename = path.join(app_config_path, "app_config.json")

if path.exists(__filename):
    __file = open(__filename)
    app_config = json.loads(__file.read())
    __file.close()
else:
    print("App configuration error: Configuration Missing")
    exit(1)

runtime_env = app_config["current_runtime_env"]
# runtime_env = 20.04
print(runtime_env)

if runtime_env >= 22.04:
    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
else: gi.require_version("Gtk", "3.0")

if runtime_env >= 23.04:
    gi.require_version("Vte", "3.91")

def update_app_config():
    __file = open(__filename, "w")
    __file.write(json.dumps(app_config))
    __file.close()

def get_ui_file_path(filename: str, ui_path="src/ui"):
    match runtime_env:
        case 20.04: return path.join(ui_path, "focal", filename)
        case 22.04: return path.join(ui_path, "jammy", filename)
        case 23.04: return path.join(ui_path, "lunar", filename)
