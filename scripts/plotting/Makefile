PYTHON := ../../.venv/Scripts/python.exe

SCRIPTS := $(wildcard fig_*.py)

.PHONY: all $(SCRIPTS:.py=) help

all: $(SCRIPTS:.py=)


$(SCRIPTS:.py=):
	PLOT_SHOW=0 SAVE_FIGURES=1 $(PYTHON) $@.py

help:
	@echo "Available targets:"
	@echo "  all    - Generate all figures (default)"
	@echo "  help   - Show this help message"
	@echo "Available python scripts:"
	@for s in $(SCRIPTS); do echo "  $$s"; done
	@echo "Usage:"
	@echo "  make <fig_name_without_py>  (e.g., make fig_demo)"
