#! /bin/bash

run () {
	local current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
	pushd $current_dir > /dev/null
	docker stop wmf_scraper || true
	docker rm wmf_scraper || true
	docker run -d -t \
		--name wmf_scraper \
		--mount type=bind,source=$(realpath "${current_dir}/../"),target=/home/coder/source \
		wmf_scraper:1.1.1
	popd > /dev/null
}

run $@
