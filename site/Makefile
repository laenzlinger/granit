.PHONY: help serve build clean kibot

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

serve: ## Serve site locally with live reload
	cd site && hugo mod get && hugo server -D --navigateToChanged

build: ## Build the site
	cd site && hugo mod get && hugo --minify

clean: ## Clean generated files
	rm -rf site/public site/resources site/static/3D site/static/Assembly \
	       site/static/BoM site/static/Browse site/static/JLCPCB \
	       site/static/PCB site/static/PCBWay site/static/Schematic

kibot: ## Run KiBot and copy outputs into site/static
	cd hardware && kibot -e granit.kicad_sch -b granit.kicad_pcb -d generated
	rsync -a hardware/generated/ site/static/
	mkdir -p site/static/images
	cp hardware/generated/3D/*.png site/static/images/ 2>/dev/null || true
