# -*- coding: utf-8 -*-
"""
Functionality to generate and work with the directory structure of a project
"""
from __future__ import absolute_import, print_function

import copy
import os
from datetime import date
from os.path import join as join_path

import pyscaffold
from six import string_types

from . import info, shell, templates, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def set_default_args(args):
    """
    Set default arguments for some parameters

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    args = copy.copy(args)
    utils.safe_set(args, "author", info.username())
    utils.safe_set(args, "email", info.email())
    utils.safe_set(args, "year", date.today().year)
    utils.safe_set(args, "license", "none")
    utils.safe_set(args, "version", pyscaffold.__version__)
    utils.safe_set(args, "title", "="*len(args.project) + "\n" +
                                  args.project + "\n" +
                                  "="*len(args.project))
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python']
    utils.safe_set(args, "classifiers", utils.list2str(classifiers, indent=15))
    utils.safe_set(args, "console_scripts", utils.list2str([], indent=19))
    utils.safe_set(args, "junit_xml", False)
    utils.safe_set(args, "coverage_xml", False)
    utils.safe_set(args, "coverage_html", False)
    return args


def make_structure(args):
    """
    Creates the project structure as dictionary of dictionaries

    :param args: command line parameters as :obj:`argparse.Namespace`
    :return: structure as dictionary of dictionaries
    """
    args = set_default_args(args)
    struct = {args.project: {
        ".gitignore": templates.gitignore(args),
        args.package: {"__init__.py": templates.init(args),
                       "_version.py": templates.version(args)},
        "tests": {"__init__.py": ""},
        "docs": {"conf.py": templates.sphinx_conf(args),
                 "index.rst": templates.sphinx_index(args),
                 "license.rst": templates.sphinx_license(args),
                 "Makefile": templates.sphinx_makefile(args),
                 "_static": {
                     ".gitignore": templates.gitignore_empty(args)}},
        "README.rst": templates.readme(args),
        "AUTHORS.rst": templates.authors(args),
        "MANIFEST.in": templates.manifest_in(args),
        "LICENSE.txt": templates.license(args),
        "setup.py": templates.setup(args),
        "versioneer.py": templates.versioneer(args),
        "requirements.txt": templates.requirements(args),
        ".coveragerc": templates.coveragerc(args),
        ".gitattributes": templates.gitattributes(args)}}
    proj_dir = struct[args.project]
    if args.travis:
        proj_dir[".travis.yml"] = templates.travis(args)
        proj_dir["tests"]["travis_install.sh"] = templates.travis_install(args)
    if args.django:
        proj_dir["manage.py"] = None
        proj_dir[args.package]["settings.py"] = None
        proj_dir[args.package]["urls.py"] = None
        proj_dir[args.package]["wsgi.py"] = None
    if args.pre_commit:
        proj_dir[".pre-commit-config.yaml"] = templates.pre_commit_config(args)
    if args.tox:
        proj_dir["tox.ini"] = templates.tox(args),
    if args.update and not args.force:  # Do not overwrite following files
        safe = {args.project: {
            ".gitignore": None,
            ".gitattributes": None,
            "README.rst": None,
            "AUTHORS.rst": None,
            "requirements.txt": None,
            ".travis.yml": None,
            ".pre-commit-config.yaml": None,
            "tox.ini": None,
            "tests": {"travis_install.sh": None},
            "doc": {"index.rst": None}
        }}
        safe = check_files_exist(safe)
        struct = remove_from_struct(struct, safe)

    return struct


def create_structure(struct, prefix=None, update=False):
    """
    Manifests a directory structure in the filesystem

    :param struct: directory structure as dictionary of dictionaries
    :param prefix: prefix path for the structure
    :param update: update an existing directory structure as boolean
    """
    if prefix is None:
        prefix = os.getcwd()
    for name, content in struct.items():
        if isinstance(content, string_types):
            with open(join_path(prefix, name), "w") as fh:
                fh.write(utils.utf8_encode(content))
        elif isinstance(content, dict):
            try:
                os.mkdir(join_path(prefix, name))
            except OSError:
                if not update:
                    raise
            create_structure(struct[name],
                             prefix=join_path(prefix, name),
                             update=update)
        elif content is None:
            pass
        else:
            raise RuntimeError("Don't know what to do with content type "
                               "{type}.".format(type=type(content)))


def create_django_proj(args):
    """
    Creates a standard Django project with django-admin.py

    :param args: command line parameters as :obj:`argparse.Namespace`
    """
    try:
        shell.django_admin("--version")
    except:
        raise RuntimeError("django-admin.py is not installed, "
                           "run: pip install django")
    shell.django_admin("startproject", args.project)
    args.package = args.project  # since this is required by Django
    args.force = True


def check_files_exist(struct, prefix=None):
    """
    Checks which files exist in a directory structure

    :param struct: directory structure as dictionary of dictionaries
    :param prefix: prefix path for the structure
    :return: returns a dictionary of dictionaries where keys representing
        files exists in the filesystem.
    """
    result = dict()
    if prefix is None:
        prefix = os.getcwd()
    for name, content in struct.items():
        if isinstance(content, dict):
            result[name] = check_files_exist(struct[name],
                                             prefix=join_path(prefix, name))
            if not result[name]:  # dict is empty
                del result[name]
        else:
            if os.path.isfile(join_path(prefix, name)):
                result[name] = content
    return result


def remove_from_struct(orig_struct, del_struct):
    """
    Removes files existing in `del_struct` from structure `orig_struct`

    :param orig_struct: directory structure as dictionary of dictionaries
    :param del_struct: directory structure as dictionary of dictionaries
    :return: directory structure as dictionary of dictionaries
    """
    result = dict()
    for k, v in orig_struct.items():
        if isinstance(v, dict):
            if k in del_struct:
                result[k] = remove_from_struct(orig_struct[k], del_struct[k])
                if not result[k]:  # dict is empty
                    del result[k]
            else:
                result[k] = copy.deepcopy(orig_struct[k])
        else:
            if k in del_struct:
                continue
            else:
                result[k] = orig_struct[k]
    return result
