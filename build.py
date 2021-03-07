
import subprocess
import re
import os
import sys
import shutil


def get_make_output(makefile):
    proc = subprocess.run(
        f"make lib -n -f {makefile}", capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr)
        exit(1)
    return proc.stdout


def classify_lines(lines):
    compile_calls = list()

    for line in lines:
        args = line.split()
        if 'gcc' in args[0]:
            compile_calls.append(line)

    return {'compile': compile_calls}


def process_compile_lines(lines):
    sources = list()
    header_dirs = set()

    for line in lines:
        args = line.split()
        for arg in args:
            if re.search(r'\.[csS]$', arg) is not None:
                sources.append(arg)
            include_match = re.search(r'^-I(.+)$', arg)
            if include_match is not None:
                header_dirs.add(include_match.group(1))

    return {'sources': sources, 'header_dirs': header_dirs}


def list_headers(header_dirs):
    headers = []

    for header_dir in header_dirs:
        for file in os.listdir(header_dir):
            if re.search(r'\.h$', file) is not None:
                headers.append(os.path.join(header_dir, file))

    return headers


def build_package(package_name, sources, headers):
    package_dir = os.path.join('build', package_name)
    shutil.rmtree(package_dir, ignore_errors=True)

    package_source_dir = os.path.join(package_dir, 'src')
    os.makedirs(package_source_dir)
    for source in sources:
        shutil.copy(source, package_source_dir)

    package_header_dir = os.path.join(package_dir, 'include')
    os.makedirs(package_header_dir)
    for header in headers:
        shutil.copy(header, package_header_dir)


package_name = sys.argv[1]

make_lines = get_make_output(f"{package_name}.Makefile").splitlines()

classified_lines = classify_lines(make_lines)

compile_items = process_compile_lines(classified_lines['compile'])

headers = list_headers(compile_items['header_dirs'])

build_package(package_name, compile_items['sources'], headers)
