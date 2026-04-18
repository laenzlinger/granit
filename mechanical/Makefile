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

screenshot: assembly ## Render assembly screenshots (via o3dv in headless Chromium)
	for f in assembly-slim.step assembly-wide.step; do \
		node screenshot.mjs $$f $${f%.step}.png; \
	done

clean:
	rm -f granit-pcb.step assembly-slim.step assembly-wide.step assembly-slim.png assembly-wide.png

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
