pkg_version := $(shell sed -n '/version=/p' setup.py | sed "s/[',]//g" | awk -F'=' '{print $$2}')
py_version := $(shell python -V 2>&1 | awk '{print $$2}' | awk -F'.' '{print $$1"."$$2}')
target_egg := ganglia_alert-${pkg_version}-py${py_version}.egg

gen_target_egg :
	python setup.py build
	python setup.py sdist
	python setup.py bdist_egg
	$(info generate and install dist/${target_egg})

install:
	easy_install dist/${target_egg}

clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf ganglia_alert.egg-info

