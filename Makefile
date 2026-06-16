# Nasim — task runner. The CI/CD loop lives in .claude/rules/cicd-loop.md.
PY ?= python3
PYTEST ?= $(PY) -m pytest
export PYTHONPATH := src:$(PYTHONPATH)

.PHONY: help lint test unit integration capability rollback e2e deploy loop install uninstall clean

help: ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

lint: ## ruff + black --check + import smoke
	-$(PY) -m ruff check src test
	-$(PY) -m black --check src test
	$(PY) -c "import nasim, nasim.config; nasim.config.Config.load(); print('import + config OK')"

test: unit ## alias for the fast unit tests

unit: ## pure unit tests (no network)
	$(PYTEST) test/unit

integration: ## tests against the live bridge
	$(PYTEST) -m integration test/integration

capability: ## Anthropic API capability matrix (live bridge)
	$(PYTEST) -m capability test/capability

rollback: ## nasim start/stop rollback contract
	$(PYTEST) -m rollback test/rollback

e2e: ## real claude binary writes/edits files via Ollama
	# Direct mode (native) tested manually or via integration that only needs ssh+ollama (no bridge service)

test-direct: ## quick direct native reachability (requires ssh black + ollama on black)
	python -m nasim direct-start || true
	python -c "
import urllib.request, json, os
base = 'http://localhost:11434'
print('direct base:', base)
data = json.loads(urllib.request.urlopen(base + '/api/tags', timeout=6).read())
print('models on black via direct:', [m['name'] for m in data.get('models', [])][:3])
" 
	python -m nasim direct-stop || true
	$(PYTEST) -m e2e test/e2e

deploy: ## push the bridge to the server and restart the service
	bash src/nasim/bridge/deploy/deploy.sh

loop: ## full CI/CD loop (E2E=1 to include e2e)
	bash bin/loop.sh

install: ## install the nasim shell function into your profile
	bash install.sh

uninstall: ## remove the nasim shell function
	bash uninstall.sh

clean: ## remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
