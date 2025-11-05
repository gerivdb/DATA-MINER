#!/usr/bin/env python3
"""
DATA-MINER MSR Analysis Engine
Mining Software Repositories for ECOSYSTEM-1 Intelligence

Author: ECOSYSTEM-1 DEV COMET
Created: 2025-11-05
Master Issue: #2 - DATA-MINER Evolution
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path
import statistics
from collections import defaultdict, Counter
import re

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from textstat import flesch_reading_ease

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CommitPattern:
    """Commit pattern analysis result"""
    pattern_id: str
    repository: str
    commit_sha: str
    author: str
    timestamp: datetime
    message: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    pattern_type: str  # 'feature', 'bugfix', 'refactor', 'docs', 'test'
    complexity_score: float
    impact_score: float
    
@dataclass
class AntiPattern:
    """Anti-pattern detection result"""
    pattern_id: str
    pattern_name: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    affected_repositories: List[str]
    affected_files: List[str]
    description: str
    remediation_suggestion: str
    auto_fixable: bool
    detection_confidence: float
    first_detected: datetime = field(default_factory=datetime.now)
    occurrences: int = 1
    
@dataclass
class LearningInsight:
    """Extracted learning insight"""
    insight_id: str
    insight_type: str  # 'best_practice', 'success_pattern', 'failure_pattern'
    repositories: List[str]
    evidence: List[str]  # Supporting evidence (commits, files, metrics)
    confidence_score: float
    applicability_score: float  # How applicable to other repos
    insight_text: str
    actionable_steps: List[str]
    generated_at: datetime = field(default_factory=datetime.now)
    
@dataclass
class PlaybookEntry:
    """Generated playbook entry"""
    playbook_id: str
    title: str
    category: str  # 'architecture', 'process', 'quality', 'performance'
    description: str
    steps: List[Dict[str, Any]]
    prerequisites: List[str]
    success_criteria: List[str]
    related_patterns: List[str]
    effectiveness_rating: float
    last_updated: datetime = field(default_factory=datetime.now)

class MSRAnalysisEngine:
    """
    Mining Software Repositories Analysis Engine
    
    Capabilities:
    - Cross-repository pattern analysis
    - Anti-pattern detection with remediation
    - Learning insights extraction
    - Automated playbook generation
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.analysis_cache: Dict[str, Any] = {}
        self.commit_patterns: List[CommitPattern] = []
        self.anti_patterns: List[AntiPattern] = []
        self.learning_insights: List[LearningInsight] = []
        self.generated_playbooks: List[PlaybookEntry] = []
        
        # Analysis models
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.commit_classifier = None  # Would be trained ML model
        
        # Repository exclusion patterns
        self.exclusion_patterns = config.get('exclusion_patterns', ['geri-cms-*'])
        
        # Critical repositories for priority analysis
        self.critical_repos = config.get('critical_repos', [
            'DevTools', 'FLUENCE', 'WAZAA', 'ECOS-CLI', 'BRAIN'
        ])
        
    async def start_msr_analysis(self):
        """Start comprehensive MSR analysis"""
        logger.info("Starting MSR Analysis Engine for ECOSYSTEM-1")
        
        # Initialize analysis pipeline
        await self.initialize_analysis_pipeline()
        
        # Start analysis tasks
        tasks = [
            asyncio.create_task(self.analyze_commit_patterns()),
            asyncio.create_task(self.detect_anti_patterns()),
            asyncio.create_task(self.extract_learning_insights()),
            asyncio.create_task(self.generate_playbooks()),
            asyncio.create_task(self.update_analytics_dashboard())
        ]
        
        logger.info("MSR Analysis Engine started")
        await asyncio.gather(*tasks)
        
    async def initialize_analysis_pipeline(self):
        """Initialize the analysis pipeline"""
        # Load historical data if available
        await self.load_analysis_cache()
        
        # Initialize ML models
        await self.initialize_ml_models()
        
        # Setup repository graph for dependency analysis
        self.repo_graph = await self.build_repository_graph()
        
        logger.info("Analysis pipeline initialized")
        
    async def load_analysis_cache(self):
        """Load cached analysis results"""
        cache_path = Path(self.config.get('cache_path', './data/msr_cache.json'))
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    self.analysis_cache = json.load(f)
                logger.info(f"Loaded analysis cache: {len(self.analysis_cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                
    async def initialize_ml_models(self):
        """Initialize machine learning models for pattern detection"""
        # Placeholder for ML model initialization
        # In production, this would load pre-trained models
        logger.info("ML models initialized (placeholder)")
        
    async def build_repository_graph(self) -> nx.DiGraph:
        """Build dependency graph of repositories"""
        graph = nx.DiGraph()
        
        # Add nodes for all repositories
        repo_list = await self.get_repository_list()
        for repo in repo_list:
            graph.add_node(repo, category=self.get_repo_category(repo))
            
        # Add edges for dependencies (simplified implementation)
        dependencies = {
            'WAZAA': ['ECOS-CLI', 'DATA-MINER', 'comet-devcomet-extension'],
            'ECOS-CLI': ['WAZAA'],
            'DevTools': ['FLUENCE', 'WAZAA'],
            'FLUENCE': ['DevTools', 'BRAIN'],
            'vsix-ai-orchestrator': ['vscode-lm-proxy']
        }
        
        for repo, deps in dependencies.items():
            for dep in deps:
                if graph.has_node(dep):
                    graph.add_edge(repo, dep, relationship='depends_on')
                    
        logger.info(f"Repository graph built: {len(graph.nodes())} nodes, {len(graph.edges())} edges")
        return graph
        
    async def get_repository_list(self) -> List[str]:
        """Get list of repositories to analyze"""
        # In production, this would fetch from GitHub API
        return [
            'WAZAA', 'ECOS-CLI', 'DATA-MINER', 'DOC-UNIV-DEV',
            'DevTools', 'FLUENCE', 'BRAIN', 'vsix-ai-orchestrator',
            'comet-devcomet-extension', 'GeriCode', 'vscode-lm-proxy'
        ]
        
    def get_repo_category(self, repo: str) -> str:
        """Get repository category for graph analysis"""
        categories = {
            'structural': ['WAZAA', 'ECOS-CLI', 'DATA-MINER', 'DOC-UNIV-DEV'],
            'core': ['DevTools', 'FLUENCE', 'BRAIN'],
            'extension': ['comet-devcomet-extension', 'vsix-ai-orchestrator', 'GeriCode']
        }
        
        for category, repos in categories.items():
            if repo in repos:
                return category
        return 'other'
        
    async def analyze_commit_patterns(self):
        """Analyze commit patterns across repositories"""
        while True:
            try:
                logger.info("Starting commit pattern analysis")
                
                # Analyze each repository
                for repo in await self.get_repository_list():
                    if self.should_exclude_repo(repo):
                        continue
                        
                    await self.analyze_repository_commits(repo)
                    
                # Cross-repository pattern analysis
                await self.analyze_cross_repo_patterns()
                
                # Update pattern database
                await self.store_commit_patterns()
                
                await asyncio.sleep(self.config.get('commit_analysis_interval', 3600))
                
            except Exception as e:
                logger.error(f"Commit pattern analysis error: {e}")
                await asyncio.sleep(7200)
                
    def should_exclude_repo(self, repo: str) -> bool:
        """Check if repository should be excluded from analysis"""
        for pattern in self.exclusion_patterns:
            if pattern.replace('*', '') in repo.lower():
                return True
        return False
        
    async def analyze_repository_commits(self, repo: str):
        """Analyze commit patterns for specific repository"""
        try:
            # Get recent commits (placeholder - would use GitHub MCP)
            commits = await self.get_repository_commits(repo, days=30)
            
            for commit in commits:
                pattern = await self.classify_commit_pattern(repo, commit)
                if pattern:
                    self.commit_patterns.append(pattern)
                    
            logger.debug(f"Analyzed {len(commits)} commits for {repo}")
            
        except Exception as e:
            logger.error(f"Repository commit analysis error for {repo}: {e}")
            
    async def get_repository_commits(self, repo: str, days: int = 30) -> List[Dict]:
        """Get recent commits for repository (placeholder)"""
        # Mock commit data - in production would use GitHub MCP
        mock_commits = {
            'DevTools': [
                {
                    'sha': 'abc123',
                    'author': 'gerivdb',
                    'message': 'fix: PowerShell automation failing on Windows 11',
                    'timestamp': datetime.now() - timedelta(hours=6),
                    'files': ['src/automation.ps1', 'tests/automation_test.ps1'],
                    'additions': 25,
                    'deletions': 8
                },
                {
                    'sha': 'def456',
                    'author': 'gerivdb', 
                    'message': 'feat: add Windows 11 compatibility layer',
                    'timestamp': datetime.now() - timedelta(hours=12),
                    'files': ['src/windows11.ps1', 'docs/windows11.md'],
                    'additions': 145,
                    'deletions': 0
                }
            ],
            'FLUENCE': [
                {
                    'sha': 'ghi789',
                    'author': 'gerivdb',
                    'message': 'feat: implement cognitive decision matrix',
                    'timestamp': datetime.now() - timedelta(hours=18),
                    'files': ['src/cognitive/matrix.go', 'internal/decision.go'],
                    'additions': 89,
                    'deletions': 12
                }
            ]
        }
        
        return mock_commits.get(repo, [])
        
    async def classify_commit_pattern(self, repo: str, commit: Dict) -> Optional[CommitPattern]:
        """Classify commit pattern using message analysis"""
        message = commit['message'].lower()
        
        # Pattern classification logic
        pattern_type = 'other'
        if message.startswith('feat'):
            pattern_type = 'feature'
        elif message.startswith('fix'):
            pattern_type = 'bugfix'
        elif message.startswith('refactor'):
            pattern_type = 'refactor'
        elif message.startswith('docs'):
            pattern_type = 'documentation'
        elif message.startswith('test'):
            pattern_type = 'test'
            
        # Calculate complexity score
        complexity = self.calculate_commit_complexity(commit)
        
        # Calculate impact score
        impact = self.calculate_commit_impact(commit, repo)
        
        return CommitPattern(
            pattern_id=f"{repo}_{commit['sha'][:8]}",
            repository=repo,
            commit_sha=commit['sha'],
            author=commit['author'],
            timestamp=commit['timestamp'],
            message=commit['message'],
            files_changed=commit.get('files', []),
            lines_added=commit.get('additions', 0),
            lines_deleted=commit.get('deletions', 0),
            pattern_type=pattern_type,
            complexity_score=complexity,
            impact_score=impact
        )
        
    def calculate_commit_complexity(self, commit: Dict) -> float:
        """Calculate complexity score for commit"""
        # Simple complexity heuristic
        files_count = len(commit.get('files', []))
        lines_changed = commit.get('additions', 0) + commit.get('deletions', 0)
        
        # Normalize to 0-100 scale
        complexity = (files_count * 10) + (lines_changed / 10)
        return min(complexity, 100.0)
        
    def calculate_commit_impact(self, commit: Dict, repo: str) -> float:
        """Calculate impact score for commit"""
        # Impact based on repository importance and change scope
        repo_weight = 100.0 if repo in self.critical_repos else 50.0
        
        # File type impact
        files = commit.get('files', [])
        critical_files = sum(1 for f in files if any(ext in f for ext in ['.py', '.go', '.ps1', '.json']))
        
        impact = (repo_weight * 0.3) + (critical_files * 10) + (len(files) * 5)
        return min(impact, 100.0)
        
    async def analyze_cross_repo_patterns(self):
        """Analyze patterns across repositories"""
        if len(self.commit_patterns) < 10:
            return
            
        logger.info("Analyzing cross-repository patterns")
        
        # Group patterns by type
        patterns_by_type = defaultdict(list)
        for pattern in self.commit_patterns:
            patterns_by_type[pattern.pattern_type].append(pattern)
            
        # Analyze each pattern type
        for pattern_type, patterns in patterns_by_type.items():
            await self.analyze_pattern_type_trends(pattern_type, patterns)
            
        # Identify cross-repo correlations
        await self.identify_cross_repo_correlations()
        
    async def analyze_pattern_type_trends(self, pattern_type: str, patterns: List[CommitPattern]):
        """Analyze trends for specific pattern type"""
        if len(patterns) < 3:
            return
            
        # Temporal analysis
        patterns_by_repo = defaultdict(list)
        for pattern in patterns:
            patterns_by_repo[pattern.repository].append(pattern)
            
        # Calculate metrics per repository
        for repo, repo_patterns in patterns_by_repo.items():
            avg_complexity = statistics.mean(p.complexity_score for p in repo_patterns)
            avg_impact = statistics.mean(p.impact_score for p in repo_patterns)
            frequency = len(repo_patterns)
            
            logger.debug(f"{repo} {pattern_type} patterns: {frequency} commits, "
                        f"avg complexity: {avg_complexity:.1f}, avg impact: {avg_impact:.1f}")
                        
    async def identify_cross_repo_correlations(self):
        """Identify correlations between repositories"""
        # Group commits by time windows to find correlated activity
        time_windows = defaultdict(list)
        
        for pattern in self.commit_patterns:
            # Group by 4-hour windows
            window = pattern.timestamp.replace(minute=0, second=0) 
            window_key = window - timedelta(hours=window.hour % 4)
            time_windows[window_key].append(pattern)
            
        # Find windows with high cross-repo activity
        high_activity_windows = []
        for window, patterns in time_windows.items():
            repo_count = len(set(p.repository for p in patterns))
            if repo_count >= 3:  # Activity in 3+ repos simultaneously
                high_activity_windows.append((window, patterns))
                
        logger.info(f"Identified {len(high_activity_windows)} high cross-repo activity periods")
        
        # Analyze correlations
        for window, patterns in high_activity_windows:
            correlation_insight = await self.analyze_activity_correlation(window, patterns)
            if correlation_insight:
                self.learning_insights.append(correlation_insight)
                
    async def analyze_activity_correlation(self, window: datetime, 
                                          patterns: List[CommitPattern]) -> Optional[LearningInsight]:
        """Analyze correlation in activity patterns"""
        repo_activity = defaultdict(list)
        for pattern in patterns:
            repo_activity[pattern.repository].append(pattern)
            
        # Check if activity suggests coordinated development
        common_themes = self.extract_common_themes([p.message for p in patterns])
        
        if len(common_themes) >= 2:  # At least 2 common themes
            return LearningInsight(
                insight_id=f"correlation_{window.strftime('%Y%m%d_%H%M%S')}",
                insight_type='success_pattern',
                repositories=list(repo_activity.keys()),
                evidence=[p.message for p in patterns[:5]],  # Sample evidence
                confidence_score=0.7,
                applicability_score=0.8,
                insight_text=f"Coordinated development activity detected: {', '.join(common_themes)}",
                actionable_steps=[
                    "Consider formalizing coordinated development process",
                    "Create shared development timeline",
                    "Establish cross-repo code review process"
                ]
            )
            
        return None
        
    def extract_common_themes(self, messages: List[str]) -> List[str]:
        """Extract common themes from commit messages"""
        # Simple keyword extraction
        all_words = []
        for message in messages:
            # Clean and tokenize
            words = re.findall(r'\b\w+\b', message.lower())
            all_words.extend(words)
            
        # Count word frequency
        word_counts = Counter(all_words)
        
        # Filter common themes (appearing in multiple messages)
        themes = []
        for word, count in word_counts.items():
            if count >= 2 and len(word) > 3:  # Minimum frequency and length
                themes.append(word)
                
        return themes[:10]  # Top 10 themes
        
    async def detect_anti_patterns(self):
        """Detect anti-patterns across repositories"""
        while True:
            try:
                logger.info("Starting anti-pattern detection")
                
                # Architectural anti-patterns
                arch_patterns = await self.detect_architectural_anti_patterns()
                
                # Development anti-patterns  
                dev_patterns = await self.detect_development_anti_patterns()
                
                # Process anti-patterns
                process_patterns = await self.detect_process_anti_patterns()
                
                # Store detected anti-patterns
                all_patterns = arch_patterns + dev_patterns + process_patterns
                self.anti_patterns.extend(all_patterns)
                
                logger.info(f"Detected {len(all_patterns)} anti-patterns")
                
                await asyncio.sleep(self.config.get('anti_pattern_detection_interval', 7200))
                
            except Exception as e:
                logger.error(f"Anti-pattern detection error: {e}")
                await asyncio.sleep(14400)
                
    async def detect_architectural_anti_patterns(self) -> List[AntiPattern]:
        """Detect architectural anti-patterns"""
        patterns = []
        
        # God Object detection (simplified)
        for repo in await self.get_repository_list():
            if self.should_exclude_repo(repo):
                continue
                
            # Mock analysis - would analyze actual code
            large_files = await self.find_large_files(repo)
            
            for file_info in large_files:
                if file_info['lines'] > 1000:  # Threshold for God Object
                    patterns.append(AntiPattern(
                        pattern_id=f"god_object_{repo}_{file_info['name']}",
                        pattern_name="God Object",
                        severity="medium" if file_info['lines'] < 2000 else "high",
                        affected_repositories=[repo],
                        affected_files=[file_info['path']],
                        description=f"Large file detected: {file_info['lines']} lines in {file_info['name']}",
                        remediation_suggestion="Consider breaking into smaller, focused modules",
                        auto_fixable=False,
                        detection_confidence=0.8
                    ))
                    
        return patterns
        
    async def find_large_files(self, repo: str) -> List[Dict]:
        """Find large files in repository (mock implementation)"""
        # Mock data - would analyze actual repository files
        mock_large_files = {
            'WAZAA': [
                {'name': 'orchestrator.py', 'path': 'src/orchestrator.py', 'lines': 1200},
                {'name': 'main.py', 'path': 'src/main.py', 'lines': 850}
            ],
            'DevTools': [
                {'name': 'automation.ps1', 'path': 'src/automation.ps1', 'lines': 1500}
            ]
        }
        
        return mock_large_files.get(repo, [])
        
    async def detect_development_anti_patterns(self) -> List[AntiPattern]:
        """Detect development anti-patterns"""
        patterns = []
        
        # Dead code detection
        for repo in await self.get_repository_list():
            dead_code_files = await self.find_dead_code(repo)
            
            for file_path in dead_code_files:
                patterns.append(AntiPattern(
                    pattern_id=f"dead_code_{repo}_{hash(file_path)}",
                    pattern_name="Dead Code",
                    severity="low",
                    affected_repositories=[repo],
                    affected_files=[file_path],
                    description=f"Potentially unused code detected in {file_path}",
                    remediation_suggestion="Review and remove if confirmed unused",
                    auto_fixable=True,
                    detection_confidence=0.6
                ))
                
        # Duplicate code detection across repositories
        duplicate_patterns = await self.detect_cross_repo_duplicates()
        patterns.extend(duplicate_patterns)
        
        return patterns
        
    async def find_dead_code(self, repo: str) -> List[str]:
        """Find potentially dead code in repository"""
        # Placeholder implementation
        return []  # Would implement actual dead code detection
        
    async def detect_cross_repo_duplicates(self) -> List[AntiPattern]:
        """Detect duplicate code across repositories"""
        patterns = []
        
        # Simplified duplicate detection
        # Would implement proper code similarity analysis
        
        return patterns
        
    async def detect_process_anti_patterns(self) -> List[AntiPattern]:
        """Detect process-related anti-patterns"""
        patterns = []
        
        # Long-lived branch detection
        for repo in await self.get_repository_list():
            long_branches = await self.find_long_lived_branches(repo)
            
            for branch_info in long_branches:
                patterns.append(AntiPattern(
                    pattern_id=f"long_branch_{repo}_{branch_info['name']}",
                    pattern_name="Long-Lived Feature Branch",
                    severity="medium",
                    affected_repositories=[repo],
                    affected_files=[],
                    description=f"Branch '{branch_info['name']}' active for {branch_info['days']} days",
                    remediation_suggestion="Consider merging or breaking into smaller changes",
                    auto_fixable=False,
                    detection_confidence=0.9
                ))
                
        return patterns
        
    async def find_long_lived_branches(self, repo: str) -> List[Dict]:
        """Find long-lived branches in repository"""
        # Mock implementation
        return []  # Would implement actual branch analysis
        
    async def store_commit_patterns(self):
        """Store commit patterns for future analysis"""
        # Store in cache for persistence
        patterns_data = {
            'commit_patterns': [asdict(p) for p in self.commit_patterns[-100:]],  # Keep last 100
            'last_updated': datetime.now().isoformat()
        }
        
        cache_path = Path(self.config.get('patterns_cache_path', './data/commit_patterns.json'))
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(patterns_data, f, default=str, indent=2)
            
    async def extract_learning_insights(self):
        """Extract actionable learning insights"""
        while True:
            try:
                logger.info("Extracting learning insights")
                
                # Analyze successful patterns
                success_insights = await self.analyze_successful_patterns()
                
                # Analyze failure patterns
                failure_insights = await self.analyze_failure_patterns()
                
                # Generate improvement recommendations
                improvement_insights = await self.generate_improvement_recommendations()
                
                # Store insights
                all_insights = success_insights + failure_insights + improvement_insights
                self.learning_insights.extend(all_insights)
                
                logger.info(f"Extracted {len(all_insights)} learning insights")
                
                await asyncio.sleep(self.config.get('insight_extraction_interval', 3600))
                
            except Exception as e:
                logger.error(f"Learning insight extraction error: {e}")
                await asyncio.sleep(7200)
                
    async def analyze_successful_patterns(self) -> List[LearningInsight]:
        """Analyze successful development patterns"""
        insights = []
        
        # Find patterns with high success (low subsequent fixes)
        feature_patterns = [p for p in self.commit_patterns if p.pattern_type == 'feature']
        
        for pattern in feature_patterns:
            # Check if feature required many subsequent fixes
            subsequent_fixes = await self.count_subsequent_fixes(pattern)
            
            if subsequent_fixes == 0:  # Successful feature
                insight = LearningInsight(
                    insight_id=f"success_{pattern.pattern_id}",
                    insight_type='best_practice',
                    repositories=[pattern.repository],
                    evidence=[pattern.message],
                    confidence_score=0.8,
                    applicability_score=0.7,
                    insight_text=f"Successful feature implementation pattern in {pattern.repository}",
                    actionable_steps=[
                        f"Follow similar approach for {pattern.repository} features",
                        "Document this implementation pattern",
                        "Consider reusing architecture in other repos"
                    ]
                )
                insights.append(insight)
                
        return insights[:10]  # Limit insights
        
    async def count_subsequent_fixes(self, pattern: CommitPattern) -> int:
        """Count fixes that followed a feature (simplified)"""
        # Simplified implementation - would analyze actual commit history
        return 0  # Placeholder
        
    async def analyze_failure_patterns(self) -> List[LearningInsight]:
        """Analyze failure patterns to extract lessons"""
        insights = []
        
        # Find bugfix patterns with high complexity
        bugfix_patterns = [p for p in self.commit_patterns if p.pattern_type == 'bugfix']
        high_complexity_fixes = [p for p in bugfix_patterns if p.complexity_score > 70]
        
        for pattern in high_complexity_fixes:
            insight = LearningInsight(
                insight_id=f"failure_{pattern.pattern_id}",
                insight_type='failure_pattern',
                repositories=[pattern.repository],
                evidence=[pattern.message],
                confidence_score=0.7,
                applicability_score=0.8,
                insight_text=f"Complex bugfix pattern indicates potential architectural issue",
                actionable_steps=[
                    "Review root cause of complex fixes",
                    "Consider refactoring affected areas",
                    "Implement additional testing"
                ]
            )
            insights.append(insight)
            
        return insights[:5]  # Limit failure insights
        
    async def generate_improvement_recommendations(self) -> List[LearningInsight]:
        """Generate improvement recommendations based on analysis"""
        insights = []
        
        # Analyze commit frequency and suggest process improvements
        repo_commit_freq = defaultdict(int)
        for pattern in self.commit_patterns:
            repo_commit_freq[pattern.repository] += 1
            
        for repo, freq in repo_commit_freq.items():
            if freq < 5:  # Low activity
                insight = LearningInsight(
                    insight_id=f"improvement_{repo}_activity",
                    insight_type='best_practice',
                    repositories=[repo],
                    evidence=[f"Only {freq} commits in analysis period"],
                    confidence_score=0.6,
                    applicability_score=0.5,
                    insight_text=f"Low development activity in {repo} - consider review",
                    actionable_steps=[
                        f"Review {repo} roadmap and priorities",
                        "Consider consolidating with other repositories",
                        "Evaluate if repository is still needed"
                    ]
                )
                insights.append(insight)
                
        return insights
        
    async def generate_playbooks(self):
        """Generate automated playbooks from insights"""
        while True:
            try:
                logger.info("Generating playbooks from learning insights")
                
                # Group insights by category
                insights_by_category = defaultdict(list)
                for insight in self.learning_insights:
                    category = self.categorize_insight(insight)
                    insights_by_category[category].append(insight)
                    
                # Generate playbooks for each category
                for category, insights in insights_by_category.items():
                    if len(insights) >= 3:  # Minimum insights for playbook
                        playbook = await self.create_playbook_from_insights(category, insights)
                        self.generated_playbooks.append(playbook)
                        
                logger.info(f"Generated {len(self.generated_playbooks)} playbooks")
                
                await asyncio.sleep(self.config.get('playbook_generation_interval', 7200))
                
            except Exception as e:
                logger.error(f"Playbook generation error: {e}")
                await asyncio.sleep(14400)
                
    def categorize_insight(self, insight: LearningInsight) -> str:
        """Categorize insight for playbook generation"""
        if 'architecture' in insight.insight_text.lower():
            return 'architecture'
        elif 'process' in insight.insight_text.lower() or 'workflow' in insight.insight_text.lower():
            return 'process'
        elif 'quality' in insight.insight_text.lower() or 'test' in insight.insight_text.lower():
            return 'quality'
        elif 'performance' in insight.insight_text.lower():
            return 'performance'
        else:
            return 'general'
            
    async def create_playbook_from_insights(self, category: str, 
                                           insights: List[LearningInsight]) -> PlaybookEntry:
        """Create playbook from grouped insights"""
        # Aggregate actionable steps
        all_steps = []
        for insight in insights:
            all_steps.extend(insight.actionable_steps)
            
        # Remove duplicates and structure
        unique_steps = list(set(all_steps))
        
        # Create structured steps
        structured_steps = []
        for i, step in enumerate(unique_steps[:10]):  # Limit to 10 steps
            structured_steps.append({
                'step_number': i + 1,
                'description': step,
                'type': 'action',
                'estimated_effort': 'medium',
                'prerequisites': []
            })
            
        # Calculate effectiveness rating
        avg_confidence = statistics.mean(i.confidence_score for i in insights)
        avg_applicability = statistics.mean(i.applicability_score for i in insights)
        effectiveness = (avg_confidence + avg_applicability) / 2
        
        return PlaybookEntry(
            playbook_id=f"playbook_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"{category.title()} Best Practices for ECOSYSTEM-1",
            category=category,
            description=f"Automated playbook generated from {len(insights)} learning insights",
            steps=structured_steps,
            prerequisites=["Access to ECOSYSTEM-1 repositories", "Understanding of project structure"],
            success_criteria=["Improved code quality metrics", "Reduced anti-pattern occurrences"],
            related_patterns=[i.insight_id for i in insights],
            effectiveness_rating=effectiveness
        )
        
    async def update_analytics_dashboard(self):
        """Update analytics dashboard data"""
        while True:
            try:
                dashboard_data = await self.generate_analytics_dashboard()
                
                # Store dashboard data
                dashboard_path = Path(self.config.get('dashboard_path', './data/analytics_dashboard.json'))
                dashboard_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(dashboard_path, 'w') as f:
                    json.dump(dashboard_data, f, default=str, indent=2)
                    
                logger.info("Analytics dashboard updated")
                
                await asyncio.sleep(self.config.get('dashboard_update_interval', 300))
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                await asyncio.sleep(600)
                
    async def generate_analytics_dashboard(self) -> Dict:
        """Generate analytics dashboard data"""
        current_time = datetime.now()
        
        # Pattern analysis summary
        pattern_stats = defaultdict(int)
        for pattern in self.commit_patterns:
            pattern_stats[pattern.pattern_type] += 1
            
        # Anti-pattern summary
        anti_pattern_stats = defaultdict(int)
        for ap in self.anti_patterns:
            anti_pattern_stats[ap.severity] += 1
            
        # Learning insights summary
        insight_stats = defaultdict(int)
        for insight in self.learning_insights:
            insight_stats[insight.insight_type] += 1
            
        return {
            'timestamp': current_time.isoformat(),
            'analysis_summary': {
                'total_commit_patterns': len(self.commit_patterns),
                'pattern_distribution': dict(pattern_stats),
                'anti_patterns_detected': len(self.anti_patterns),
                'anti_pattern_severity': dict(anti_pattern_stats),
                'learning_insights': len(self.learning_insights),
                'insight_distribution': dict(insight_stats),
                'playbooks_generated': len(self.generated_playbooks)
            },
            'repository_health': await self.calculate_repository_health_scores(),
            'recommendations': await self.get_top_recommendations(),
            'trends': await self.calculate_trend_analysis()
        }
        
    async def calculate_repository_health_scores(self) -> Dict[str, float]:
        """Calculate health scores for each repository"""
        health_scores = {}
        
        for repo in await self.get_repository_list():
            # Calculate based on anti-patterns, commit activity, etc.
            repo_anti_patterns = [ap for ap in self.anti_patterns if repo in ap.affected_repositories]
            
            base_score = 100.0
            
            # Penalties for anti-patterns
            for ap in repo_anti_patterns:
                if ap.severity == 'critical':
                    base_score -= 20
                elif ap.severity == 'high':
                    base_score -= 10
                elif ap.severity == 'medium':
                    base_score -= 5
                elif ap.severity == 'low':
                    base_score -= 2
                    
            health_scores[repo] = max(base_score, 0.0)
            
        return health_scores
        
    async def get_top_recommendations(self) -> List[Dict]:
        """Get top recommendations for ecosystem improvement"""
        recommendations = []
        
        # From anti-patterns
        critical_anti_patterns = [ap for ap in self.anti_patterns if ap.severity in ['critical', 'high']]
        for ap in critical_anti_patterns[:5]:  # Top 5
            recommendations.append({
                'type': 'anti_pattern_remediation',
                'priority': 'high' if ap.severity == 'critical' else 'medium',
                'description': ap.remediation_suggestion,
                'affected_repos': ap.affected_repositories
            })
            
        # From learning insights
        high_impact_insights = [i for i in self.learning_insights if i.applicability_score > 0.7]
        for insight in high_impact_insights[:3]:  # Top 3
            recommendations.append({
                'type': 'improvement_opportunity',
                'priority': 'medium',
                'description': insight.insight_text,
                'actionable_steps': insight.actionable_steps[:2]
            })
            
        return recommendations
        
    async def calculate_trend_analysis(self) -> Dict:
        """Calculate trend analysis for dashboard"""
        # Analyze trends over time
        trends = {
            'commit_activity': await self.analyze_commit_trends(),
            'quality_trends': await self.analyze_quality_trends(),
            'complexity_trends': await self.analyze_complexity_trends()
        }
        
        return trends
        
    async def analyze_commit_trends(self) -> Dict:
        """Analyze commit activity trends"""
        # Group commits by day
        daily_commits = defaultdict(int)
        for pattern in self.commit_patterns:
            day_key = pattern.timestamp.date().isoformat()
            daily_commits[day_key] += 1
            
        # Calculate trend direction
        recent_days = sorted(daily_commits.keys())[-7:]  # Last 7 days
        if len(recent_days) >= 2:
            trend_direction = 'increasing' if daily_commits[recent_days[-1]] > daily_commits[recent_days[0]] else 'decreasing'
        else:
            trend_direction = 'stable'
            
        return {
            'daily_commits': dict(daily_commits),
            'trend_direction': trend_direction,
            'avg_daily_commits': statistics.mean(daily_commits.values()) if daily_commits else 0
        }
        
    async def analyze_quality_trends(self) -> Dict:
        """Analyze code quality trends"""
        # Simplified quality analysis based on anti-patterns over time
        return {
            'anti_pattern_trend': 'improving',  # Placeholder
            'quality_score_avg': 85.2
        }
        
    async def analyze_complexity_trends(self) -> Dict:
        """Analyze code complexity trends"""
        # Analyze complexity scores over time
        complexity_scores = [p.complexity_score for p in self.commit_patterns]
        
        return {
            'avg_complexity': statistics.mean(complexity_scores) if complexity_scores else 0,
            'complexity_trend': 'stable',  # Would calculate actual trend
            'high_complexity_commits': len([s for s in complexity_scores if s > 80])
        }

# Configuration and initialization
class MSRConfig:
    """Configuration for MSR Analysis Engine"""
    
    @staticmethod
    def get_production_config() -> Dict:
        return {
            'cache_path': './data/msr_cache.json',
            'patterns_cache_path': './data/commit_patterns.json',
            'dashboard_path': './data/analytics_dashboard.json',
            'commit_analysis_interval': 3600,      # 1 hour
            'anti_pattern_detection_interval': 7200,  # 2 hours
            'insight_extraction_interval': 3600,    # 1 hour
            'playbook_generation_interval': 7200,   # 2 hours
            'dashboard_update_interval': 300,       # 5 minutes
            'exclusion_patterns': ['geri-cms-*'],
            'critical_repos': ['DevTools', 'FLUENCE', 'WAZAA', 'ECOS-CLI', 'BRAIN'],
            'max_patterns_in_memory': 1000,
            'enable_ml_analysis': False,  # Disabled until models trained
            'analysis_lookback_days': 30
        }

# Main execution
async def main():
    """Test MSR analysis engine"""
    config = MSRConfig.get_production_config()
    engine = MSRAnalysisEngine(config)
    
    logger.info("DATA-MINER MSR Analysis Engine - Starting Analysis")
    
    try:
        await engine.start_msr_analysis()
    except KeyboardInterrupt:
        logger.info("MSR Analysis Engine stopped")
    except Exception as e:
        logger.error(f"MSR Analysis Engine error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
