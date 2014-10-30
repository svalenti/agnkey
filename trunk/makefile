############################################################
# this is a make file to mount the agnagent pipeline
#
#
#
#
#
###########################################################
ROOTDIR= /Users/svalenti/redu
PREFIX=/Users/svalenti

PYTHON    = /usr/bin/env python
TSCRIPT   = ./setup.py install --prefix=$(PREFIX)



all:  test

build: clean
	$(PYTHON) setup.py build

install: build
	if test $(PYTHON) = /usr/bin/env python; then \
		$(PYTHON) setup.py install --prefix=$(PREFIX); \
	elif test $(PYTHON) = /usr/bin/env python; then \
                $(PYTHON) setup.py install --prefix=$(PREFIX); \
	else \
                $(PYTHON) setup.py install --prefix=$(PREFIX); \
	fi

uninstall:
        if test $(PYTHON) = /usr/bin/env python; then \
                pip-2.4 uninstall -y -v psutil; \
        else \
                cd ..; $(PYTHON) -m pip uninstall -y -v psutil; \
        fi

test: install
	$(PYTHON) $(TSCRIPT) 


clean:
	rm -rf build
	rm -rf dist
