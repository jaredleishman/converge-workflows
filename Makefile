.PHONY: validate test check

validate:
	python scripts/validate.py

test:
	python -m unittest discover -s tests -v

check: validate test
