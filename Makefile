test:
	py.test

clean:
	pythong --wash

upload:
	python setup.py sdist upload --sign
