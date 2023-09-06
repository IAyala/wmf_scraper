#! /bin/bash

source ./scripts/bash_utils.sh

PYTEST_COMMAND='python -B -m pytest -vvv -rfs -p no:cacheprovider -x --junitxml=coverage/junit.xml'
COVERAGE_COMMAND='--cov=src/ --cov-config=.coveragerc --cov-report xml:coverage/cov.xml --cov-report html:coverage/cov_html'

run_tests() {
    print_color "Test Execution (must pass 100%)" $COLOR_PINK
    $PYTEST_COMMAND $COVERAGE_COMMAND $@
    if [ "$?" != "0" ]; then
        print_color "Tests Failed!! (must pass 100%)" $COLOR_RED
        exit 1
    fi
    NUMBER_TESTS=$(pytest --collect-only | grep "<Function\|<Class" -c)
    print_color "Replacing README.md with number of tests" $COLOR_PINK
    sed -i -E "s/tests-([[:digit:]])*/tests-${NUMBER_TESTS}/" README.md
    print_color "Coverage report (must pass 20%)" $COLOR_PINK
    coverage report --precision=2 -m --skip-covered --skip-empty --fail-under=20
    if [ "$?" != "0" ]; then
        print_color "Coverage Failed!! (must pass 20%)" $COLOR_RED
        exit 1
    fi
    print_color "Generating updated coverage badge" $COLOR_PINK
    rm -f coverage_badge/coverage.svg
    coverage-badge -o coverage_badge/coverage.svg
    zip -rj coverage/coverage.zip coverage/cov_html
}

run_ruff() {
  print_color "Running Ruff linting" $COLOR_PINK
  ruff check src
}

run() {
    run_tests $@
    run_ruff $@
    print_end_timestamp
}

run $@
