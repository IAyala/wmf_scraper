source /home/coder/source/scripts/bash_utils.sh
source /home/coder/source/scripts/bash_functions.sh
print_color "Loading Pyenv" $COLOR_PINK
export PATH="/home/coder/.pyenv/bin:$PATH"
source_version
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
echo
print_color "############################" $COLOR_GREEN
print_color "#                          #" $COLOR_GREEN
print_color "#   ENVIRONMENT IS READY   #" $COLOR_GREEN
print_color "#       run 'help' to      #" $COLOR_GREEN
print_color "#        see options       #" $COLOR_GREEN
print_color "#                          #" $COLOR_GREEN
print_color "############################" $COLOR_GREEN
print_color "Python version:" $COLOR_PINK
python -V
print_color "Current wmf_scraper version" $COLOR_BLUE
echo $VERSION
