.DEFAULT_GOAL := help
.PHONY: assembly pcb-step end-plates screenshot clean help

PCB_DIR := ../hardware

pcb-step: ## Export PCB STEP from KiCad (connectors only, no CM4)
	cd $(PCB_DIR) && kicad-cli pcb export step \
		--define-var GIT_HASH=$$(git rev-parse --short HEAD) \
		--output ../mechanical/granit-pcb.step \
		--subst-models --force \
		--component-filter "J1,J2,J4,J7,J8,BT1,SW1,D1" \
		granit.kicad_pcb

end-plates: ## Generate end plate outputs (STL + DXF)
	for v in slim wide; do \
		openscad -o end-plate-$$v.stl -D "variant=\"$$v\"" -D '$$fn=64' end-plate.scad; \
		openscad -o end-plate-$$v.dxf -D "variant=\"$$v\"" -D 'mode="2d"' end-plate.scad; \
	done

assembly: pcb-step end-plates ## Build FreeCAD assembly STEP files
	cd .. && freecadcmd mechanical/assembly.py

screenshot: assembly ## Render assembly screenshots (o3dv via headless Chromium)
	npm install --silent 2>/dev/null
	for f in assembly-slim.step assembly-wide.step; do \
		node screenshot.mjs $$f $${f%.step}.png; \
	done

clean: ## Remove generated files
	rm -f granit-pcb.step assembly-slim.step assembly-wide.step \
	      assembly-slim.png assembly-wide.png \
	      end-plate-slim.stl end-plate-wide.stl \
	      end-plate-slim.dxf end-plate-wide.dxf

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
