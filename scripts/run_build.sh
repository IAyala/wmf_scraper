#! /bin/bash

source_utils() {
    source ./scripts/bash_utils.sh
}

source_bashrc() {
    source $HOME/.bashrc
}

source_pyenv() {
    print_color "Loading Pyenv" $COLOR_PINK
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyven virtualenv-init -)"
}

build_library () {
    poetry build
}

run() {
    source_bashrc $@
    source_utils $@
    source_pyenv $@
    build_library $@
}

run $@
