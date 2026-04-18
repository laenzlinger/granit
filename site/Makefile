.PHONY: help serve build clean kibot render

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

serve: ## Serve site locally with live reload
	hugo mod get && hugo server -D --navigateToChanged

build: ## Build the site
	hugo mod get && hugo --minify

clean: ## Clean generated files
	rm -rf public resources static/3D static/Assembly \
	       static/BoM static/Browse static/JLCPCB \
	       static/PCB static/PCBWay static/Schematic

kibot: ## Run KiBot and copy outputs into static
	cd ../hardware && kibot -e granit.kicad_sch -b granit.kicad_pcb -d generated
	rsync -a ../hardware/generated/ static/

render: ## Render 3D image
	$(MAKE) -C ../hardware render

assembly: ## Copy assembly models into site
	mkdir -p static/assembly
	cp ../mechanical/assembly-slim.step ../mechanical/assembly-wide.step static/assembly/
