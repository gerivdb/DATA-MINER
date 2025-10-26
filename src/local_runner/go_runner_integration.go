// Package local_runner - Intégration Go Runner Self Hosted DevTools
// Alternative locale aux GitHub Actions pour DATA-MINER autonome
// Basé sur l'approche DevTools existante

package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/robfig/cron/v3"
)

// GoRunnerConfig - Configuration runner local DATA-MINER
type GoRunnerConfig struct {
	RunnerID       string `json:"runner_id"`
	WorkspacePath  string `json:"workspace_path"`
	LogPath        string `json:"log_path"`
	Schedule       string `json:"schedule"` // Cron format
	GitHubToken    string `json:"github_token"`
	EcosystemRepos []string `json:"ecosystem_repos"`
	ParallelJobs   int    `json:"parallel_jobs"`
}

// Job - Définition job mining local
type Job struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Command   string    `json:"command"`
	Args      []string  `json:"args"`
	Schedule  string    `json:"schedule"`
	Timeout   time.Duration `json:"timeout"`
	CreatedAt time.Time `json:"created_at"`
	Status    string    `json:"status"`
}

// LocalRunner - Runner local DATA-MINER échappant aux tokens payants
type LocalRunner struct {
	config *GoRunnerConfig
	cron   *cron.Cron
	jobs   map[string]*Job
	logger *log.Logger
}

// NewLocalRunner - Constructeur runner local
func NewLocalRunner(configPath string) (*LocalRunner, error) {
	config, err := loadConfig(configPath)
	if err != nil {
		return nil, fmt.Errorf("erreur chargement config: %w", err)
	}

	// Création répertoires si nécessaire
	os.MkdirAll(config.WorkspacePath, 0755)
	os.MkdirAll(config.LogPath, 0755)

	// Logger
	logFile, err := os.OpenFile(filepath.Join(config.LogPath, "runner.log"), 
		os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		return nil, fmt.Errorf("erreur création log: %w", err)
	}

	return &LocalRunner{
		config: config,
		cron:   cron.New(),
		jobs:   make(map[string]*Job),
		logger: log.New(logFile, "[DATA-MINER-RUNNER] ", log.LstdFlags),
	}, nil
}

// Start - Démarrage runner avec jobs prédéfinis DATA-MINER
func (r *LocalRunner) Start() error {
	r.logger.Printf("Démarrage Go Runner local DATA-MINER (ID: %s)", r.config.RunnerID)

	// Jobs DATA-MINER standards
	r.addDataMinerJobs()

	// Démarrage cron
	r.cron.Start()

	r.logger.Printf("Runner actif avec %d jobs planifiés", len(r.jobs))
	return nil
}

// addDataMinerJobs - Ajout jobs spécifiques DATA-MINER
func (r *LocalRunner) addDataMinerJobs() {
	// Job 1: Mining écosystème hebdomadaire
	ecosystemJob := &Job{
		ID:      "ecosystem-mining-weekly",
		Name:    "Mining ECOSYSTEM-1 hebdomadaire",
		Command: "python3",
		Args:    []string{"scripts/ecosystem_mining.py", "--comprehensive"},
		Schedule: "0 2 * * 1", // Lundi 2h du matin
		Timeout: 30 * time.Minute,
		Status:  "active",
	}
	r.addJob(ecosystemJob)

	// Job 2: Génération rapport governance quotidien
	governanceJob := &Job{
		ID:      "governance-report-daily",
		Name:    "Rapport governance quotidien",
		Command: "python3",
		Args:    []string{"src/governance/ci_gatekeeper.py", "--report"},
		Schedule: "0 8 * * *", // Tous les jours 8h
		Timeout: 10 * time.Minute,
		Status:  "active",
	}
	r.addJob(governanceJob)

	// Job 3: Nettoyage artefacts anciens
	cleanupJob := &Job{
		ID:      "cleanup-old-artifacts",
		Name:    "Nettoyage artefacts > 30 jours",
		Command: "powershell",
		Args:    []string{"-File", "scripts/cleanup-artifacts.ps1", "-Days", "30"},
		Schedule: "0 1 1 * *", // Premier du mois 1h
		Timeout: 15 * time.Minute,
		Status:  "active",
	}
	r.addJob(cleanupJob)

	// Job 4: Synchronisation avec DevTools Hub
	syncJob := &Job{
		ID:      "sync-devtools-hub",
		Name:    "Sync avec DevTools Hub",
		Command: "make",
		Args:    []string{"sync-devtools"},
		Schedule: "*/30 * * * *", // Toutes les 30 minutes
		Timeout: 5 * time.Minute,
		Status:  "active",
	}
	r.addJob(syncJob)
}

