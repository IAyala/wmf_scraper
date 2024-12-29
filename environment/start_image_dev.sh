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
		--mount type=bind,source=$(realpath "${current_dir}/../"),target=/home/coder/source \
		--entrypoint /home/coder/init.sh \
		wmf_scraper:1.1.1
	popd > /dev/null
}

run $@
