SECONDS=0
COLOR_PINK=35
COLOR_GREEN=32
COLOR_RED=31
COLOR_YELLOW=33
COLOR_BLUE=34

export PYTHONIOENCODING=utf-8

now_in_ms() {
    if command -v python &> /dev/null; then
        echo "$(python -c 'from __future__ import print_function; import datetime, time;now=datetime.datetime.now(); print(int(time.mktime(now.utctimetuple())*1000+now.microsecond/1000))')"
    else
        echo "$(date +%s%N | cut -b1-13)"
    fi
}


START="$(now_in_ms)"
LOGURU_FORMAT='{{"level":"{level}","messageDateTime":"{time}","thread":{thread},"message":"{message}","logger.name":"{name}","logger.method_name":"{file}::{module}.{function}","messageTimestampUTC":{time:X!UTC}}}'

print_color() {
    local COLOR=29
    if [ "$2" != "" ]; then
        COLOR=$2
    fi
    printf "\033[0;${COLOR}m%-6s\033[0m" "$1"
    echo
}

trap_handler() {
    SCRIPT_NAME="$0"
    LASTLINE="$1"
    LASTERR="$2"
    print_color "ERROR: in -> ${SCRIPT_NAME}: line ${LASTLINE}: exit status of last command: ${LASTERR}" $COLOR_RED
}

trap '[ $? -eq 0 ] && exit 0 || trap_handler ${LINENO} $?' EXIT

print_end_timestamp() {
    NOW="$(now_in_ms)"
    print_color "Total elapsed time $(($SECONDS / 60)) minutes and $(($SECONDS % 60)) seconds ($(($NOW - $START)) in ms)" $COLOR_PINK
}

source_version() {
    if [ ! -f pyproject.toml ]; then
        print_color "pyproject.toml file does not exist. Setting VERSION to 0.0.0" $COLOR_RED
        export VERSION=0.0.0
    else
        VERSION=$(cat pyproject.toml | grep -m 1 'version' | awk '{print $3}' | tr '"' ' ' | awk '{print $1}')
        print_color "export VERSION=$VERSION" $COLOR_YELLOW
        export VERSION=$VERSION
    fi
}

source_image_version() {
    IMAGE_VERSION=$(cat environment/start_image_dev.sh | grep wmf_scraper: | awk -F ':' '{print $2}')
    print_color "export IMAGE_VERSION=$IMAGE_VERSION" $COLOR_YELLOW
    export IMAGE_VERSION=$IMAGE_VERSION
}

export_env_file() {
    if [ ! -f $1 ]; then
        print_color "Env file does not exist ($1)" $COLOR_RED 
    else
        print_color "Exporting environment variables from $1" $COLOR_PINK
        while IFS="" read -r line || [ -n "$line" ]; do 
            if [[ ! -z "$line" ]] && [[ ! "$line" == "#"* ]]; then
                key=$(echo $line | sed 's/=/ /' | awk '{print $1}' | sed 's/\./_/g' | xargs echo)
                val=$(echo $line | sed 's/=/ /' | awk '{for(i=2;i<=NF-1;i++) print $i" "; print $NF}' | xargs echo)
                if [[ "${val}" == *"$"* ]]; then
                    val=$(eval echo "$val")
                fi
                current_env=$(eval echo "\$$key")
                if [[ ! -z $key ]] && [[ -z "$current_env" ]]; then
                    if [[ "${key}" == *"KEY"* ]] || [[ "${key}" == *"TOKEN"* ]] || [[ "${key}" == *"PASS"* ]] || [[ "${key}" == *"SECRET"* ]]; then
                        print_color "export ${key}=******" $COLOR_YELLOW
                        export "${key}"="${val}"
                    else
                        print_color "export ${key}=${val}" $COLOR_YELLOW
                        export "${key}"="${val}"
                    fi
                else
                    if [[ "${key}" == *"KEY"* ]] || [[ "${key}" == *"TOKEN"* ]] || [[ "${key}" == *"PASS"* ]] || [[ "${key}" == *"SECRET"* ]]; then
                        print_color "variable is already set: ${key}=******" $COLOR_GREEN
                    elif [ "${key}" != "" ]; then
                        print_color "variable is already set: ${key}=${val}, Its set to '${current_env}'" $COLOR_GREEN
                    fi
                fi
            fi
        done < $1
    fi
}

unset_env_file() {
  if [ ! -f $1 ]; then
    print_color "Env file does not exist ($1)" $COLOR_RED 
  else
    print_color "Unsetting environment variables from $1" $COLOR_PINK
      while IFS="" read -r line || [ -n "$line" ]; do 
        if [[ ! -z "$line" ]] && [[ ! "$line" == "#"* ]]; then
          key=$(echo $line | sed 's/=/ /' | awk '{print $1}' | sed 's/\./_/g')
          print_color "Unsetting ${key}" $COLOR_YELLOW
          unset "$key"
        fi
      done < $1
  fi
}
