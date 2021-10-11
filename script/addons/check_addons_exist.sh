#!/usr/bin/env bash
# TODO check only in config path and not all code
FILE_NAME=$1
# Need to split by , when contain multiple file_name
#FILE_NAME_ARR=($(echo $FILE_NAME | tr "," "\n"))
IFS=',' read -ra FILE_NAME_ARR <<< "$FILE_NAME"

for i in "${FILE_NAME_ARR[@]}"; do
  COUNT=$(find ./addons ./odoo -name "${i}"|wc -l)
  if [[ $COUNT -eq 0 ]]; then
    echo "ERROR cannot find module name '${i}'."
    exit 1
  elif [[ $COUNT -ne 1 ]]; then
    echo "ERROR contains ${COUNT} module name '${i}', will create error at installation."
    find . -name "${i}"
    exit 2
  fi
done
exit 0
