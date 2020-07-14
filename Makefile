en:
	PYTHONPATH=$(shell PWD)/plugins ./driver.py english Bert

es:
	PYTHONPATH=$(shell PWD)/plugins ./driver.py spanish Ernie

bad:
	PYTHONPATH=$(shell PWD)/plugins ./driver.py german Cookie

test:
	pytest -xv test.py
