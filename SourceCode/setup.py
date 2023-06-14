import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
   "includes" : ["PyQt5", "PyQt5.QtWidgets", "re", ]
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

#windows 7 compatibility
if sys.platform == "win32":
    base = "Win32GUI"
    build_exe_options["include_msvcr"] = True


setup(
    name="PGO-CNC_Converter",
    options={"build_exe": build_exe_options},
    executables=[Executable("SourceCode/main.py", base=base)]
)