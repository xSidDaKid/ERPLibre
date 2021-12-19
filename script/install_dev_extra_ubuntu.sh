#!/usr/bin/env bash

# Need this for test extra

if [[ "${OSTYPE}" == "linux-gnu" ]]; then
    OS=$(lsb_release -si)
    VERSION=$(cat /etc/issue)
    if [[ "${OS}" == "Ubuntu" ]]; then
        if [[  "${VERSION}" == Ubuntu\ 18.04* || "${VERSION}" == Ubuntu\ 20.04* ]]; then
            sudo apt install mariadb-client mariadb-server
        else
            echo "Your version is not supported, only support 18.04 and 20.04 : ${VERSION}"
        fi
    else
        echo "Your Linux system is not supported, only support Ubuntu 18.04 or Ubuntu 20.04."
    fi
fi
