# # header
# coding: utf-8

from __future__ import print_function

if __name__ != '__main__':
    raise NotImplementedError('should never include setup.py')

# # definitions

full_package_name = None

# # __init__.py parser

import sys
from _ast import *       # NOQA
from ast import parse


if sys.version_info < (3, ):
    string_type = basestring
else:
    string_type = str


if sys.version_info < (3, 4):
    class Bytes():
        pass

    class NameConstant:
        pass

if sys.version_info < (2, 7):
    class Set():
        pass


def literal_eval(node_or_string):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, and None.
    """
    _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, string_type):
        node_or_string = parse(node_or_string, mode='eval')
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body

    def _convert(node):
        if isinstance(node, (Str, Bytes)):
            return node.s
        elif isinstance(node, Num):
            return node.n
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return list(map(_convert, node.elts))
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, Dict):
            return dict((_convert(k), _convert(v)) for k, v
                        in zip(node.keys, node.values))
        elif isinstance(node, NameConstant):
            return node.value
        elif sys.version_info < (3, 4) and isinstance(node, Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif isinstance(node, UnaryOp) and \
             isinstance(node.op, (UAdd, USub)) and \
             isinstance(node.operand, (Num, UnaryOp, BinOp)):  # NOQA
            operand = _convert(node.operand)
            if isinstance(node.op, UAdd):
                return + operand
            else:
                return - operand
        elif isinstance(node, BinOp) and \
             isinstance(node.op, (Add, Sub)) and \
             isinstance(node.right, (Num, UnaryOp, BinOp)) and \
             isinstance(node.left, (Num, UnaryOp, BinOp)):  # NOQA
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, Add):
                return left + right
            else:
                return left - right
        elif isinstance(node, Call) and node.func.id == 'dict':
            return dict((k.arg, _convert(k.value)) for k in node.keywords)
        elif isinstance(node, Call) and node.func.id == 'set':
            return set(_convert(k) for k in node.args)
        err = SyntaxError('malformed node or string: ' + repr(node))
        err.filename = '<string>'
        err.lineno = node.lineno
        err.offset = node.col_offset
        err.text = repr(node)
        err.node = node
        raise err
    return _convert(node_or_string)


# parses python ( "= dict( )" ) or ( "= {" )
def _package_data(fn):
    data = {}
    with open(fn) as fp:
        parsing = False
        lines = []
        for line in fp.readlines():
            if sys.version_info < (3,):
                line = line.decode('utf-8')
            if line.startswith(u'_package_data'):
                if 'dict(' in line:
                    parsing = 'python'
                    lines.append(u'dict(\n')
                elif line.endswith(u'= {\n'):
                    parsing = 'python'
                    lines.append(u'{\n')
                else:
                    raise NotImplementedError
                continue
            if not parsing:
                continue
            if parsing == 'python':
                if line.startswith(u')') or line.startswith(u'}'):
                    lines.append(line)
                    try:
                        data = literal_eval(u''.join(lines))
                    except SyntaxError as e:
                        context = 2
                        from_line = e.lineno - (context + 1)
                        to_line = e.lineno + (context - 1)
                        w = len(str(to_line))
                        for index, line in enumerate(lines):
                            if from_line <= index <= to_line:
                                print(u"{:{}}: {}".format(index, w, line), end=u'')
                                if index == e.lineno - 1:
                                    print(u"{:{}}  {}^--- {}".format(
                                        u' ', w, u' ' * e.offset, e.node))
                        raise
                    break
                lines.append(line)
            else:
                raise NotImplementedError
    return data

# make sure you can run "python ../some/dir/setup.py install"
pkg_data = _package_data(__file__.replace('setup.py', '__init__.py'))

exclude_files = [
    'setup.py',
]

# # imports
import os
import sys
import platform

from setuptools import setup, Extension, Distribution  # NOQA
from setuptools.command import install_lib


# # helper
def _check_convert_version(tup):
    """Create a PEP 386 pseudo-format conformant string from tuple tup."""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    nr_digits = 0  # nr of adjacent digits in rest, to verify
    post_dev = False  # are we processig post/dev
    for x in tup[1:]:
        if isinstance(x, int):
            nr_digits += 1
            if nr_digits > 2:
                raise ValueError("too many consecutive digits " + ret_val)
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            if post_dev:
                raise ValueError("release level specified after "
                                 "post/dev:" + x)
            nr_digits = 0
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            nr_digits = 1  # only one can follow
            post_dev = True
            ret_val += '.post' if first_letter == 'p' else '.dev'
        else:
            raise ValueError('First letter of "' + x + '" not recognised')
    return ret_val


version_info = pkg_data['version_info']
version_str = _check_convert_version(version_info)


class MyInstallLib(install_lib.install_lib):
    def install(self):
        fpp = pkg_data['full_package_name'].split('.')  # full package path
        full_exclude_files = [os.path.join(*(fpp + [x]))
                              for x in exclude_files]
        alt_files = []
        outfiles = install_lib.install_lib.install(self)
        for x in outfiles:
            for full_exclude_file in full_exclude_files:
                if full_exclude_file in x:
                    os.remove(x)
                    break
            else:
                alt_files.append(x)
        return alt_files


class NameSpacePackager(object):
    def __init__(self, pkg_data):
        assert isinstance(pkg_data, dict)
        self._pkg_data = pkg_data
        self.full_package_name = self.pn(self._pkg_data['full_package_name'])
        self._split = None
        self.depth = self.full_package_name.count('.')
        self.command = None
        self._pkg = [None, None]  # required and pre-installable packages
        if sys.argv[0] == 'setup.py' and sys.argv[1] == 'install' and \
           '--single-version-externally-managed' not in sys.argv:
            print('error: have to install with "pip install ."')
            sys.exit(1)
        # If you only support an extension module on Linux, Windows thinks it
        # is pure. That way you would get pure python .whl files that take
        # precedence for downloading on Linux over source with compilable C
        if self._pkg_data.get('universal'):
            Distribution.is_pure = lambda *args: True
        else:
            Distribution.is_pure = lambda *args: False
        for x in sys.argv:
            if x[0] == '-' or x == 'setup.py':
                continue
            self.command = x
            break

    def pn(self, s):
        if sys.version_info < (3, ) and isinstance(s, unicode):
            return s.encode('utf-8')
        return s

    @property
    def split(self):
        """split the full package name in list of compontents traditionally
        done by setuptools.find_packages. This routine skips any directories
        with __init__.py that start with "_" or ".", or contain a
        setup.py/tox.ini (indicating a subpackage)
        """
        if self._split is None:
            fpn = self.full_package_name.split('.')
            self._split = []
            while fpn:
                self._split.insert(0, '.'.join(fpn))
                fpn = fpn[:-1]
            for d in os.listdir('.'):
                if not os.path.isdir(d) or d == self._split[0] or d[0] in '._':
                    continue
                # prevent sub-packages in namespace from being included
                x = os.path.join(d, 'setup.py')
                if os.path.exists(x):
                    if not os.path.exists(os.path.join(d, 'tox.ini')):
                        print('\n>>>>> found "{0}" without tox.ini <<<<<\n'
                              ''.format(x))
                    continue
                x = os.path.join(d, '__init__.py')
                if os.path.exists(x):
                    self._split.append(self.full_package_name + '.' + d)
        return self._split

    @property
    def namespace_packages(self):
        return self.split[:self.depth]

    def namespace_directories(self, depth=None):
        """return list of directories where the namespace should be created /
        can be found
        """
        res = []
        for index, d in enumerate(self.split[:depth]):
            # toplevel gets a dot
            if index > 0:
                d = os.path.join(*d.split('.'))
            res.append('.' + d)
        return res

    @property
    def package_dir(self):
        return {
            # don't specify empty dir, clashes with package_data spec
            self.full_package_name: '.',
            self.split[0]: self.namespace_directories(1)[0],
        }

    def create_dirs(self):
        """create the directories necessary for namespace packaging"""
        directories = self.namespace_directories(self.depth)
        if not os.path.exists(directories[0]):
            for d in directories:
                os.mkdir(d)
                with open(os.path.join(d, '__init__.py'), 'w') as fp:
                    fp.write('import pkg_resources\n'
                             'pkg_resources.declare_namespace(__name__)\n')

    def check(self):
        try:
            from pip.exceptions import InstallationError
        except ImportError:
            return
        # arg is either develop (pip install -e) or install
        if self.command not in ['install', 'develop']:
            return

        # if hgi and hgi.base are both in namespace_packages matching
        # against the top (hgi.) it suffices to find minus-e and non-minus-e
        # installed packages. As we don't know the order in namespace_packages
        # do some magic
        prefix = self.split[0]
        prefixes = set([prefix, prefix.replace('_', '-')])
        for p in sys.path:
            if not p:
                continue  # directory with setup.py
            if os.path.exists(os.path.join(p, 'setup.py')):
                continue  # some linked in stuff might not be hgi based
            if not os.path.isdir(p):
                continue
            if p.startswith('/tmp/'):
                continue
            for fn in os.listdir(p):
                for pre in prefixes:
                    if fn.startswith(pre):
                        break
                else:
                    continue
                full_name = os.path.join(p, fn)
                # not in prefixes the toplevel is never changed from _ to -
                if fn == prefix and os.path.isdir(full_name):
                    # directory -> other, non-minus-e, install
                    if self.command == 'develop':
                        raise InstallationError(
                            'Cannot mix develop (pip install -e),\nwith '
                            'non-develop installs for package name {0}'.format(
                                fn))
                elif fn == prefix:
                    raise InstallationError(
                        'non directory package {0} in {1}'.format(
                            fn, p))
                for pre in [x + '.' for x in prefixes]:
                    if fn.startswith(pre):
                        break
                else:
                    continue  # hgiabc instead of hgi.
                if fn.endswith('-link') and self.command == 'install':
                    raise InstallationError(
                        'Cannot mix non-develop with develop\n(pip install -e)'
                        ' installs for package name {0}'.format(fn))

    def entry_points(self, script_name=None, package_name=None):
        ep = self._pkg_data.get('entry_points', True)
        if ep is None:
            return None
        if ep not in [True, 1]:
            return {'console_scripts': [ep]}
        if package_name is None:
            package_name = self.full_package_name
        if not script_name:
            script_name = package_name.split('.')[-1]
        return {'console_scripts': [
            '{0} = {1}:main'.format(script_name, package_name),
        ]}

    @property
    def url(self):
        return 'https://bitbucket.org/{0}/{1}'.format(
            *self.full_package_name.split('.', 1))

    @property
    def author(self):
        return self._pkg_data['author']

    @property
    def author_email(self):
        return self._pkg_data['author_email']

    @property
    def license(self):
        lic = self._pkg_data.get('license')
        if lic is None:
            # lic_fn = os.path.join(os.path.dirname(__file__), 'LICENSE')
            # assert os.path.exists(lic_fn)
            return "MIT license"
        return license

    @property
    def description(self):
        return self._pkg_data['description']

    @property
    def status(self):
        # αβ
        status = self._pkg_data.get('status', u'β')
        if status == u'α':
            return (3, 'Alpha')
        elif status == u'β':
            return (4, 'Beta')
        elif u'stable' in status.lower():
            return (5, 'Production/Stable')
        raise NotImplementedError

    @property
    def classifiers(self):
        return [
            'Development Status :: {0} - {1}'.format(*self.status),
            'Intended Audience :: Developers',
            'License :: ' + ('Other/Proprietary License'
                             if self.pn(self._pkg_data.get('license')) else
                             'OSI Approved :: MIT License'),
            'Operating System :: OS Independent',
            'Programming Language :: Python',
        ] + [self.pn(x) for x in self._pkg_data.get('classifiers', [])]

    @property
    def install_requires(self):
        """list of packages required for installation"""
        return self._analyse_packages[0]

    @property
    def install_pre(self):
        """list of packages required for installation"""
        return self._analyse_packages[1]

    @property
    def _analyse_packages(self):
        """gather from configuration, names starting with * need
        to be installed explicitly as they are not on PyPI
        install_requires should be  dict, with keys 'any', 'py27' etc
        or a list (which is as if only 'any' was defined
        """
        if self._pkg[0] is None:
            self._pkg[0] = []
            self._pkg[1] = []

        ir = self._pkg_data.get('install_requires')
        if ir is None:
            return self._pkg  # these will be both empty at this point
        if isinstance(ir, list):
            self._pkg[0] = ir
            return self._pkg
        # 'any' for all builds, 'py27' etc for specifics versions
        packages = ir.get('any', [])
        implementation = platform.python_implementation()
        if implementation == 'CPython':
            pyver = 'py{0}{1}'.format(*sys.version_info)
        elif implementation == 'PyPy':
            pyver = 'pypy' if sys.version_info < (3, ) else 'pypy3'
        packages.extend(ir.get(pyver, []))
        for p in packages:
            # package name starting with * means use local source tree,  non-published
            # to PyPi or maybe not latest version on PyPI -> pre-install
            if p[0] == '*':
                p = p[1:]
                self._pkg[1].append(p)
            self._pkg[0].append(p)
        return self._pkg

    @property
    def data_files(self):
        df = self._pkg_data.get('data_files', [])
        if self._pkg_data.get('license') is None:
            df.append('LICENSE')
        if not df:
            return None
        return [('.', df), ]

    @property
    def package_data(self):
        df = self._pkg_data.get('data_files', [])
        if self._pkg_data.get('license') is None:
            # include the file
            df.append('LICENSE')
            # but don't install it
            exclude_files.append('LICENSE')
        if not df:
            return {}
        return {self.full_package_name: df}

    @property
    def ext_modules(self):
        """check if the C module can be build by trying to compile a small
            program against the libyaml development library"""
        if hasattr(self, '_ext_modules'):
            return self._ext_modules
        if '--version' in sys.argv:
            return None
        # if sys.platform == "win32":
        #     return None
        import tempfile
        import shutil
        from textwrap import dedent

        import distutils.sysconfig
        import distutils.ccompiler
        from distutils.errors import CompileError, LinkError

        self._ext_modules = []
        for target in self._pkg_data.get('ext_modules', []):  # list of dicts
            test_code = target.get('test')
            libraries = [self.pn(x) for x in target.get('lib')]
            ext = Extension(
                self.pn(target['name']),
                sources=[self.pn(x) for x in target['src']],
                libraries=libraries,
            )
            if not test_code:
                self._ext_modules.append(ext)
                continue
            # write a temporary .c file to compile
            c_code = dedent(target['test'])
            try:
                tmp_dir = tempfile.mkdtemp(prefix='tmp_ruamel_')
                bin_file_name = 'test' + self.pn(target['name'])
                file_name = os.path.join(tmp_dir, bin_file_name + '.c')
                with open(file_name, 'w') as fp:
                    fp.write(c_code)

                # and try to compile it
                compiler = distutils.ccompiler.new_compiler()
                assert isinstance(compiler, distutils.ccompiler.CCompiler)
                distutils.sysconfig.customize_compiler(compiler)

                try:
                    compiler.link_executable(
                        compiler.compile(
                            [file_name],
                            output_dir='/',  # as file_name has absolute prefix
                        ),
                        bin_file_name,
                        output_dir=tmp_dir,
                        libraries=libraries,
                    )
                except CompileError:
                    print('compile error:', file_name)
                    continue
                except LinkError:
                    print('libyaml link error', file_name)
                    continue
                self._ext_modules.append(ext)
            except Exception as e:  # NOQA
                # print('Exception:', e)
                pass
            finally:
                shutil.rmtree(tmp_dir)
        return self._ext_modules

    def wheel(self, kw, setup):
        """temporary add setup.cfg if creating a wheel to include LICENSE file
        https://bitbucket.org/pypa/wheel/issues/47
        """
        if 'bdist_wheel' not in sys.argv:
            return
        file_name = 'setup.cfg'
        if os.path.exists(file_name):  # add it if not in there?
            return
        with open(file_name, 'w') as fp:
            if os.path.exists('LICENSE'):
                fp.write('[metadata]\nlicense-file = LICENSE\n')
            else:
                print("\n\n>>>>>> LICENSE file not found <<<<<\n\n")
            if self._pkg_data.get('universal'):
                fp.write('[bdist_wheel]\nuniversal = 1\n')
        try:
            setup(**kw)
        except:
            raise
        finally:
            os.remove(file_name)
        return True


# # call setup
def main():
    nsp = NameSpacePackager(pkg_data)
    nsp.check()
    nsp.create_dirs()
    kw = dict(
        name=nsp.full_package_name,
        namespace_packages=nsp.namespace_packages,
        version=version_str,
        packages=nsp.split,
        url=nsp.url,
        author=nsp.author,
        author_email=nsp.author_email,
        cmdclass={'install_lib': MyInstallLib},
        package_dir=nsp.package_dir,
        entry_points=nsp.entry_points(),
        description=nsp.description,
        install_requires=nsp.install_requires,
        license=nsp.license,
        classifiers=nsp.classifiers,
        package_data=nsp.package_data,
        ext_modules=nsp.ext_modules,
    )
    if '--version' not in sys.argv or '--verbose' in sys.argv:
        for k in sorted(kw):
            v = kw[k]
            print(k, '->', v)
    with open('README.rst') as fp:
        kw['long_description'] = fp.read()
    if nsp.wheel(kw, setup):
        return
    for x in ['-c', 'egg_info', '--egg-base', 'pip-egg-info']:
        if x not in sys.argv:
            break
    else:
        # we're doing a tox setup install any starred package by searching up the source tree
        # until you match your/package/name for your.package.name
        for p in nsp.install_pre:
            import subprocess
            # search other source
            setup_path = os.path.join(*p.split('.') + ['setup.py'])
            try_dir = os.path.dirname(sys.executable)
            while len(try_dir) > 1:
                full_path_setup_py = os.path.join(try_dir, setup_path)
                if os.path.exists(full_path_setup_py):
                    pip = sys.executable.replace('python', 'pip')
                    cmd = [pip, 'install', os.path.dirname(full_path_setup_py)]
                    # with open('/var/tmp/notice', 'a') as fp:
                    #     print('installing', cmd, file=fp)
                    subprocess.check_output(cmd)
                    break
                try_dir = os.path.dirname(try_dir)
    setup(**kw)


main()
