import os

# if not os.path.exists(".build"):
#     if os.system("meson setup .build") != 0: exit(1)
# elif os.system("meson setup .build --reconfigure") != 0: exit(1)

if os.system("meson compile -C .build") != 0: exit(1)
os.system("./.build/app")