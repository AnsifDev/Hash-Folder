from os import path, system, mkdir
import gi
# import lsb_release

app_cache = path.abspath(".cache")
app_config = path.abspath(".config")

if not path.exists(app_cache): mkdir(app_cache)
if not path.exists(app_config): mkdir(app_config)

filename = path.join(app_cache, "temp.dat")
cmd = "lsb_release -r > "+filename.replace(" ", "\\ ")
system(cmd)

file = open(filename)
file_str = file.read()
file.close()

version_code = float(file_str.split(":")[1].strip())
# version_code = float(lsb_release.get_distro_information()["RELEASE"])
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
