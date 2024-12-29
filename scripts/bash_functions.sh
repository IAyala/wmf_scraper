#! /bin/bash

source_utils () {
  local current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
  pushd $current_dir
  source ./bash_utils.sh
  popd
}

source_utils

print_color "Adding 'test' function to bash" $COLOR_PINK
test () {
    ${HOME}/source/scripts/run_tests.sh $@
}
print_color "Adding 'precommit' function to bash" $COLOR_PINK
precommit () {
    ${HOME}/source/scripts/run_precommit.sh $@
}
print_color "Adding 'build' function to bash" $COLOR_PINK
build () {
    ${HOME}/source/scripts/run_build.sh $@
}
print_color "Adding 'bump_version' function to bash" $COLOR_PINK
bump_version () {
    ${HOME}/source/scripts/run_bump.sh $@
}
print_color "Adding 'help' function to bash" $COLOR_PINK
help () {
    ${HOME}/source/scripts/run_help.sh $@
}
