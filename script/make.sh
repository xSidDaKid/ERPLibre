#!/usr/bin/env bash
echo "
===> ${@}
"
time make $@
echo "
<=== ${@}
"
