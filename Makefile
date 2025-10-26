# DATA-MINER Makefile
# Inspiré du Makefile EMAIL-SENDER-1 (11KB) optimisé MSR

.PHONY: install analyze dashboard clean test

# Variables
PYTHON := python3
PIP := pip3
REQS := requirements.txt

## Installation
install:
	@echo "🔧 Installation DATA-MINER..."
	$(PIP) install -r $(REQS)
	@echo "✅ Installation terminée"

## Analyse écosystème complète
analyze-ecosystem:
	@echo "🔍 Analyse ECOSYSTEM-1..."
	$(PYTHON) scripts/ecosystem_mining.py
	@echo "📊 Résultats dans data/mining_results/"

## Dashboard temps réel
dashboard-start:
	@echo "📊 Démarrage dashboard MSR..."
	streamlit run dashboards/ecosystem_dashboard.py

## Validation anti-patterns
check-antipatterns:
	@echo "🚨 Vérification anti-patterns..."
	$(PYTHON) src/governance/ci_gatekeeper.py

## Tests complets
test:
	@echo "🧪 Exécution tests..."
	pytest tests/ -v --cov=src/

## Nettoyage
clean:
	rm -rf data/temp/ .pytest_cache/ __pycache__/

## Aide
help:
	@echo "DATA-MINER - Commandes disponibles:"
	@echo "  install         - Installation dépendances"
	@echo "  analyze-ecosystem - Analyse complète ECOSYSTEM-1"
	@echo "  dashboard-start - Dashboard temps réel"
	@echo "  check-antipatterns - Validation governance"
	@echo "  test           - Tests complets"
	@echo "  clean          - Nettoyage fichiers temporaires"