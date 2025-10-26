# DATA-MINER Makefile avec Go Runner local
# Alternative aux GitHub Actions via exécution locale PC
# Intégration DevTools Hub + ECOYSTEM Orchestrator

.PHONY: install analyze dashboard clean test local-runner help

# Variables
PYTHON := python3
PIP := pip3
GO := go
REQS := requirements.txt
LOCAL_RUNNER := src/local_runner/go_runner_integration
PS_RUNNER := scripts/local_ci_runner.ps1

## Installation complète avec runner local
install:
	@echo "🔧 Installation DATA-MINER avec Go Runner local..."
	$(PIP) install -r $(REQS)
	$(GO) mod tidy
	$(GO) build -o bin/data-miner-runner $(LOCAL_RUNNER).go
	@echo "✅ Installation terminée (runner local compilé)"

## Démarrage runner local (alternative GitHub Actions)
local-runner-start:
	@echo "🚀 Démarrage Go Runner local..."
	@if [ -f "bin/data-miner-runner" ]; then \
		./bin/data-miner-runner config/go_runner.json & \
		echo "Runner PID: $$!" > .runner.pid; \
		echo "✅ Go Runner démarré (PID: $$!)"; \
	else \
		echo "❌ Runner non compilé - exécuter: make install"; \
		exit 1; \
	fi

## Démarrage runner PowerShell (Windows)
local-runner-ps1:
	@echo "🚀 Démarrage PowerShell Runner..."
	pwsh -File $(PS_RUNNER) -Action start-runner -Schedule daily -Verbose

## Arrêt runner local
local-runner-stop:
	@echo "⏹️ Arrêt runner local..."
	@if [ -f ".runner.pid" ]; then \
		kill $$(cat .runner.pid) 2>/dev/null || true; \
		rm .runner.pid; \
		echo "✅ Runner arrêté"; \
	else \
		echo "⚠️ Aucun runner actif trouvé"; \
	fi

## Status runner
local-runner-status:
	@echo "📊 Status Go Runner local:"
	@if [ -f ".runner.pid" ] && kill -0 $$(cat .runner.pid) 2>/dev/null; then \
		echo "✅ Runner actif (PID: $$(cat .runner.pid))"; \
		echo "📁 Workspace: ./workspace/"; \
		echo "📝 Logs: ./logs/runner/"; \
	else \
		echo "❌ Runner inactif"; \
	fi

## Analyse écosystème (via runner local si actif, sinon direct)
analyze-ecosystem:
	@echo "🔍 Mining ECOSYSTEM-1..."
	@if [ -f ".runner.pid" ] && kill -0 $$(cat .runner.pid) 2>/dev/null; then \
		echo "📡 Exécution via Go Runner local..."; \
		curl -X POST http://localhost:8080/api/jobs/ecosystem-mining || \
		echo "⚠️ API runner inaccessible - exécution directe"; \
	fi
	$(PYTHON) scripts/ecosystem_mining.py --comprehensive
	@echo "📊 Résultats dans data/mining_results/"

## Dashboard avec runner local
dashboard-start:
	@echo "📊 Démarrage dashboard MSR..."
	@if [ -f ".runner.pid" ] && kill -0 $$(cat .runner.pid) 2>/dev/null; then \
		echo "🔗 Dashboard intégré au runner local"; \
	fi
	streamlit run dashboards/ecosystem_dashboard.py --server.port 8501

## Validation anti-patterns via runner local
check-antipatterns:
	@echo "🚨 Vérification anti-patterns..."
	$(PYTHON) src/governance/ci_gatekeeper.py --validate-ecosystem

## Tests avec runner local si disponible
test:
	@echo "🧪 Exécution tests..."
	pytest tests/ -v --cov=src/
	@if [ -f ".runner.pid" ] && kill -0 $$(cat .runner.pid) 2>/dev/null; then \
		echo "📤 Résultats envoyés au runner local"; \
	fi

## Installation alternatives complètes
install-alternatives:
	@echo "⚙️ Installation alternatives GitHub Actions..."
	@chmod +x scripts/local_alternatives.sh
	@./scripts/local_alternatives.sh

## Nettoyage avec préservation runner
clean:
	@echo "🧹 Nettoyage (préservation runner)..."
	rm -rf data/temp/ .pytest_cache/ __pycache__/
	@echo "✅ Nettoyage terminé (runner préservé)"

## Synchronisation DevTools Hub
sync-devtools:
	@echo "🔄 Synchronisation DevTools Hub..."
	@# Logique de sync avec DevTools (à définir selon votre setup)
	git fetch --all
	@echo "✅ Sync DevTools terminée"

## Dashboard mise à jour données
dashboard-update:
	@echo "📊 Mise à jour données dashboard..."
	$(PYTHON) dashboards/ecosystem_dashboard.py --update-data --no-server

## Aide complète
help:
	@echo "DATA-MINER - Alternatives GitHub Actions (Self-Hosted)"
	@echo "="*60
	@echo "🎯 OBJECTIF: Éviter tokens payants GitHub Actions"
	@echo "🖥️  SOLUTION: Runner local Go + PowerShell + alternatives"
	@echo ""
	@echo "Commandes principales:"
	@echo "  install              - Installation complète + compilation runner Go"
	@echo "  local-runner-start   - Démarrage Go Runner local"
	@echo "  local-runner-ps1     - Démarrage PowerShell Runner (Windows)"
	@echo "  local-runner-stop    - Arrêt runner local"
	@echo "  local-runner-status  - Status runner actuel"
	@echo ""
	@echo "Analyse & Mining:"
	@echo "  analyze-ecosystem    - Mining ECOSYSTEM-1 via runner local"
	@echo "  check-antipatterns   - Validation governance"
	@echo "  dashboard-start      - Dashboard intégré runner"
	@echo ""
	@echo "Alternatives GitHub Actions:"
	@echo "  install-alternatives - ACT, Drone.io, Jenkins, Cron+Make"
	@echo ""
	@echo "Utilitaires:"
	@echo "  sync-devtools        - Sync avec DevTools Hub"
	@echo "  dashboard-update     - Mise à jour données uniquement"
	@echo "  test                 - Tests avec intégration runner"
	@echo "  clean                - Nettoyage (préserve runner)"