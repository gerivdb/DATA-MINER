# Architecture Go Runner Local - Alternative GitHub Actions

## 🎯 PROBLÉMATIQUE RÉSOLUE

**Problème** : GitHub Actions devient payant au-delà des quotas gratuits
**Solution** : Go Runner self-hosted local utilisant votre PC comme infrastructure
**Avantage** : Contrôle total, coût nul, intégration DevTools Hub native

## 🏗️ ARCHITECTURE TECHNIQUE

```ascii
┌──────────────────── LOCAL RUNNER ECOSYSTEM ─────────────────────┐
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   DATA-MINER    │    │   GO RUNNER     │    │   DEVTOOLS   │ │
│  │     JOBS        │◄──►│  SELF HOSTED    │◄──►│     HUB      │ │
│  │                 │    │                 │    │              │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                        │                      │      │
│           ▼                        ▼                      ▼      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ Ecosystem Mining│    │  Cron Scheduler │    │   Sync Hub   │ │
│  │ Governance Rep  │    │  Job Queue      │    │  Templates   │ │
│  │ Dashboard Update│    │  Log Manager    │    │  Scripts     │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│                                                                  │
│                    💻 LOCAL PC (pas de cloud)                   │
└──────────────────────────────────────────────────────────────────┘
```

## 🔧 STACK RUNNER LOCAL

### **Go Runner Core**
- **Langage** : Go (performance, concurrence native)
- **Scheduler** : robfig/cron/v3 (planification flexible)
- **Jobs** : Queue FIFO avec timeout et retry
- **Logs** : JSON structurés + rotation automatique
- **API** : HTTP simple pour trigger manuel/dashboard

### **PowerShell Runner Alternatif**
- **Plateforme** : Windows Task Scheduler integration
- **Jobs** : Hashtable PowerShell avec validation
- **Monitoring** : EventLog Windows + fichiers JSON
- **Backup** : Exécution immédiate si scheduler fail

### **Alternatives Disponibles**
1. **ACT** (nektos/act) : GitHub Actions workflows locaux
2. **Drone.io** : Self-hosted avec Docker compose
3. **Jenkins** : Local lightweight container
4. **Cron + Make** : Solution UNIX minimaliste

## 🚀 AVANTAGES vs GITHUB ACTIONS

| Critère | GitHub Actions | Go Runner Local | Avantage |
|---------|----------------|-----------------|----------|
| **Coût** | Payant après quotas | Gratuit total | 💰 **100% économie** |
| **Contrôle** | Limité environment | Total contrôle | 🎛️ **Personnalisation** |
| **Performance** | Variable cloud | Dédié local | ⚡ **Performance garantie** |
| **Sécurité** | GitHub infra | PC local isolé | 🔒 **Contrôle données** |
| **Integration** | GitHub only | DevTools Hub | 🔗 **Écosystème natif** |
| **Debugging** | Cloud logs | Logs locaux | 🐛 **Debug immédiat** |

## 📋 JOBS DATA-MINER INTÉGRÉS

### **1. ecosystem-mining-weekly**
- **Fréquence** : Lundi 2h (hebdomadaire)
- **Durée** : ~30 minutes
- **Action** : `python scripts/ecosystem_mining.py --comprehensive`
- **Output** : `data/mining_results/ecosystem_analysis_YYYYMMDD.json`

### **2. governance-report-daily**  
- **Fréquence** : Quotidien 8h
- **Durée** : ~10 minutes
- **Action** : `python src/governance/ci_gatekeeper.py --report`
- **Output** : `data/governance/daily_report_YYYYMMDD.json`

### **3. dashboard-update-hourly**
- **Fréquence** : Toutes les 2h
- **Durée** : ~5 minutes
- **Action** : `python dashboards/ecosystem_dashboard.py --update-data`
- **Output** : Données dashboard rafraîchies

### **4. sync-devtools-frequent**
- **Fréquence** : 30 minutes
- **Durée** : ~2 minutes
- **Action** : `make sync-devtools`
- **Output** : Synchronisation scripts/templates DevTools

## 🛠️ INSTALLATION & USAGE

### **Installation**
```bash
# Clone DATA-MINER
git clone https://github.com/gerivdb/DATA-MINER.git
cd DATA-MINER

# Installation avec runner local
make install

# Configuration
cp config/go_runner.json.template config/go_runner.json
# Éditer token GitHub et paramètres
```

### **Démarrage Runner**
```bash
# Go Runner (Linux/macOS/Windows)
make local-runner-start

# PowerShell Runner (Windows optimisé)
make local-runner-ps1

# Status verification
make local-runner-status
```

### **Alternatives Installation**
```bash
# Menu interactif alternatives
make install-alternatives

# Ou directement:
./scripts/local_alternatives.sh 1  # ACT
./scripts/local_alternatives.sh 2  # Drone.io  
./scripts/local_alternatives.sh 3  # Jenkins
./scripts/local_alternatives.sh 4  # Cron+Make
```

## 🔄 INTÉGRATION DEVTOOLS ECOSYSTEM

### **DevTools Hub → DATA-MINER**
- Scripts PowerShell partagés
- Templates governance réutilisés
- Branch management synchronisé
- MCP GitHub configurations

### **ECOYSTEM → DATA-MINER**
- Orchestration planning
- Métriques agrégées
- Coordination releases
- Health monitoring

### **DATA-MINER → Satellites**
- Mining cross-repos ECOSYSTEM-1
- Anti-patterns detection
- Playbooks distribution
- Quality gates enforcement

## 📊 MONITORING & OBSERVABILITÉ

### **Logs Structurés**
```json
{
  "timestamp": "2025-10-26T20:30:00Z",
  "runner_id": "data-miner-local-01",
  "job_id": "ecosystem-mining-weekly",
  "status": "completed",
  "duration_ms": 1847320,
  "output_files": ["data/mining_results/ecosystem_analysis_20251026.json"]
}
```

### **Métriques Performance**
- **Job Success Rate** : %succès/échec par job
- **Execution Time** : Trends durée exécution  
- **Resource Usage** : CPU/RAM/Disk local
- **Data Production** : Volume artefacts générés

## 🚧 LIMITATIONS & SOLUTIONS

### **Limitations Identifiées**
- **Disponibilité PC** : Runner arrêté si PC éteint
- **Parallélisme** : Limité aux cores locaux
- **Réseau** : Dépendant connexion Internet
- **Backup** : Artefacts uniquement locaux

### **Solutions Implémentées**
- **Wake-on-LAN** : Réveil automatique PC pour jobs critiques
- **Job Queue** : Exécution différée si ressources limitées
- **Retry Logic** : Nouvelle tentative automatique en cas d'échec réseau
- **Cloud Sync** : Upload artefacts optionnel vers storage externe

## 🎯 PROCHAINES ÉVOLUTIONS

1. **API REST** : Interface Web pour management jobs
2. **Clustering** : Coordination multi-PC si besoin
3. **Webhooks** : Triggers GitHub events → runner local
4. **Mobile Dashboard** : Monitoring mobile via app
5. **Backup Cloud** : Sync artefacts cloud avec chiffrement

---
*Architecture validée par experience EMAIL-SENDER-1 infrastructure locale*