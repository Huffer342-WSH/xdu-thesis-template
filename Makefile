SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

XDUTS_DIR := .\template\xduts
ROOT_CLS := .\xdupgthesis.cls
XDUTS_WORK_DIR := .\build\xduts-work
WORK_CLS := $(XDUTS_WORK_DIR)\xdupgthesis.cls
WORK_INS := $(XDUTS_WORK_DIR)\xduts.ins
WORK_DTX := $(XDUTS_WORK_DIR)\xduts.dtx

.PHONY: xduts-init xduts-prepare xduts-build xduts-apply build plotting

xduts-init:
	git submodule status template/xduts

xduts-prepare:
	New-Item -ItemType Directory -Force '$(XDUTS_WORK_DIR)' | Out-Null
	Copy-Item -Force '$(XDUTS_DIR)\xduts.ins' '$(WORK_INS)'
	Copy-Item -Force '$(XDUTS_DIR)\xduts.dtx' '$(WORK_DTX)'

xduts-build: xduts-init xduts-prepare
	Push-Location '$(XDUTS_WORK_DIR)'; xetex xduts.ins; Pop-Location

xduts-apply: xduts-build
	Copy-Item -Force '$(WORK_CLS)' '$(ROOT_CLS)'

build:
	latexmk -xelatex -bibtex -synctex=1 -interaction=nonstopmode -file-line-error -logfilewarnings -outdir=build main

build-blind:
	latexmk -xelatex -bibtex -synctex=1 -interaction=nonstopmode -file-line-error -logfilewarnings -outdir=build main_blind

plotting:
	$(MAKE) -C ./scripts/plotting all
