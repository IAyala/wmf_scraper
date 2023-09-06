#! /bin/bash

source ${HOME}/source/scripts/bash_utils.sh

print_general_help() {
    echo
    print_color "Welcome to the Development Environment available functions" $COLOR_GREEN
    echo
    print_color "Syntax: help [test|precommit]" $COLOR_PINK
    echo
    print_color "options:" $COLOR_WHITE
    print_color "test                 Prints the test function help" $COLOR_YELLOW
    print_color "precommit            Prints the precommit function help" $COLOR_YELLOW
    print_color "bump_version         Bumps version and creates tag" $COLOR_YELLOW
    print_color "bump_image_version   Bumps docker image version" $COLOR_YELLOW
    echo
}

print_test_help() {
    print_color "The 'test' function runs the app tests in the terminal" $COLOR_GREEN
    print_color "It runs 'pytest' under the hood and will run all tests by default" $COLOR_GREEN
    print_color "You can pass any argument that is accepted by the 'pytest' library to it" $COLOR_GREEN
    print_color "In example, if you want to run a 'specific_test', you can run:" $COLOR_GREEN
    print_color 'test -k "specific_test"' $COLOR_YELLOW
}

print_precommit_help() {
    print_color "The 'precommit' function runs the 'pre-commit' script on the app" $COLOR_GREEN
}

print_bump_help() {
    print_color "Run with one of the allowed options: patch | minor | major" $COLOR_GREEN
}

help() {
    local argument="$1"
    case "$argument" in
        test)
            print_test_help $@
        ;;
        precommit)
            print_precommit_help $@
        ;;
        bump)
            print_bump_help $@
        ;;
        bump_docker)
            print_bump_help $@
        ;;
        *)
            print_general_help $@
        ;;
    esac
}

help $@
