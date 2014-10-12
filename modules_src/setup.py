#
# python setup.py build
#
#
# macosx:
#
#   to prevent errors like this:
#
#     /usr/libexec/gcc/powerpc-apple-darwin10/4.0.1/as: assembler (/usr/bin/../libexec/gcc/darwin/ppc/as or /usr/bin/../local/libexec/gcc/darwin/ppc/as) for architecture ppc not installed
#     Installed assemblers are:
#     /usr/bin/../libexec/gcc/darwin/x86_64/as for architecture x86_64
#     /usr/bin/../libexec/gcc/darwin/i386/as for architecture i386
#
#   disable ppc support:
#
#     export ARCHFLAGS="-arch i386 -arch x86_64"; python setup.py build
#
# random note: python setup.py build > log.txt 2>&1
#

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import sys


libraries = []
extra_compile_args = []
extra_link_args = []

if sys.platform == "darwin":
    # negate the -g debugging flag that got always added in macosx by default
    extra_compile_args = ["-g0"]
    extra_link_args = ['-framework', 'OpenGL']
elif sys.platform == "win32":
    libraries = ["opengl32"]
elif sys.platform == "linux2":
    libraries = ["GL"]
else:
    raise RuntimeError("platform %s not supported" % (sys.platform))


ext_cpp = Extension(
    "cpp",
    language="c++",
    sources=["cpp.pyx",
             "helpers_src/opengl_graphics.cpp",
             "mip_buf_src/mip_buf_renderer.cpp",
             "mip_buf_simple_src/mip_buf_simple_renderer.cpp"],
    include_dirs=["helpers_src", "mip_buf_src", "mip_buf_simple_src"],
    library_dirs=[],
    libraries=libraries,
    #define_macros=[("WIN32", "1")],
    extra_link_args=extra_link_args,
    extra_compile_args=extra_compile_args,
    #depends=[],
    )


setup(
    name         = "cppwrappers",
    version      = "0.1",
    license      = "MIT",
    description  = "python wrapper for various cpp classes/functions/helpers",
    long_description  = """nah""",
    keywords     = "",
    author       = "",
    author_email = "",
    url          = "",
    classifiers  = [],
    ext_modules  = [ext_cpp],
    cmdclass     = {'build_ext': build_ext}
    )


# the setup.py "clean" command is not working completely for cython. we'll do it ourselves.

if "clean" in sys.argv:
    import os
    import shutil
    for p in ["cpp.cpp"]:
        print "deleting", p
        try:    os.remove(p)
        except: pass
    shutil.rmtree("build", True)

