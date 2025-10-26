# Branch Management DATA-MINER

Inspiré de DevTools (le plus avancé de l'écosystème)

## STRUCTURE
```
main
├── dev 
│   ├── feature/msr-engine
│   ├── feature/analysis-platform
│   ├── feature/governance-system
│   └── hotfix/critical-bugs
└── production (tags releases)
```

## WORKFLOW
1. **Feature** : `dev` → `feature/nom-descriptif` → PR vers `dev`
2. **Release** : `dev` → `main` → tag version
3. **Hotfix** : `main` → `hotfix/fix` → PR vers `main` + `dev`
4. **JAMAIS** direct sur main/dev

## VALIDATION PR
- Tests passing obligatoire
- MSR rules compliance  
- Anti-patterns check
- Playbook conformity