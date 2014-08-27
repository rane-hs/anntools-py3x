#!/bin/sh

CWD=`pwd`
export PYTHONPATH="$CWD"

do_tests () {
    PYTHON=$1
    echo "$PYTHON: =============================================="
    $PYTHON tests/test_conversion.py
    $PYTHON tests/test_cooperation.py
    $PYTHON tests/test_typecheck.py
    $PYTHON tests/test_validation.py
}

do_tests python2.4
do_tests python2.5
do_tests python2.6
do_tests python3.0
