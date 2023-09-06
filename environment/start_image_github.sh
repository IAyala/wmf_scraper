#! /bin/bash

run () {
	local current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
	pushd $current_dir > /dev/null
	docker stop wmf_scraper || true
	docker rm wmf_scraper || true
	docker run -d -t \
		--name wmf_scraper \
		-v ${current_dir}/../:/home/coder/source \
		wmf_scraper:0.0.1
	popd > /dev/null
}

run $@
