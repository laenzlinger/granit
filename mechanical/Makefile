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
	@mkdir -p out
	for v in slim wide; do \
		openscad -o out/end-plate-$$v.stl -D "variant=\"$$v\"" -D '$$fn=64' end-plate.scad; \
		openscad -o out/end-plate-$$v.dxf -D "variant=\"$$v\"" -D 'mode="2d"' end-plate.scad; \
	done

case-models: ## Generate Hammond 1455 case models (STL)
	@mkdir -p out
	@for spec in "L 220 1455L2201" "T 220 1455T2201" "T 160 1455T1601" "N 160 1455N1601"; do \
		set -- $$spec; \
		for part in body lid end_plate; do \
			openscad -o out/$$3-$$part.stl -D "profile=\"$$1\"" -D "length=$$2" -D "render_part=\"$$part\"" -D '$$fn=64' 1455-case.scad; \
		done; \
	done

hdd-models: ## Generate HDD STEP models from OpenSCAD (via STL→STEP)
	openscad -o out/2.5inch_HDD.stl -D 'drive="2.5"' hdd.scad
	openscad -o out/3.5inch_HDD_NAS.stl -D 'drive="3.5"' hdd.scad
	cd .. && freecadcmd mechanical/stl2step.py

assembly: pcb-step end-plates case-models hdd-models ## Build FreeCAD assembly STEP files
	cd .. && freecadcmd mechanical/assembly.py

glb: ## Convert assembly STEP files to GLB
	python3 step2glb.py out/assembly-*.step

clean: ## Remove generated files
	rm -rf out

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
