#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import getpass
import os
import socket

import pytest
from pyscaffold import info, runner
from six import string_types

from .fixtures import git_mock, noconfgit_mock, nogit_mock, tmpdir  # noqa

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_username_with_git(git_mock):  # noqa
    username = info.username()
    assert isinstance(username, string_types)
    assert len(username) > 0


def test_username_with_no_git(nogit_mock):  # noqa
    username = info.username()
    assert isinstance(username, string_types)
    assert getpass.getuser() == username


def test_email_with_git(git_mock):  # noqa
    email = info.email()
    assert "@" in email


def test_email_with_nogit(nogit_mock):  # noqa
    email = info.email()
    assert socket.gethostname() == email.split("@")[1]


def test_git_is_installed(git_mock):  # noqa
    assert info.is_git_installed()


def test_git_is_not_installed(nogit_mock):  # noqa
    assert not info.is_git_installed()


def test_is_git_configured(git_mock):  # noqa
    assert info.is_git_configured()


def test_is_git_not_configured(noconfgit_mock):  # noqa
    assert not info.is_git_configured()


def test_project_raises():
    args = type("Namespace", (object,), {"project": "non_existant"})
    with pytest.raises(RuntimeError):
        info.project(args)


def test_project_without_args(tmpdir):  # noqa
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    runner.main(old_args)
    args = ["my_project"]
    args = runner.parse_args(args)
    new_args = info.project(args)
    assert new_args.url == "http://www.blue-yonder.com/"
    assert new_args.package == "my_project"
    assert new_args.license == "none"
    assert new_args.description == "my description"
    assert new_args.junit_xml is False
    assert new_args.coverage_xml is False
    assert new_args.coverage_html is False


def test_project_with_junit_coverage_args(tmpdir):  # noqa
    old_args = ["my_project", "--with-junit-xml", "--with-coverage-xml",
                "--with-coverage-html"]
    runner.main(old_args)
    args = ["my_project"]
    args = runner.parse_args(args)
    new_args = info.project(args)
    assert new_args.junit_xml is True
    assert new_args.coverage_xml is True
    assert new_args.coverage_html is True


def test_project_with_junit_coverage_args_overwritten(tmpdir):  # noqa
    old_args = ["my_project"]
    runner.main(old_args)
    args = ["my_project", "--with-junit-xml", "--with-coverage-xml",
            "--with-coverage-html"]
    args = runner.parse_args(args)
    new_args = info.project(args)
    assert new_args.junit_xml is True
    assert new_args.coverage_xml is True
    assert new_args.coverage_html is True


def test_project_with_args(tmpdir):  # noqa
    old_args = ["my_project", "-u", "http://www.blue-yonder.com/",
                "-d", "my description"]
    runner.main(old_args)
    args = ["my_project", "-u", "http://www.google.com/",
            "-d", "other description", "-l", "new-bsd"]
    args = runner.parse_args(args)
    new_args = info.project(args)
    assert new_args.url == "http://www.google.com/"
    assert new_args.package == "my_project"
    assert new_args.license == "new-bsd"
    assert new_args.description == "other description"


def test_project_with_no_setup(tmpdir):  # noqa
    os.mkdir("my_project")
    open("my_project/versioneer.py", 'a').close()
    args = ["my_project"]
    args = runner.parse_args(args)
    with pytest.raises(IOError):
        info.project(args)


def test_project_with_wrong_setup(tmpdir):  # noqa
    os.mkdir("my_project")
    open("my_project/versioneer.py", 'a').close()
    open("my_project/setup.py", 'a').close()
    args = ["my_project"]
    args = runner.parse_args(args)
    with pytest.raises(AttributeError):
        info.project(args)


def test_project_with_no_versioneer(tmpdir):  # noqa
    os.mkdir("my_project")
    open("my_project/setup.py", 'a').close()
    args = ["my_project"]
    args = runner.parse_args(args)
    with pytest.raises(IOError):
        info.project(args)
