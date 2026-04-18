.DEFAULT_GOAL := help
.PHONY: test step pdf render pos clean

GIT_HASH = $(shell git rev-parse --short HEAD)
REVISION ?= $(shell git describe --tags --abbrev=0 2>/dev/null || echo dev)
PROJECT_NAME = granit

test: ## Run ERC and DRC checks
	mkdir -p out
	kicad-cli sch erc \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/erc.rpt \
		--severity-warning \
		--severity-error \
		--exit-code-violations \
		$(PROJECT_NAME).kicad_sch
	kicad-cli pcb drc \
		--schematic-parity \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/drc.rpt \
		--severity-error \
		--severity-warning \
		--exit-code-violations \
		$(PROJECT_NAME).kicad_pcb

step: ## Export 3D model
	mkdir -p out
	kicad-cli pcb export step \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/$(PROJECT_NAME).step \
		--subst-models \
		--force \
		$(PROJECT_NAME).kicad_pcb

pdf: ## Export PDF (schematic and PCB)
	mkdir -p out
	kicad-cli pcb export pdf \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/$(PROJECT_NAME)-pcb-front.pdf \
		--layers F.Cu \
		$(PROJECT_NAME).kicad_pcb
	kicad-cli pcb export pdf \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/$(PROJECT_NAME)-pcb-back.pdf \
		--layers B.Cu \
		$(PROJECT_NAME).kicad_pcb
	kicad-cli sch export pdf \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output out/$(PROJECT_NAME)-schematic.pdf \
		$(PROJECT_NAME).kicad_sch

render: ## Render 3D board image for README
	mkdir -p ../site/static/images
	kicad-cli pcb render \
		--define-var GIT_HASH=$(GIT_HASH) \
		--define-var REVISION=$(REVISION) \
		--output ../site/static/images/$(PROJECT_NAME)-3d.png \
		--width 1600 --height 900 \
		--side top --quality high \
		--rotate -30,0,0 \
		--background opaque \
		$(PROJECT_NAME).kicad_pcb

pos: ## Export position file for OpenPnP
	mkdir -p out
	kicad-cli pcb export pos \
		--output /dev/stdout \
		--format csv \
		--side both \
		--units mm \
		--smd-only \
		--exclude-dnp \
		$(PROJECT_NAME).kicad_pcb \
	| python3 ~/.openpnp2/remap-pnp.py > out/$(PROJECT_NAME).pos.csv

clean:
	rm -rf out

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
