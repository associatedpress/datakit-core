#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from datakit import utils


def test_home_dir_from_env_vars(monkeypatch):
    custom_home = '/opt/custom-home'
    monkeypatch.setenv('DATAKIT_HOME', custom_home)
    assert utils.home_dir() == custom_home


def test_home_dir_default():
    user_home = os.path.join(os.path.expanduser('~'), '.datakit')
    assert utils.home_dir() == user_home
