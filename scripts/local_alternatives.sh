#!/bin/bash
# scripts/local_alternatives.sh
# Alternatives locales complètes aux GitHub Actions pour DATA-MINER
# Solutions self-hosted inspirées de la stack EMAIL-SENDER-1

set -euo pipefail

# Configuration
DATA_MINER_HOME="$(pwd)"
LOGS_DIR="$DATA_MINER_HOME/logs/alternatives"
WORKSPACE_DIR="$DATA_MINER_HOME/workspace"
CONFIG_FILE="$DATA_MINER_HOME/config/alternatives.json"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$LOGS_DIR/alternatives.log"
}

log_error() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${RED}[ERROR]${NC} $1" | tee -a "$LOGS_DIR/alternatives.log"
}

log_success() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOGS_DIR/alternatives.log"
}

# Préparation environnement
setup_environment() {
    log "🏗️ Préparation environnement DATA-MINER local..."
    
    mkdir -p "$LOGS_DIR" "$WORKSPACE_DIR"
    
    # Vérification outils requis
    local tools=("git" "python3" "make" "docker")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Outil manquant: $tool"
            exit 1
        fi
    done
    
    log_success "Environnement préparé"
}

# Alternative 1: ACT - GitHub Actions local (nektos/act)
setup_act_runner() {
    log "🎭 Installation ACT - GitHub Actions local..."
    
    # Installation ACT si pas présent
    if ! command -v act &> /dev/null; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install act
        else
            log_error "OS non supporté pour ACT"
            return 1
        fi
    fi
    
    # Test ACT avec workflow DATA-MINER
    if [ -f ".github/workflows/data-miner.yml" ]; then
        log "Test exécution workflow local via ACT..."
        act -n  # Dry run
        log_success "ACT configuré - workflows GitHub Actions exécutables localement"
    else
        log "Création workflow exemple pour ACT..."
        mkdir -p ".github/workflows"
        cat > ".github/workflows/data-miner.yml" << EOF
name: DATA-MINER Local Pipeline
on: [push, workflow_dispatch]

jobs:
  mining:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run ecosystem mining
      run: python scripts/ecosystem_mining.py --local
EOF
        log_success "Workflow ACT créé - testable avec: act"
    fi
}

# Alternative 2: Drone.io self-hosted
setup_drone_runner() {
    log "🚁 Configuration Drone.io self-hosted..."
    
    # Vérification Docker
    if ! docker --version &> /dev/null; then
        log_error "Docker requis pour Drone.io"
        return 1
    fi
    
    # Configuration Drone server local
    cat > "docker-compose.drone.yml" << EOF
version: '3.8'

services:
  drone-server:
    image: drone/drone:2
    container_name: data-miner-drone
    ports:
      - "3000:80"
    environment:
      - DRONE_GITHUB_CLIENT_ID=\${DRONE_GITHUB_CLIENT_ID}
      - DRONE_GITHUB_CLIENT_SECRET=\${DRONE_GITHUB_CLIENT_SECRET}
      - DRONE_RPC_SECRET=data-miner-secret
      - DRONE_SERVER_HOST=localhost:3000
      - DRONE_SERVER_PROTO=http
    volumes:
      - ./data/drone:/data
    restart: unless-stopped
      
  drone-runner:
    image: drone/drone-runner-docker:1
    container_name: data-miner-drone-runner
    environment:
      - DRONE_RPC_PROTO=http
      - DRONE_RPC_HOST=drone-server
      - DRONE_RPC_SECRET=data-miner-secret
      - DRONE_RUNNER_CAPACITY=2
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      - drone-server
    restart: unless-stopped
EOF
    
    # Pipeline Drone pour DATA-MINER
    cat > ".drone.yml" << EOF
kind: pipeline
type: docker
name: data-miner-msr

steps:
- name: ecosystem-mining
  image: python:3.10
  commands:
  - pip install -r requirements.txt
  - python scripts/ecosystem_mining.py
  
- name: governance-report  
  image: python:3.10
  commands:
  - python src/governance/ci_gatekeeper.py --report
  
- name: dashboard-update
  image: python:3.10
  commands:
  - python dashboards/ecosystem_dashboard.py --update-data

trigger:
  event:
  - push
  - cron
  cron:
  - daily-mining
EOF
    
    log_success "Drone.io configuré - docker-compose up -f docker-compose.drone.yml"
}

