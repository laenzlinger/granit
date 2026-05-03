.DEFAULT_GOAL := help
.PHONY: test step pdf pnp feeder-map setup save clean

GIT_HASH = $(shell git rev-parse --short HEAD)
REVISION ?= $(shell git describe --tags --exact-match 2>/dev/null || echo dev)
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

pnp: ## Generate OpenPnP position file and board XML
	kicad-cli pcb export pos \
		--output /dev/stdout \
		--format csv \
		--side both \
		--units mm \
		--smd-only \
		--exclude-dnp \
		$(PROJECT_NAME).kicad_pcb \
	| openpnp-tools generate -o pnp -n $(PROJECT_NAME) --board-width 92 --board-height 99.5
	openpnp-tools ensure-parts pnp/$(PROJECT_NAME).board.xml

feeder-map: ## Generate HTML feeder layout map
	kicad-cli sch export bom \
		--fields "Value,Footprint,IPN" \
		--labels "Value,Footprint,IPN" \
		--group-by "Value,Footprint,IPN" \
		--exclude-dnp \
		-o pnp/bom.csv \
		$(PROJECT_NAME).kicad_sch
	openpnp-tools map --bom pnp/bom.csv \
		-o pnp/feeder-map.html pnp/$(PROJECT_NAME).job.xml

setup: ## Apply base config and assign feeders (OpenPnP must be closed)
	openpnp-tools config apply
	openpnp-tools assign --reset-unused pnp/feeders.csv

save: ## Pull tuning changes and commit to config repo (OpenPnP must be closed)
	openpnp-tools config save -m "tuning: update from $(PROJECT_NAME)"

clean:
	rm -rf out

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
