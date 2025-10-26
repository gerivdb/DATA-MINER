# Playbook: Durcissement Clone Lovable → Produit Durable

## 🎯 OBJECTIF
Transformer un clone Lovable temporaire en dépôt de production robuste selon 
l'expérience empirique des 30 suppressions et leçons EMAIL-SENDER-1.

## 📋 CHECKLIST 7 ÉTAPES CRITIQUES

### ✅ **ÉTAPE 1 : NOMMAGE STABLE**
- [ ] Éliminer suffixes hash/timestamp  
- [ ] Adopter nommage sémantique métier
- [ ] Vérifier unicité écosystème
- **Critère acceptation** : Nom ne match aucun pattern Lovable
- **Evidence** : 30 dépôts supprimés avaient patterns hash/timestamp

### ✅ **ÉTAPE 2 : CONSOLIDATION MODULES**
- [ ] Identifier duplications cross-files
- [ ] Factoriser composants réutilisables  
- [ ] Éliminer dead code
- **Critère acceptation** : DRY score > 80%
- **Evidence** : Duplications identifiées cause principale complexité

### ✅ **ÉTAPE 3 : TESTS & CI/CD**
- [ ] Test coverage > 70%
- [ ] Pipeline CI/CD fonctionnel
- [ ] Intégration continue validée
- **Critère acceptation** : Tests passent, deploy automatique
- **Evidence** : EMAIL-SENDER-1 avait testing exhaustif efficace

### ✅ **ÉTAPE 4 : DÉCOUPLAGE ARCHITECTURE**
- [ ] Réduire co-changements > seuil
- [ ] Séparer concerns métier/technique
- [ ] APIs contract-first
- **Critère acceptation** : Coupling score < 0.5
- **Evidence** : Couplage fort = cause abandon EMAIL-SENDER-1

### ✅ **ÉTAPE 5 : MEMORY & PERFORMANCE**
- [ ] Patterns gestion mémoire EMAIL-SENDER-1
- [ ] Monitoring performance baseline
- [ ] Optimisation hotspots identifiés  
- **Critère acceptation** : Performance stable, pas de fuites
- **Evidence** : Cache logic simulation + Mem0 analysis validés

### ✅ **ÉTAPE 6 : DOCUMENTATION VIVANTE**
- [ ] README complet avec examples
- [ ] API documentation générée
- [ ] Architecture decision records
- **Critère acceptation** : Onboarding < 30min
- **Evidence** : EMAIL-SENDER-1 avait doc autogénérée 91KB

### ✅ **ÉTAPE 7 : GOUVERNANCE INTÉGRÉE**
- [ ] Règles RBAC configurées
- [ ] CI gates anti-patterns actifs  
- [ ] Playbook compliance validée
- **Critère acceptation** : 0 violation governance
- **Evidence** : Governance EMAIL-SENDER-1 (.govpolicy/) fonctionnelle

## 🔧 TEMPLATES GÉNÉRÉS

Chaque étape génère des templates réutilisables pour accélérer 
les futurs durcissements selon cette méthodologie éprouvée.

## 📊 MÉTRIQUES SUCCÈS

- **Avant durcissement** : Clone Lovable temporaire
- **Après durcissement** : Dépôt production-ready
- **Critères validation** : 7/7 étapes passées
- **Evidence empirique** : Basé sur 30 cas réels analysés

## 🚀 EXÉCUTION

```bash
# Validation playbook
make validate-hardening REPO=nom-repo

# Application automatisée
make apply-hardening REPO=nom-repo

# Vérification post-traitement
make verify-hardening REPO=nom-repo
```