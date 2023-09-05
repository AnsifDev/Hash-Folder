project('org.htg.hashfolder', 'vala', 'c')
add_global_arguments('-I/usr/lib64/', language : 'c')
add_global_arguments('--pkg=posix', language : 'vala')

dependencies = [
    dependency('gtk4'), 
    dependency('libadwaita-1'),
    dependency('gee-0.8'),
    dependency('json-glib-1.0'), 
    dependency('vte-2.91-gtk4')
]

sources = run_command('./.meson_tools/file_scanner.py', 'src/vala', '*.vala', check:true).stdout().strip().split('\n')

gnome = import('gnome') 
run_command('./.meson_tools/resource_builder.py', meson.project_name(), check:true)
sources += gnome.compile_resources('resources', 'resources.xml', source_dir: 'src/resources')
 
executable('app', sources, dependencies: dependencies, install: true, export_dynamic: true)
 
icons = run_command('./.meson_tools/file_scanner.py', 'src/resources/icons', '*.svg', check:true).stdout().strip()
if icons != ''
    icon_list = icons.split('\n')
    symbolic_dir = join_paths(get_option('datadir'), 'icons', 'hicolor', 'symbolic', 'actions')
    install_data(icon_list, install_dir: symbolic_dir)
endif

fs = import('fs')
metainfo = join_paths('src/resources/app', meson.project_name()+'.metainfo.xml')
if fs.exists(metainfo)
    install_data(metainfo, install_dir: '/app/share/metainfo')
endif

desktop = join_paths('src/resources/app', meson.project_name()+'.desktop')
if fs.exists(desktop)
    install_data(desktop, install_dir: '/app/share/applications')
endif

app_icon = join_paths('src/resources/app', meson.project_name()+'.svg')
if fs.exists(app_icon)
    install_data(app_icon, install_dir: '/app/share/icons/hicolor/scalable/apps')
endif

app_icon_devel = join_paths('src/resources/app', meson.project_name()+'.Devel.svg')
if fs.exists(app_icon_devel)
    install_data(app_icon_devel, install_dir: '/app/share/icons/hicolor/scalable/apps')
endif

app_icon_symbolic = join_paths('src/resources/app', meson.project_name()+'-symbolic.svg')
if fs.exists(app_icon_symbolic)
    install_data(app_icon_symbolic, install_dir: '/app/share/icons/hicolor/symbolic/apps')
endif