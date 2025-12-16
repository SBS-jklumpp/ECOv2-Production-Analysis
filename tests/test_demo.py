#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Pytest demo module"""

# Native imports
import importlib.resources
from logging import getLogger

# Third-party imports
import pytest

# Sea-Bird imports

# Internal imports
import testresources

logger = getLogger(__name__)

datafiles = importlib.resources.files(testresources).resolve()
logger.debug("Path to datafiles: %r", datafiles)

def test_that_should_pass():

    assert True

@pytest.mark.xfail
def test_that_should_fail():

    assert False

def test_that_uses_datafile():

    with open(datafiles / 'datafile.txt') as f:
        assert "todo delete me" in f.read()

def test_that_uses_caplog(caplog):

    caplog.set_level('DEBUG')

    logger.debug("NOTHING TO SEE HERE")
    assert "SECRET TEXT" not in caplog.text

    logger.debug("SECRET TEXT")
    assert "SECRET TEXT" in caplog.text

    logger.debug("I read caplog.text and it said %r", caplog.text)

def test_that_exc_raised():

    with pytest.raises(ZeroDivisionError):
        what_could_go_wrong = 1 / 0
