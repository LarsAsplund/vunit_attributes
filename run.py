from pathlib import Path
from vunit import VUnit

prj = VUnit.from_argv()
prj.add_library("lib").add_source_files(Path(__file__).parent / "test/*.vhd")
prj.main()
