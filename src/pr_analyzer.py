"""
PR Risk Analyzer - Automated risk assessment for pull requests

This module integrates git metrics extraction with the ML model
to automatically predict risk for code changes.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.predictor import RiskPredictor
from src.git_monitor import GitRiskAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PRRiskAnalyzer:
    """Analyze pull requests for defect risk"""

    # Experience mapping: years of experience -> category
    EXPERIENCE_MAPPING = {
        'Senior': 'Senior',
        'Mid': 'Mid',
        'Junior': 'Junior',
        'Lead': 'Senior',
        'Intern': 'Junior'
    }

    def __init__(self, model_path: str, repo_path: str):
        """Initialize with trained model and repository"""
        logger.info(f"Initializing PR Risk Analyzer")
        logger.info(f"  Model: {model_path}")
        logger.info(f"  Repo: {repo_path}")

        try:
            self.predictor = RiskPredictor(model_path)
            self.git_analyzer = GitRiskAnalyzer(repo_path)
            self.repo_path = repo_path
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def analyze_branch(self, branch: str = 'feature',
                      base_branch: str = 'main',
                      module: str = None) -> Dict:
        """
        Analyze a branch/PR for risk

        Args:
            branch: Feature branch name
            base_branch: Base branch to compare against
            module: Module being changed (optional)

        Returns:
            Risk analysis with score, level, and recommendations
        """

        logger.info(f"Analyzing {branch} against {base_branch}")

        # Extract metrics from git
        try:
            git_metrics = self.git_analyzer.analyze_branch_changes(branch, base_branch)
        except Exception as e:
            logger.error(f"Failed to extract git metrics: {e}")
            return {'error': str(e)}

        if 'error' in git_metrics:
            return git_metrics

        # Build features for prediction
        features = self._build_features(git_metrics, module)

        # Get prediction
        try:
            risk_score, risk_level, probs = self.predictor.predict(features)
        except Exception as e:
            logger.error(f"Failed to predict risk: {e}")
            return {'error': str(e)}

        return {
            'branch': branch,
            'base_branch': base_branch,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'probabilities': probs,
            'metrics': git_metrics,
            'features_used': features,
            'timestamp': datetime.now().isoformat(),
            'recommendation': self._get_recommendation(risk_level, git_metrics)
        }

    def _build_features(self, git_metrics: Dict,
                       module: str = None) -> Dict:
        """
        Build feature vector for prediction model

        Maps extracted git metrics to model input features
        """

        # Required features (defaults)
        features = {
            'module': module or 'Unknown',
            'files_changed': git_metrics['files_changed'],
            'lines_added': git_metrics.get('lines_added', 0),
            'lines_deleted': 0,  # Would need to extract from git
            'complexity_score': min(git_metrics.get('complexity_score', 2), 10),
            'developer_experience': self._estimate_developer_experience(
                git_metrics.get('num_contributors', 1)
            ),
            'team_size': git_metrics.get('num_contributors', 1),
            'past_defect_rate': 0.10,  # Would query from historical data
            'test_coverage': 0.70,  # Would query from CI/test reports
            'automation_coverage': 0.65,  # Would query from CI
            'regression_failures': 0,  # Would query from CI
            'story_points': self._estimate_story_points(
                git_metrics['files_changed'],
                git_metrics.get('lines_added', 0)
            ),
            'dependencies': self._count_dependencies(git_metrics),
            'days_to_release': 7  # Would query from release schedule
        }

        logger.info(f"Built features: {json.dumps({k: v for k, v in features.items() if k != 'module'}, indent=2)}")

        return features

    def _estimate_developer_experience(self, num_contributors: int) -> str:
        """
        Estimate developer experience based on team size
        (In production, this would query a database)
        """
        if num_contributors == 1:
            return 'Senior'  # Solo contributors often senior
        elif num_contributors <= 2:
            return 'Mid'
        else:
            return 'Junior'  # Larger teams more likely to have junior devs

    def _estimate_story_points(self, files_changed: int,
                              lines_added: int) -> int:
        """
        Estimate story points based on change size
        (In production, query from JIRA)
        """
        if files_changed <= 3 and lines_added <= 100:
            return 2
        elif files_changed <= 8 and lines_added <= 300:
            return 5
        elif files_changed <= 15 and lines_added <= 700:
            return 8
        else:
            return 13

    def _count_dependencies(self, git_metrics: Dict) -> int:
        """
        Count external dependencies changed
        (In production, analyze imports and requirements changes)
        """
        changed_files = git_metrics.get('files_modified', [])

        # Check for dependency files
        dep_count = 0
        for file in changed_files:
            if any(name in file for name in [
                'requirements.txt', 'package.json', 'pom.xml',
                'Gemfile', 'go.mod', 'Cargo.toml', 'build.gradle'
            ]):
                dep_count += 1

        return min(dep_count, 3)  # Cap at 3 for calculation

    def _get_recommendation(self, risk_level: str,
                           git_metrics: Dict) -> Dict:
        """Generate testing recommendations based on risk"""

        recommendations = {
            'Low': {
                'testing_level': 'Quick sanity check',
                'test_suites': ['Smoke tests'],
                'manual_testing': False,
                'requires_review': False,
                'deployment': 'Direct to production',
                'time_estimate': '15-30 minutes'
            },
            'Medium': {
                'testing_level': 'Standard regression testing',
                'test_suites': ['Module regression', 'Integration tests'],
                'manual_testing': True,
                'requires_review': True,
                'deployment': 'Standard deployment',
                'time_estimate': '1-2 hours'
            },
            'High': {
                'testing_level': 'Full QA cycle with extended testing',
                'test_suites': [
                    'Full regression suite',
                    'Integration tests',
                    'Performance tests',
                    'Security tests'
                ],
                'manual_testing': True,
                'requires_review': True,
                'requires_security_review': True,
                'deployment': 'Canary deployment (5% → 25% → 50% → 100%)',
                'time_estimate': '2-3 days',
                'on_call_coverage': True
            }
        }

        base_recommendation = recommendations.get(risk_level, {})

        # Add module-specific recommendations
        if git_metrics['files_changed'] > 10:
            base_recommendation['additional_focus'] = [
                'Large change scope - verify no regression',
                'Multiple teams may be affected'
            ]

        return base_recommendation

    def generate_pr_comment(self, analysis: Dict) -> str:
        """Generate GitHub PR comment with risk analysis"""

        risk_level = analysis['risk_level']
        risk_score = analysis['risk_score']
        metrics = analysis['metrics']
        recommendation = analysis['recommendation']

        # Emoji mapping
        emoji = {
            'Low': '🟢',
            'Medium': '🟠',
            'High': '🔴'
        }

        comment = f"""
