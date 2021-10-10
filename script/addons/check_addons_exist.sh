#!/usr/bin/env bash
# TODO check only in config path and not all code
# TODO missing path of odoo
FILE_NAME=$1
COUNT=$(find . -name "${FILE_NAME}"|wc -l)
if [[ $COUNT -eq 0 ]]; then
  echo "ERROR cannot find module name '${FILE_NAME}'."
  exit 1
elif [[ $COUNT -eq 1 ]]; then
  exit 0
else
  echo "ERROR contains ${COUNT} module name '${FILE_NAME}', will create error at installation."
  exit 2
fi
