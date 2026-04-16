.DEFAULT_GOAL := help
.PHONY: assembly pcb-step clean help

PCB_DIR := ../hardware

pcb-step: ## Export PCB STEP from KiCad
	cd $(PCB_DIR) && kicad-cli pcb export step \
		--define-var GIT_HASH=$$(git rev-parse --short HEAD) \
		--output ../mechanical/granit-pcb.step \
		--subst-models --force granit.kicad_pcb

assembly: pcb-step ## Build FreeCAD assemblies (slim + wide, colored 3MF)
	cd .. && freecadcmd mechanical/assembly.py

screenshot: assembly ## Render assembly screenshots
	cd .. && unset WAYLAND_DISPLAY && \
	for f in mechanical/assembly-slim.3mf mechanical/assembly-wide.3mf; do \
		LIBGL_ALWAYS_SOFTWARE=1 ASSEMBLY_FILE=$$f \
		xvfb-run -a -s "-screen 0 2160x2160x24" freecad mechanical/screenshot.py; \
	done; true

clean:
	rm -f granit-pcb.step assembly-slim.3mf assembly-wide.3mf assembly-slim.png assembly-wide.png

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
