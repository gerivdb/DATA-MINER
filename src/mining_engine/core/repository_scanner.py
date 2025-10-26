#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de scan des dépôts ECOSYSTEM-1 pour extraction métadonnées MSR
Basé sur GitHub API + analyse statique + patterns EMAIL-SENDER-1
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path

class EcosystemRepositoryScanner:
    """Scanner MSR pour dépôts ECOSYSTEM-1"""
    
    def __init__(self, config_path: str = "config/ecosystem.json"):
        self.config = self._load_config(config_path)
        self.github_token = self.config["github"]["token"]
        self.ecosystem_repos = self.config["ecosystem"]["repositories"]
        
    def _load_config(self, config_path: str) -> Dict:
        """Chargement configuration écosystème"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    async def scan_all_repositories(self) -> Dict[str, Any]:
        """Scan complet de tous les dépôts ECOSYSTEM-1"""
        
        results = {
            "scan_timestamp": datetime.now().isoformat(),
            "ecosystem_count": len(self.ecosystem_repos),
            "repositories": {},
            "cross_repo_analysis": {},
            "patterns_detected": {},
            "recommendations": []
        }
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._analyze_repository(session, repo) 
                for repo in self.ecosystem_repos
            ]
            
            repo_analyses = await asyncio.gather(*tasks)
            
            for analysis in repo_analyses:
                if analysis and "name" in analysis:
                    results["repositories"][analysis["name"]] = analysis
                    
        # Analyse croisée post-traitement
        results["cross_repo_analysis"] = await self._cross_repository_analysis(results["repositories"])
        results["patterns_detected"] = self._detect_ecosystem_patterns(results["repositories"])
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    async def _analyze_repository(self, session: aiohttp.ClientSession, repo_name: str) -> Dict[str, Any]:
        """Analyse approfondie d'un dépôt individuel"""
        
        try:
            # Métadonnées GitHub
            repo_data = await self._fetch_github_metadata(session, repo_name)
            
            # Analyse des commits (derniers 100)  
            commits_analysis = await self._analyze_commits(session, repo_name)
            
            # Analyse des issues/PR
            issues_analysis = await self._analyze_issues_prs(session, repo_name)
            
            # Détection patterns Lovable
            lovable_patterns = self._detect_lovable_patterns(repo_name, repo_data)
            
            # Analyse statique structure
            structure_analysis = await self._analyze_repository_structure(session, repo_name)
            
            return {
                "name": repo_name,
                "metadata": repo_data,
                "commits_analysis": commits_analysis,
                "issues_analysis": issues_analysis, 
                "lovable_patterns": lovable_patterns,
                "structure": structure_analysis,
                "mining_score": self._calculate_mining_score(repo_data, commits_analysis, issues_analysis),
                "recommendations": self._generate_repo_recommendations(repo_name, repo_data)
            }
            
        except Exception as e:
            return {"name": repo_name, "error": str(e), "mining_score": 0}
            
    async def _fetch_github_metadata(self, session: aiohttp.ClientSession, repo_name: str) -> Dict:
        """Récupération métadonnées GitHub via API"""
        headers = {"Authorization": f"token {self.github_token}"}
        url = f"https://api.github.com/repos/gerivdb/{repo_name}"
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"GitHub API error: {response.status}"}
    
    def _detect_lovable_patterns(self, repo_name: str, repo_data: Dict) -> Dict:
        """Détection patterns Lovable dans métadonnées"""
        import re
        
        patterns = {
            "is_lovable_clone": False,
            "pattern_type": None,
            "confidence": 0.0
        }
        
        # Patterns Lovable identifiés
        if re.search(r"-[a-f0-9]{8}$", repo_name):
            patterns.update({"is_lovable_clone": True, "pattern_type": "hash_suffix", "confidence": 0.95})
        elif re.search(r"-\d{2}-\d{2}-\d{2}-\d{2}$", repo_name):
            patterns.update({"is_lovable_clone": True, "pattern_type": "timestamp", "confidence": 0.90})
            
        return patterns
    
    def _calculate_mining_score(self, metadata: Dict, commits: Dict, issues: Dict) -> float:
        """Score mining basé sur métriques MSR"""
        score = 0.0
        
        # Activité récente
        if commits.get("recent_activity", 0) > 10:
            score += 3.0
            
        # Qualité structure
        if metadata.get("size", 0) > 1000:
            score += 2.0
            
        # Community engagement
        if metadata.get("stargazers_count", 0) > 0:
            score += 1.0
            
        return min(score, 10.0)
    
    async def _cross_repository_analysis(self, repositories: Dict) -> Dict:
        """Analyse croisée entre dépôts ECOSYSTEM-1"""
        return {
            "dependency_graph": {},
            "common_patterns": {},
            "cross_contamination_risk": {}
        }
    
    def _detect_ecosystem_patterns(self, repositories: Dict) -> Dict:
        """Détection patterns transversaux écosystème"""
        return {
            "naming_conventions": {},
            "architecture_patterns": {},
            "technology_clusters": {}
        }
    
    def _generate_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Génération recommendations basées sur MSR analysis"""
        return [
            {
                "type": "governance",
                "priority": "HIGH",
                "title": "Implémenter CI gates anti-patterns",
                "description": "Prévenir réintroduction patterns Lovable"
            }
        ]