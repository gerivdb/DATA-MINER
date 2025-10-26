#!/usr/bin/env python3  
# Détecteur d'anti-patterns basé sur l'expérience Lovable + EMAIL-SENDER-1

import re
from datetime import datetime
from typing import Dict, List, Any

class AntiPatternDetector:
    """Détection d'anti-patterns spécifiques à l'écosystème GERIVDB"""
    
    LOVABLE_ANTIPATTERNS = {
        "hash_suffix_naming": {
            "pattern": r"-[a-f0-9]{8}$",
            "severity": "HIGH", 
            "remedy": "Adopter nommage sémantique stable",
            "evidence": "30 dépôts geri-cms supprimés avec ce pattern"
        },
        "timestamp_proliferation": {
            "pattern": r"-\\d{2}-\\d{2}-\\d{2}-\\d{2}$",
            "severity": "HIGH",
            "remedy": "Utiliser versioning sémantique",
            "evidence": "8 dépôts timestamp détectés lors nettoyage"
        },
        "monolithic_growth": {
            "pattern": "single_repo_>500MB", 
            "severity": "CRITICAL",
            "remedy": "Modularisation via microservices (leçon EMAIL-SENDER-1)",
            "evidence": "EMAIL-SENDER-1 abandonné à 744KB par surcharge"
        },
        "memory_leak_accumulation": {
            "pattern": "memory_growth_>10MB_per_week",
            "severity": "MEDIUM",
            "remedy": "Patterns gestion mémoire EMAIL-SENDER-1",
            "evidence": "Cache logic simulation + Mem0 analysis réussis"
        }
    }
    
    def __init__(self):
        self.detection_history = []
        
    def detect_all_antipatterns(self, repo_data: Dict) -> List[Dict]:
        """Détection complète anti-patterns avec evidence empirique"""
        detected = []
        
        for pattern_name, config in self.LOVABLE_ANTIPATTERNS.items():
            if self._matches_pattern(repo_data, config["pattern"]):
                detection = {
                    "pattern": pattern_name,
                    "severity": config["severity"], 
                    "remedy": config["remedy"],
                    "evidence": config["evidence"],
                    "detection_timestamp": datetime.now().isoformat(),
                    "affected_repo": repo_data.get("name", "unknown"),
                    "confidence": self._calculate_confidence(repo_data, config)
                }
                
                detected.append(detection)
                self.detection_history.append(detection)
                
        return detected
    
    def _matches_pattern(self, repo_data: Dict, pattern: str) -> bool:
        """Vérification pattern matching avec evidence"""
        repo_name = repo_data.get("name", "")
        
        if pattern.startswith("r"):
            # Pattern regex
            pattern_clean = pattern.split("r")[1].strip('"')
            return bool(re.search(pattern_clean, repo_name))
        elif "single_repo_>500MB" in pattern:
            # Pattern taille (leçon EMAIL-SENDER-1)
            size_kb = repo_data.get("size", 0)
            return size_kb > 500000  # 500MB en KB
        elif "memory_growth" in pattern:
            # Pattern mémoire (à implémenter avec historique)
            return False  # Nécessite données temporelles
            
        return False
    
    def _calculate_confidence(self, repo_data: Dict, config: Dict) -> float:
        """Calcul confiance détection basé sur evidence empirique"""
        base_confidence = 0.8
        
        # Bonus si evidence historique forte
        if "30 dépôts" in config["evidence"]:
            base_confidence += 0.15
        elif "EMAIL-SENDER-1" in config["evidence"]:
            base_confidence += 0.1
            
        return min(base_confidence, 1.0)
    
    def generate_remedy_plan(self, detected_patterns: List[Dict]) -> Dict:
        """Plan de remédiation basé sur patterns détectés"""
        
        remedy_plan = {
            "generated_at": datetime.now().isoformat(),
            "total_patterns": len(detected_patterns),
            "critical_count": len([p for p in detected_patterns if p["severity"] == "CRITICAL"]),
            "remediation_steps": [],
            "estimated_effort": self._estimate_remediation_effort(detected_patterns)
        }
        
        # Priorisation par severity
        for pattern in sorted(detected_patterns, key=lambda x: 
                            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}[x["severity"]]):
            
            remedy_plan["remediation_steps"].append({
                "priority": pattern["severity"],
                "action": pattern["remedy"],
                "evidence": pattern["evidence"],
                "target_repo": pattern["affected_repo"]
            })
            
        return remedy_plan
    
    def _estimate_remediation_effort(self, patterns: List[Dict]) -> str:
        """Estimation effort remédiation basée sur experience"""
        critical_count = len([p for p in patterns if p["severity"] == "CRITICAL"])
        high_count = len([p for p in patterns if p["severity"] == "HIGH"])
        
        if critical_count > 0:
            return "2-4 semaines (refactoring majeur)"
        elif high_count > 5:
            return "1-2 semaines (nettoyage intensif)"
        else:
            return "2-5 jours (ajustements)"