# Alternative 3: Jenkins local lightweight
setup_jenkins_local() {
    log "🏗️ Configuration Jenkins local léger..."
    
    # Jenkins via Docker
    cat > "docker-compose.jenkins.yml" << EOF
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: data-miner-jenkins
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    environment:
      - JENKINS_OPTS=--httpPort=8080
    volumes:
      - ./data/jenkins:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - \$PWD:\$PWD
    restart: unless-stopped
EOF
    
    # Pipeline Jenkins pour DATA-MINER
    mkdir -p "jenkins-pipelines"
    cat > "jenkins-pipelines/Jenkinsfile.data-miner" << EOF
pipeline {
    agent any
    
    triggers {
        cron('H 2 * * 1')  // Lundi 2h (mining hebdomadaire)
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }
        
        stage('Ecosystem Mining') {
            steps {
                sh 'python3 scripts/ecosystem_mining.py --comprehensive'
            }
            post {
                always {
                    archiveArtifacts 'data/mining_results/*.json'
                }
            }
        }
        
        stage('Governance Report') {
            steps {
                sh 'python3 src/governance/ci_gatekeeper.py --report'
            }
        }
        
        stage('Dashboard Update') {
            steps {
                sh 'python3 dashboards/ecosystem_dashboard.py --update-data'
            }
        }
    }
    
    post {
        always {
            echo 'DATA-MINER pipeline terminé'
        }
        failure {
            echo 'Pipeline échoué - vérifier logs'
        }
    }
}
EOF
    
    log_success "Jenkins configuré - docker-compose up -f docker-compose.jenkins.yml"
}

# Alternative 4: Cron simple + Make
setup_cron_make() {
    log "⏰ Configuration Cron + Make simple..."
    
    # Scripts wrapper pour cron
    cat > "scripts/cron_wrapper.sh" << 'EOF'
#!/bin/bash
# Wrapper cron pour DATA-MINER

cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

log_file="logs/cron-$(date +%Y%m%d).log"
echo "$(date): Démarrage $1" >> "$log_file"

case "$1" in
    "ecosystem-mining")
        make analyze-ecosystem >> "$log_file" 2>&1
        ;;
    "governance-report")
        make check-antipatterns >> "$log_file" 2>&1
        ;;
    "dashboard-update")
        make dashboard-update >> "$log_file" 2>&1
        ;;
    *)
        echo "Job inconnu: $1" >> "$log_file"
        exit 1
        ;;
esac

echo "$(date): Terminé $1 (code: $?)" >> "$log_file"
EOF
    
    chmod +x "scripts/cron_wrapper.sh"
    
    # Génération crontab
    cat > "config/crontab.data-miner" << EOF
# DATA-MINER Cron Jobs - Alternative locale GitHub Actions
# Éditer avec: crontab config/crontab.data-miner

# Mining ECOSYSTEM-1 hebdomadaire (Lundi 2h)
0 2 * * 1 $DATA_MINER_HOME/scripts/cron_wrapper.sh ecosystem-mining

# Rapport governance quotidien (8h)
0 8 * * * $DATA_MINER_HOME/scripts/cron_wrapper.sh governance-report

# Dashboard update (toutes les 2h)
0 */2 * * * $DATA_MINER_HOME/scripts/cron_wrapper.sh dashboard-update
EOF
    
    log "Installation crontab: crontab config/crontab.data-miner"
    log_success "Cron + Make configuré - alternative la plus légère"
}

# Menu principal
show_menu() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║        DATA-MINER LOCAL RUNNER         ║"
    echo "║    Alternatives GitHub Actions         ║"
    echo "╠════════════════════════════════════════╣"
    echo "║ 1. ACT - GitHub Actions local          ║"
    echo "║ 2. Drone.io - Self-hosted léger       ║"
    echo "║ 3. Jenkins - Local lightweight        ║"
    echo "║ 4. Cron + Make - Minimaliste          ║"
    echo "║ 5. Status - Vérifier runner actuel    ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Point d'entrée principal
main() {
    setup_environment
    
    if [ $# -eq 0 ]; then
        show_menu
        echo -n "Choisir alternative (1-5): "
        read -r choice
    else
        choice=$1
    fi
    
    case $choice in
        1) setup_act_runner ;;
        2) setup_drone_runner ;;
        3) setup_jenkins_local ;;
        4) setup_cron_make ;;
        5) 
            log "Status runner local..."
            echo -e "${GREEN}📊 DATA-MINER Local Status:${NC}"
            echo "Workspace: $WORKSPACE_DIR"
            echo "Logs: $LOGS_DIR"
            if pgrep -f "data-miner" > /dev/null; then
                echo -e "${GREEN}✅ Runner actif${NC}"
            else
                echo -e "${YELLOW}⏸️ Runner inactif${NC}"
            fi
            ;;
        *) 
            log_error "Choix invalide: $choice"
            show_menu
            ;;
    esac
}

# Exécution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi