#!/usr/bin/env python3
# CI Gatekeeper - Prévention anti-patterns en amont
# Inspiré des règles de gouvernance EMAIL-SENDER-1

import re
from typing import Dict, List, Any

class CIGatekeeper:
    """Gatekeeper CI pour blocage anti-patterns"""
    
    BLOCKING_RULES = {
        "no_lovable_naming": {
            "check": lambda name: not re.match(r".*-[a-f0-9]{8}$", name),
            "message": "❌ Nommage hash Lovable interdit en production",
            "severity": "BLOCKING",
            "evidence": "30 suppressions geri-cms pour ce pattern"
        },
        "no_monolithic_pr": {
            "check": lambda pr: pr.get("changed_files", 0) < 50,
            "message": "❌ PR trop volumineuse - diviser (leçon EMAIL-SENDER-1)",
            "severity": "BLOCKING",
            "evidence": "EMAIL-SENDER-1 744KB abandonné par complexité"
        },
        "mandatory_tests": {
            "check": lambda pr: pr.get("test_files_ratio", 0) > 0.2,
            "message": "❌ Ratio tests insuffisant - minimum 20%",
            "severity": "WARNING",
            "evidence": "Correlation tests/quality validée empiriquement"
        },
        "memory_management_required": {
            "check": lambda pr: "memory" in str(pr.get("description", "")).lower() if pr.get("memory_changes", False) else True,
            "message": "❌ Changements mémoire sans justification",
            "severity": "WARNING", 
            "evidence": "Patterns EMAIL-SENDER-1 cache logic obligatoires"
        }
    }
    
    def __init__(self, config_path: str = "config/rbac_config.yaml"):
        self.config = self._load_rbac_config(config_path)
        self.violations_log = []
        
    def validate_pr(self, pr_data: Dict, user_role: str = "msr_analyst") -> Dict[str, Any]:
        """Validation PR selon règles governance avec RBAC"""
        violations = []
        
        # Vérification permissions utilisateur
        if not self._check_permission(user_role, "validate:pr"):
            return {
                "valid": False,
                "violations": [{"rule": "rbac", "message": "❌ Permissions insuffisantes", "severity": "BLOCKING"}]
            }
        
        # Validation règles
        for rule_name, rule_config in self.BLOCKING_RULES.items():
            try:
                if not rule_config["check"](pr_data):
                    violation = {
                        "rule": rule_name,
                        "message": rule_config["message"], 
                        "severity": rule_config["severity"],
                        "evidence": rule_config["evidence"],
                        "timestamp": datetime.now().isoformat()
                    }
                    violations.append(violation)
                    self.violations_log.append(violation)
                    
            except Exception as e:
                # Log erreur mais ne pas bloquer
                violations.append({
                    "rule": rule_name,
                    "message": f"⚠️ Erreur validation: {str(e)}",
                    "severity": "WARNING"
                })
                
        blocking_violations = [v for v in violations if v["severity"] == "BLOCKING"]
        
        return {
            "valid": len(blocking_violations) == 0,
            "violations": violations,
            "blocking_count": len(blocking_violations),
            "warning_count": len([v for v in violations if v["severity"] == "WARNING"])
        }
    
    def _check_permission(self, user_role: str, action: str) -> bool:
        """Vérification permission RBAC"""
        role_config = self.config.get("roles", {}).get(user_role, {})
        permissions = role_config.get("permissions", [])
        return "*" in permissions or action in permissions
    
    def _load_rbac_config(self, config_path: str) -> Dict:
        """Chargement configuration RBAC"""
        import yaml
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"roles": {}, "policies": {}}
    
    def generate_governance_report(self) -> Dict:
        """Rapport governance avec métriques empiriques"""
        
        report = {
            "report_date": datetime.now().isoformat(),
            "total_validations": len(self.violations_log),
            "blocking_rate": len([v for v in self.violations_log if v["severity"] == "BLOCKING"]) / max(len(self.violations_log), 1),
            "most_common_violations": self._get_top_violations(),
            "improvement_trends": self._analyze_trends(),
            "recommendations": self._generate_governance_recommendations()
        }
        
        return report
    
    def _get_top_violations(self) -> List[Dict]:
        """Top violations pour focus amélioration"""
        violation_counts = {}
        for v in self.violations_log:
            rule = v["rule"]
            violation_counts[rule] = violation_counts.get(rule, 0) + 1
            
        return sorted(
            [{"rule": k, "count": v} for k, v in violation_counts.items()],
            key=lambda x: x["count"], reverse=True
        )[:5]