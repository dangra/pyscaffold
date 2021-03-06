#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import pytest
from pyscaffold import runner

from .fixtures import git_mock, nogit_mock, noconfgit_mock, tmpdir  # noqa

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_parse_args():
    args = ["my-project"]
    opts = runner.parse_args(args)
    assert opts.package == "my_project"


def test_main_with_nogit(nogit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_with_git_not_configured(noconfgit_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_when_folder_exists(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    os.mkdir(args[0])
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    runner.main(args)
    assert os.path.exists(args[0])


def test_main_when_updating(tmpdir, git_mock):  # noqa
    args = ["my-project"]
    runner.main(args)
    args = ["--update", "my-project"]
    runner.main(args)
    assert os.path.exists(args[1])


def test_main_when_updating_with_wrong_setup(tmpdir, git_mock):  # noqa
    os.mkdir("my_project")
    open("my_project/versioneer.py", 'a').close()
    open("my_project/setup.py", 'a').close()
    args = ["--update", "my_project"]
    with pytest.raises(RuntimeError):
        runner.main(args)


def test_main_with_license(tmpdir, git_mock):  # noqa
    args = ["my-project", "-l", "new-bsd"]
    runner.main(args)
    assert os.path.exists(args[0])


def test_run(tmpdir, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    runner.run()
    assert os.path.exists(sys.argv[1])


def test_overwrite_git_repo(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "my_project"]
    runner.run()
    with pytest.raises(SystemExit):
        runner.run()
    sys.argv = ["pyscaffold", "--force", "my_project"]
    runner.run()


def test_overwrite_dir(tmpdir):  # noqa
    os.mkdir("my_project")
    sys.argv = ["pyscaffold", "--force", "my_project"]
    runner.run()


def test_django_proj(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-django", "my_project"]
    runner.run()


def test_with_travis(tmpdir):  # noqa
    sys.argv = ["pyscaffold", "--with-travis", "my_project"]
    runner.run()
