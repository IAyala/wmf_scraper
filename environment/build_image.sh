#! /bin/bash

run () {
	local current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
	pushd $current_dir > /dev/null
	buildkit_progress=plain docker build \
	  -f Dockerfile.dev \
	  -t wmf_scraper:1.0.0 \
	  --progress=plain \
	  ..
	popd > /dev/null
}

run
