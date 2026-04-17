.DEFAULT_GOAL := help
.PHONY: help build clean

PIGEN_DIR := pi-gen-upstream

$(PIGEN_DIR):
	git clone --depth 1 https://github.com/RPi-Distro/pi-gen.git $(PIGEN_DIR)

build: $(PIGEN_DIR) ## Build Granit OS image (Docker/Podman)
	cp pi-gen/config $(PIGEN_DIR)/config
	cp -r pi-gen/stage-granit $(PIGEN_DIR)/
	touch $(PIGEN_DIR)/stage3/SKIP $(PIGEN_DIR)/stage4/SKIP $(PIGEN_DIR)/stage5/SKIP
	touch $(PIGEN_DIR)/stage3/SKIP_IMAGES $(PIGEN_DIR)/stage4/SKIP_IMAGES $(PIGEN_DIR)/stage5/SKIP_IMAGES
	chmod +x $(PIGEN_DIR)/stage-granit/*/00-run.sh $(PIGEN_DIR)/stage-granit/*/*.sh 2>/dev/null || true
	# Patch: skip arch-test (unreliable under Docker binfmt emulation)
	sed -i 's/if ! arch-test/if false \&\& ! arch-test/' $(PIGEN_DIR)/build.sh
	cd $(PIGEN_DIR) && ./build-docker.sh

clean: ## Remove build artifacts
	docker rm -v pigen_work 2>/dev/null || true
	rm -rf $(PIGEN_DIR)

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
