"""
ServiceNow Incident Management Service (Medium Risk)

Metrics:
- Files changed: 7
- Lines changed: 250
- Test coverage: 68%
- Developer experience: 1 mid-level + 1 junior
- Open defects: 2
- Expected risk: 55% (MEDIUM)
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class IncidentStatus(Enum):
    """Incident workflow states"""
    NEW = "New"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class IncidentRouter:
    """Routes incidents to appropriate teams based on severity"""

    ROUTING_MAP = {
        IncidentSeverity.CRITICAL: "network_ops",
        IncidentSeverity.HIGH: "platform_team",
        IncidentSeverity.MEDIUM: "application_team",
        IncidentSeverity.LOW: "support_team"
    }

    @staticmethod
    def get_group(severity: IncidentSeverity) -> str:
        """Get assignment group for severity level"""
        return IncidentRouter.ROUTING_MAP.get(severity, "support_team")


class SLAManager:
    """Manages SLA deadlines for incidents"""

    SLA_HOURS = {
        IncidentSeverity.CRITICAL: 1,
        IncidentSeverity.HIGH: 4,
        IncidentSeverity.MEDIUM: 8,
        IncidentSeverity.LOW: 24
    }

    @staticmethod
    def calculate_deadline(severity: IncidentSeverity) -> datetime:
        """Calculate SLA deadline based on severity"""
        hours = SLAManager.SLA_HOURS.get(severity, 24)
        return datetime.now() + timedelta(hours=hours)

    @staticmethod
    def is_breached(deadline: datetime) -> bool:
        """Check if SLA has been breached"""
        return datetime.now() > deadline


class IncidentProcessor:
    """Processes ServiceNow incidents with SLA and routing"""

    def __init__(self, db_client, notification_service):
        self.db = db_client
        self.notifier = notification_service
        self.router = IncidentRouter()
        self.sla_manager = SLAManager()

    def create_incident(self, title: str, description: str,
                       severity: IncidentSeverity, reporter_email: str) -> Dict:
        """Create and route a new incident"""

        incident = {
            'id': self._generate_id(),
            'title': title,
            'description': description,
            'severity': severity.value,
            'status': IncidentStatus.NEW.value,
            'assigned_group': self.router.get_group(severity),
            'sla_deadline': self.sla_manager.calculate_deadline(severity),
            'reporter_email': reporter_email,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        # Store in database
        self.db.insert('incidents', incident)
        logger.info(f"Created incident {incident['id']}: {title}")

        # Send notifications
        self._notify_team(incident)

        # Escalate if critical
        if severity == IncidentSeverity.CRITICAL:
            self._escalate_critical(incident)

        return incident

    def update_status(self, incident_id: str, new_status: IncidentStatus) -> Optional[Dict]:
        """Update incident status"""
        incident = self.db.get('incidents', incident_id)

        if not incident:
            logger.warning(f"Incident {incident_id} not found")
            return None

        incident['status'] = new_status.value
        incident['updated_at'] = datetime.now()

        self.db.update('incidents', incident)
        logger.info(f"Updated incident {incident_id} to {new_status.value}")

        return incident

    def get_sla_status(self, incident_id: str) -> Dict:
        """Check SLA status for an incident"""
        incident = self.db.get('incidents', incident_id)

        if not incident:
            return {'error': f"Incident {incident_id} not found"}

        deadline = incident['sla_deadline']
        breached = self.sla_manager.is_breached(deadline)
        hours_remaining = (deadline - datetime.now()).total_seconds() / 3600

        return {
            'incident_id': incident_id,
            'sla_deadline': deadline,
            'breached': breached,
            'hours_remaining': max(0, hours_remaining)
        }

    def _notify_team(self, incident: Dict):
        """Notify assigned team about new incident"""
        try:
            self.notifier.send_email(
                to=incident['assigned_group'],
                subject=f"[{incident['severity']}] Incident {incident['id']}: {incident['title']}",
                body=f"Description: {incident['description']}\n"
                     f"SLA Deadline: {incident['sla_deadline']}"
            )
            logger.info(f"Notified {incident['assigned_group']} about incident {incident['id']}")
        except Exception as e:
            logger.error(f"Failed to notify team: {e}")

    def _escalate_critical(self, incident: Dict):
        """Escalate critical incidents to management"""
        try:
            self.notifier.send_slack(
                channel="#critical-incidents",
                message=f"🚨 CRITICAL INCIDENT: {incident['title']}\n"
                        f"ID: {incident['id']}\n"
                        f"Group: {incident['assigned_group']}"
            )
            logger.info(f"Escalated critical incident {incident['id']}")
        except Exception as e:
            logger.error(f"Failed to escalate incident: {e}")

    def _generate_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = "".join([str(i % 10) for i in range(5)])
        return f"INC-{timestamp}-{random_suffix}"
