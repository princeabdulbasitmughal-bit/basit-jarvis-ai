"""
System Audit & Optimization Suite (Basit1 v2.1)
================================================

Provides automated static code analysis (AST), dynamic system metrics monitoring,
AST code transformations for performance, and resilient worker execution pools.
"""

__version__ = "2.1.0"
__author__ = "Basit1 v2.1"

from system_audit_optimizer.config import Settings
from system_audit_optimizer.auditor.ast_scanner import ASTCodeAuditor, AuditIssue, IssueSeverity
from system_audit_optimizer.auditor.metrics_collector import DynamicMetricsCollector, SystemMetrics
from system_audit_optimizer.optimizer.code_transformer import CodeOptimizerEngine
from system_audit_optimizer.optimizer.async_pool import ResilientAsyncWorkerPool

__all__ = [
    "Settings",
    "ASTCodeAuditor",
    "AuditIssue",
    "IssueSeverity",
    "DynamicMetricsCollector",
    "SystemMetrics",
    "CodeOptimizerEngine",
    "ResilientAsyncWorkerPool",
]
