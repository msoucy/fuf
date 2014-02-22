test:
	workon tester
	py.test

clean:
	workon tester
	pythong --wash

upload:
	python setup.py sdist upload --sign