// addJob - Ajout job avec planification cron
func (r *LocalRunner) addJob(job *Job) {
	r.jobs[job.ID] = job
	
	// Planification cron si schedule défini
	if job.Schedule != "" {
		r.cron.AddFunc(job.Schedule, func() {
			r.executeJob(job)
		})
	}
}

// executeJob - Exécution job avec timeout et logging
func (r *LocalRunner) executeJob(job *Job) {
	r.logger.Printf("Démarrage job: %s (%s)", job.Name, job.ID)
	start := time.Now()

	// Context avec timeout
	ctx, cancel := context.WithTimeout(context.Background(), job.Timeout)
	defer cancel()

	// Préparation commande
	cmd := exec.CommandContext(ctx, job.Command, job.Args...)
	cmd.Dir = r.config.WorkspacePath

	// Variables environnement
	cmd.Env = append(os.Environ(), 
		fmt.Sprintf("GITHUB_TOKEN=%s", r.config.GitHubToken),
		fmt.Sprintf("DATA_MINER_RUNNER_ID=%s", r.config.RunnerID),
		fmt.Sprintf("DATA_MINER_WORKSPACE=%s", r.config.WorkspacePath),
	)

	// Exécution
	output, err := cmd.CombinedOutput()
	duration := time.Since(start)

	if err != nil {
		r.logger.Printf("ERREUR job %s: %v (durée: %v)", job.ID, err, duration)
		r.logger.Printf("Output: %s", string(output))
		job.Status = "failed"
	} else {
		r.logger.Printf("SUCCÈS job %s (durée: %v)", job.ID, duration)
		job.Status = "completed"
	}

	// Sauvegarde résultats
	r.saveJobResult(job, string(output), duration, err)
}

// saveJobResult - Sauvegarde résultats job pour dashboard
func (r *LocalRunner) saveJobResult(job *Job, output string, duration time.Duration, err error) {
	result := map[string]interface{}{
		"job_id":       job.ID,
		"job_name":     job.Name,
		"executed_at":  time.Now().Format(time.RFC3339),
		"duration_ms":  duration.Milliseconds(),
		"status":       job.Status,
		"output":       output,
		"error":        nil,
	}

	if err != nil {
		result["error"] = err.Error()
	}

	// Sauvegarde JSON horodaté
	timestamp := time.Now().Format("20060102_150405")
	resultFile := filepath.Join(r.config.LogPath, fmt.Sprintf("job_%s_%s.json", job.ID, timestamp))

	data, _ := json.MarshalIndent(result, "", "  ")
	os.WriteFile(resultFile, data, 0644)
}

// loadConfig - Chargement configuration depuis JSON
func loadConfig(configPath string) (*GoRunnerConfig, error) {
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}

	var config GoRunnerConfig
	err = json.Unmarshal(data, &config)
	return &config, err
}

// main - Point d'entrée runner local
func main() {
	configPath := "config/go_runner.json"
	if len(os.Args) > 1 {
		configPath = os.Args[1]
	}

	runner, err := NewLocalRunner(configPath)
	if err != nil {
		log.Fatalf("Erreur création runner: %v", err)
	}

	if err := runner.Start(); err != nil {
		log.Fatalf("Erreur démarrage runner: %v", err)
	}

	// Maintenir le runner actif
	select {}
}