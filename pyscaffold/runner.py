# -*- coding: utf-8 -*-
"""
Command-Line-Interface of PyScaffold
"""
from __future__ import absolute_import, print_function

import argparse
import os.path
import sys

import pyscaffold

from . import info, repo, shell, structure, templates, utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def parse_args(args):
    """
    Parse command line parameters

    :param args: command line parameters as list of strings
    :return: command line parameters as :obj:`argparse.Namespace`
    """
    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")
    parser.add_argument(
        dest="project",
        help="project name",
        metavar="PROJECT")
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        required=False,
        default=None,
        help="package name (default: project name)",
        metavar="NAME")
    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        required=False,
        default=None,
        help="package description (default: '')",
        metavar="TEXT")
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        default=None,
        help="package url (default: '')",
        metavar="URL")
    license_choices = templates.licenses.keys()
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        required=False,
        default=None,
        help="package license from {choices} (default: {default})".format(
            choices=str(license_choices), default="No license"),
        metavar="LICENSE")
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="force overwriting an existing directory")
    parser.add_argument(
        "--update",
        dest="update",
        action="store_true",
        default=False,
        help="update an existing project by replacing the most important files"
             " like setup.py, versioneer.py etc. Use additionally --force to "
             "replace all scaffold files.")
    parser.add_argument(
        "--with-junit-xml",
        dest="junit_xml",
        action="store_true",
        default=None,
        help="generate a JUnit xml report")
    parser.add_argument(
        "--with-coverage-xml",
        dest="coverage_xml",
        action="store_true",
        default=None,
        help="generate a coverage xml report")
    parser.add_argument(
        "--with-coverage-html",
        dest="coverage_html",
        action="store_true",
        default=None,
        help="generate a coverage html report")
    parser.add_argument(
        "--with-travis",
        dest="travis",
        action="store_true",
        default=False,
        help="generate Travis configuration files")
    parser.add_argument(
        "--with-django",
        dest="django",
        action="store_true",
        default=False,
        help="generate Django project files")
    parser.add_argument(
        "--with-pre-commit",
        dest="pre_commit",
        action="store_true",
        default=False,
        help="generate pre-commit configuration file")
    parser.add_argument(
        "--with-tox",
        dest="tox",
        action="store_true",
        default=False,
        help="generate Tox configuration file")
    version = pyscaffold.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='PyScaffold {ver}'.format(ver=version))
    opts = parser.parse_args(args)
    if opts.package is None:
        opts.package = utils.make_valid_identifier(opts.project)
    # Strip (back)slash when added accidentally during update
    opts.project = opts.project.rstrip(os.sep)
    return opts


def main(args):
    """
    Main entry point of PyScaffold

    :param args: command line parameters as list of strings
    """
    args = parse_args(args)
    if not info.is_git_installed():
        raise RuntimeError("Make sure git is installed and working.")
    if not info.is_git_configured():
        raise RuntimeError(
            'Make sure git is configured. Run:\n' +
            '  git config --global user.email "you@example.com"\n' +
            '  git config --global user.name "Your Name"\n' +
            "to set your account's default identity.")
    if os.path.exists(args.project):
        if not args.update and not args.force:
            raise RuntimeError(
                "Directory {dir} already exists! Use --update to update an "
                "existing project or --force to overwrite an existing "
                "directory.".format(dir=args.project))
    if args.update:
        try:
            args = info.project(args)
        except (IOError, AttributeError):
            raise RuntimeError("Could not update {project}. Was it generated "
                               "with PyScaffold?".format(project=args.project))
    if args.django:
        structure.create_django_proj(args)
    proj_struct = structure.make_structure(args)
    structure.create_structure(proj_struct, update=args.update or args.force)
    if not args.update and not repo.is_git_repo(args.project):
        repo.init_commit_repo(args.project, proj_struct)


@shell.called_process_error2exit_decorator
@utils.exceptions2exit([RuntimeError])
def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
