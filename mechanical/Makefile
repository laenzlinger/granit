.DEFAULT_GOAL := help
.PHONY: assembly pcb-step end-plates case-models glb clean help

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

case-models: ## Generate Hammond 1455 case models (STL)
	openscad -o out/1455N1601.stl -D 'profile="N"' -D 'length=160' -D '$$fn=64' 1455-case.scad
	openscad -o out/1455T1601.stl -D 'profile="T"' -D 'length=160' -D '$$fn=64' 1455-case.scad
	openscad -o out/1455T1601-body.stl -D 'profile="T"' -D 'length=160' -D 'render_part="body"' -D '$$fn=64' 1455-case.scad
	openscad -o out/1455T1601-lid.stl -D 'profile="T"' -D 'length=160' -D 'render_part="lid"' -D '$$fn=64' 1455-case.scad
	openscad -o out/1455T1601-endplate.stl -D 'profile="T"' -D 'length=160' -D 'render_part="end_plate"' -D '$$fn=64' 1455-case.scad

hdd-models: ## Generate HDD STEP models from OpenSCAD (via STL→STEP)
	openscad -o 2.5inch_HDD.stl -D 'drive="2.5"' hdd.scad
	openscad -o 3.5inch_HDD_NAS.stl -D 'drive="3.5"' hdd.scad
	cd .. && freecadcmd mechanical/stl2step.py

assembly: pcb-step end-plates case-models hdd-models ## Build FreeCAD assembly STEP files
	cd .. && freecadcmd mechanical/assembly.py

glb: ## Convert assembly STEP files to GLB
	cd out && python3 ../step2glb.py

clean: ## Remove generated files
	rm -rf out

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
