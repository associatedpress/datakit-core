#!/usr/bin/env python
# -*- coding: utf-8 -*-
import errno
import os

import pytest

from datakit import utils


def test_home_dir_from_env_vars(monkeypatch):
    custom_home = '/opt/custom-home'
    monkeypatch.setenv('DATAKIT_HOME', custom_home)
    assert utils.home_dir() == custom_home


def test_home_dir_default():
    user_home = os.path.join(os.path.expanduser('~'), '.datakit')
    assert utils.home_dir() == user_home


def test_mkdir_p_creates_dir(tmpdir):
    target = os.path.join(tmpdir.strpath, 'a', 'b')
    utils.mkdir_p(target)
    assert os.path.isdir(target)


def test_mkdir_p_existing_dir_is_noop(tmpdir):
    target = tmpdir.strpath
    utils.mkdir_p(target)
    assert os.path.isdir(target)


def test_mkdir_p_reraises_non_eexist_errors(tmpdir, mocker):
    mocker.patch(
        'os.makedirs',
        side_effect=OSError(errno.EACCES, 'Permission denied'),
    )
    with pytest.raises(OSError):
        utils.mkdir_p(tmpdir.strpath)


def test_dist_for_obj_uses_dist_attributes():
    obj = type('Obj', (), {})()
    obj.dist = type('Dist', (), {'project_name': 'datakit-test-plugin', 'version': '1.2.3'})()
    assert utils.dist_for_obj(obj) == 'datakit-test-plugin (1.2.3)'


def test_dist_for_obj_omits_blank_version():
    obj = type('Obj', (), {})()
    obj.dist = type('Dist', (), {'project_name': 'datakit-test-plugin', 'version': ''})()
    assert utils.dist_for_obj(obj) == 'datakit-test-plugin'


def test_dist_for_obj_falls_back_to_cliff_without_dist():
    obj = type('Obj', (), {})()
    assert utils.dist_for_obj(obj) == 'cliff'
