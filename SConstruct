# Empty, no building required.

import os
import sys
import subprocess

linkflags = []
ccflags = ['-I.', '-MD']
platform = sys.platform
# need to do something like  on windows?
if sys.platform.startswith('win'):
    subprocess.call("vcvars32.bat")
    linkflags.extend(['-OPT:REF', '-OPT:ICF', '-NOLOGO'])
    ccflags.extend(['-W3', '-Ox', '-nologo'])
else:
    linkflags.extend(['-O3'])
    ccflags.extend(['-Wall', '-O3', '-Wpointer-arith'])

include = "#export/%s/include" % platform
lib = "#export/%s/lib" % platform
bin = "#export/%s/bin" % platform

ld_library_path = os.path.abspath(lib[1:])

env = Environment(ENV = os.environ,
                  TARGET_ARCH = "x86",
                  PLATFORM = platform,
                  CCFLAGS = ccflags,
                  LINKFLAGS = linkflags,
                  BINDIR = bin,
                  INCDIR = include,
                  LIBDIR = lib,
                  CPPPATH = [include],
                  LIBPATH = [lib],
                  LD_LIBRARY_PATH = ld_library_path)

Export("env")

#env.Alias('install', ['/usr/local'])
env.Alias('build', ['.'])

env.SConscript(["src/SConscript"], exports='env')
