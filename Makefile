.PHONY: all clean test dependencies

dependencies/requirements.txt:
	pip-compile --generate-hashes --output-file=dependencies/requirements.txt dependencies/requirements.in

dependencies/dev-requirements.txt: dependencies/requirements.txt
	pip-compile --generate-hashes --allow-unsafe --output-file=dependencies/dev-requirements.txt dependencies/dev-requirements.in

dependencies:
	pip-compile --generate-hashes --output-file=dependencies/requirements.txt dependencies/requirements.in
	pip-compile --generate-hashes --allow-unsafe --output-file=dependencies/dev-requirements.txt dependencies/dev-requirements.in
