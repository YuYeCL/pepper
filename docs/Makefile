# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXBUILD         = sphinx-build
SPHINXAPI           = sphinx-apidoc

PROJECTDIR          = ../pepper
SOURCEDIR           = source
BUILDDIR            = build

SPHINXAPIOPTS       = -e -M -f -d 1
SPHINXBUILDOPTS     =

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXBUILDOPTS) $(O)

.PHONY: help Makefile

api:
	$(SPHINXAPI) $(SPHINXAPIOPTS) -o "$(SOURCEDIR)" "$(PROJECTDIR)"
	python api_postprocess.py

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXBUILDOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXBUILDOPTS) $(O)