#! /bin/bash

source ${HOME}/source/scripts/bash_utils.sh

bump() {
    if [[ $1 == "docker" ]]; then
        BUMP_TYPE="$2"
        CONFIG="setup.image.cfg"
    else
        BUMP_TYPE="$1"
        CONFIG="setup.cfg"
    fi

    if [[ ${BUMP_TYPE} == "patch" || ${BUMP_TYPE} == "minor" || ${BUMP_TYPE} == "major" ]]; then
        print_color "Bumping version using ${BUMP_TYPE} option"
        bump2version --config-file ${HOME}/source/${CONFIG} ${BUMP_TYPE} --allow-dirty
        if [ "$?" != "0" ]; then
            exit 1
        fi
        if [[ $1 != "docker" ]]; then
            git push --tags
        fi
    else
        echo "Error: First argument is not in [patch | minor | major]." >&2
        exit 1
    fi
}

bump $@
