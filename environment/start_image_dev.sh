#! /bin/bash

run () {
	local current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
	pushd $current_dir > /dev/null
	docker stop wmf_scraper || true
	docker rm wmf_scraper || true
	docker run \
	    --security-opt seccomp=unconfined \
		--name wmf_scraper \
		-p 8888:8888 \
		-p 8000:8000 \
		-v ${current_dir}/../:/home/coder/source \
		--entrypoint /home/coder/init.sh \
		wmf_scraper:0.1.0
	popd > /dev/null
}

run $@