## {emoji[risk_level]} Risk Prediction: {risk_score:.0f}% ({risk_level})

### 📊 Code Metrics
- **Files Changed**: {metrics['files_changed']}
- **Lines Added**: {metrics.get('lines_added', 'N/A')}
- **Complexity Score**: {metrics.get('complexity_score', 'N/A'):.1f}
- **Contributors**: {metrics['num_contributors']}
- **Commits**: {metrics['num_commits']}

### 📋 Testing Recommendation
- **Level**: {recommendation['testing_level']}
- **Test Suites**: {', '.join(recommendation['test_suites'])}
- **Manual Testing**: {'✓ Required' if recommendation['manual_testing'] else '✗ Not required'}
- **Code Review**: {'✓ Required' if recommendation['requires_review'] else '✗ Not required'}
- **Deployment**: {recommendation['deployment']}
- **Time Estimate**: {recommendation['time_estimate']}

"""

        if 'on_call_coverage' in recommendation and recommendation['on_call_coverage']:
            comment += "⚠️ **On-call engineer coverage recommended during deployment**\n\n"

        if 'requires_security_review' in recommendation and recommendation['requires_security_review']:
            comment += "🔒 **Security review required before deployment**\n\n"

        comment += """---
*Risk prediction powered by ML model trained on historical defect data*
"""

        return comment

    def generate_report(self, analysis: Dict) -> str:
        """Generate detailed risk analysis report"""

        report = f"""
# Risk Analysis Report
Generated: {analysis['timestamp']}

## Summary
- **Branch**: {analysis['branch']}
- **Risk Score**: {analysis['risk_score']:.1f}%
- **Risk Level**: {analysis['risk_level']}

## Metrics
{json.dumps(analysis['metrics'], indent=2, default=str)}

## Features Used
{json.dumps(analysis['features_used'], indent=2)}

## Probabilities
- Low: {analysis['probabilities']['Low']:.1%}
- Medium: {analysis['probabilities']['Medium']:.1%}
- High: {analysis['probabilities']['High']:.1%}

## Recommendation
{json.dumps(analysis['recommendation'], indent=2)}
"""
        return report


# Example usage
if __name__ == '__main__':
    # Initialize analyzer
    analyzer = PRRiskAnalyzer(
        model_path='models/risk_model.pkl',
        repo_path='.'
    )

    # Analyze a branch
    print("🔍 Analyzing branch 'feature'...")
    result = analyzer.analyze_branch('feature', 'main', module='Payment')

    if 'error' not in result:
        print(f"\n✅ Risk: {result['risk_score']:.0f}% ({result['risk_level']})")
        print(f"\n📌 PR Comment:")
        print(analyzer.generate_pr_comment(result))
    else:
        print(f"❌ Error: {result['error']}")
