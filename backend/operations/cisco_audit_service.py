"""
Cisco Configuration Audit Service
Provides AI-powered auditing capabilities for Cisco network devices
"""

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session
from backend.database.models import (
    NetworkDevice, AuditResult, ComplianceRule, OperationLog, User
)
from backend.ai.ai_service import AIService
from backend.devices.service import DeviceService

logger = logging.getLogger(__name__)

class CiscoAuditService:
    """Enhanced Cisco configuration audit service with AI analysis"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.device_service = DeviceService(db)
        
        # Cisco-specific configuration patterns
        self.cisco_patterns = {
            'security_issues': [
                r'enable password \w+',  # Unencrypted enable password
                r'username \w+ password \w+',  # Unencrypted user password
                r'no service password-encryption',  # Password encryption disabled
                r'ip http server',  # HTTP server enabled
                r'no ip domain-lookup',  # Domain lookup disabled
            ],
            'best_practices': [
                r'service password-encryption',
                r'no ip http server',
                r'ip ssh version 2',
                r'logging buffered',
                r'ntp server',
            ],
            'compliance_pci': [
                r'access-list \d+ (permit|deny)',  # ACL configuration
                r'crypto key generate rsa',  # RSA key generation
                r'ip ssh time-out',  # SSH timeout
                r'login block-for',  # Login blocking
            ]
        }
    
    async def start_comprehensive_audit(
        self, 
        device_ids: List[str], 
        audit_type: str, 
        user_id: str,
        audit_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a comprehensive audit of selected devices"""
        
        audit_session_id = str(uuid.uuid4())
        audit_options = audit_options or {}
        
        # Create operation log
        operation = OperationLog(
            user_id=user_id,
            operation_type=f'audit_{audit_type}',
            status='running',
            command=f'Audit {len(device_ids)} devices',
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(operation)
        self.db.commit()
        
        try:
            # Process devices in parallel for better performance
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for device_id in device_ids:
                    future = executor.submit(
                        self._audit_single_device,
                        device_id, audit_session_id, audit_type, user_id, audit_options
                    )
                    futures.append(future)
                
                # Wait for all audits to complete
                results = []
                for future in futures:
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout per device
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Device audit failed: {e}")
                        results.append({'error': str(e)})
            
            # Update operation status
            operation.status = 'success'
            operation.result = f'Audited {len(results)} devices successfully'
            operation.execution_time_ms = int((datetime.now(timezone.utc) - operation.created_at).total_seconds() * 1000)
            self.db.commit()
            
            # Generate audit summary
            summary = self._generate_audit_summary(audit_session_id)
            
            return {
                'audit_session_id': audit_session_id,
                'operation_id': operation.id,
                'devices_audited': len(results),
                'total_findings': summary['total_findings'],
                'critical_findings': summary['critical_findings'],
                'estimated_completion_time': 'Completed',
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            operation.status = 'failed'
            operation.error_message = str(e)
            self.db.commit()
            raise
    
    def _audit_single_device(
        self, 
        device_id: str, 
        audit_session_id: str, 
        audit_type: str, 
        user_id: str,
        audit_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Audit a single device configuration"""
        
        try:
            # Get device information
            device = self.db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
            if not device:
                raise Exception(f"Device not found: {device_id}")
            
            # Get current configuration
            config = self._get_device_configuration(device)
            if not config:
                raise Exception(f"Could not retrieve configuration for device: {device.name}")
            
            # Perform AI-powered analysis
            ai_analysis = self._analyze_configuration_with_ai(config, device, audit_type)
            
            # Perform pattern-based analysis
            pattern_findings = self._analyze_configuration_patterns(config, device)
            
            # Combine findings
            all_findings = self._combine_findings(ai_analysis, pattern_findings)
            
            # Save findings to database
            for finding in all_findings:
                audit_result = AuditResult(
                    audit_session_id=audit_session_id,
                    device_id=device_id,
                    user_id=user_id,
                    audit_type=audit_type,
                    severity=finding['severity'],
                    finding_type=finding['type'],
                    finding_title=finding['title'],
                    finding_description=finding['description'],
                    affected_config_section=finding.get('section', 'unknown'),
                    current_config=finding.get('current_config', ''),
                    recommended_config=finding.get('recommended_config', ''),
                    remediation_steps=finding.get('remediation_steps', []),
                    risk_score=finding.get('risk_score', 0.0),
                    compliance_framework=finding.get('compliance_framework', ''),
                    ai_analysis=finding.get('ai_analysis', {}),
                    created_at=datetime.now(timezone.utc)
                )
                self.db.add(audit_result)
            
            self.db.commit()
            
            return {
                'device_id': device_id,
                'device_name': device.name,
                'findings_count': len(all_findings),
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Single device audit failed for {device_id}: {e}")
            return {
                'device_id': device_id,
                'error': str(e),
                'status': 'failed'
            }
    
    def _get_device_configuration(self, device: NetworkDevice) -> Optional[str]:
        """Retrieve current device configuration"""
        
        try:
            # Try to get fresh configuration via SSH
            config = self.device_service.get_device_config(device.id)
            if config:
                return config
            
            # Fallback to stored backup configuration
            if device.config_backup:
                logger.info(f"Using backup configuration for device {device.name}")
                return device.config_backup
            
            logger.warning(f"No configuration available for device {device.name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve configuration for {device.name}: {e}")
            return device.config_backup if device.config_backup else None
    
    def _analyze_configuration_with_ai(
        self, 
        config: str, 
        device: NetworkDevice, 
        audit_type: str
    ) -> List[Dict[str, Any]]:
        """Use AI to analyze device configuration"""
        
        try:
            # Prepare AI prompt based on audit type
            if audit_type == 'security':
                prompt = self._get_security_audit_prompt(config, device)
            elif audit_type == 'compliance':
                prompt = self._get_compliance_audit_prompt(config, device)
            elif audit_type == 'performance':
                prompt = self._get_performance_audit_prompt(config, device)
            else:  # comprehensive
                prompt = self._get_comprehensive_audit_prompt(config, device)
            
            # Get AI analysis
            ai_response = self.ai_service.get_configuration_analysis(prompt)
            
            # Parse AI response into structured findings
            findings = self._parse_ai_audit_response(ai_response, device)
            
            return findings
            
        except Exception as e:
            logger.error(f"AI configuration analysis failed: {e}")
            return []
    
    def _get_comprehensive_audit_prompt(self, config: str, device: NetworkDevice) -> str:
        """Generate comprehensive audit prompt for AI"""
        
        return f"""
        Analyze the following Cisco {device.model} configuration for a comprehensive audit.
        Device: {device.name} ({device.ip_address})
        
        Please analyze for:
        1. Security vulnerabilities and misconfigurations
        2. Performance optimization opportunities
        3. Best practice violations
        4. Compliance issues (PCI-DSS, SOX, NIST)
        5. Configuration drift from industry standards
        6. Potential reliability issues
        
        Configuration:
        ```
        {config[:8000]}  # Limit to avoid token limits
        ```
        
        For each finding, provide:
        - Severity level (critical, high, medium, low, info)
        - Finding type and title
        - Detailed description
        - Current problematic configuration
        - Recommended configuration fix
        - Step-by-step remediation
        - Risk score (0-10)
        - Compliance framework if applicable
        
        Format the response as JSON with an array of findings.
        """
    
    def _get_security_audit_prompt(self, config: str, device: NetworkDevice) -> str:
        """Generate security-focused audit prompt"""
        
        return f"""
        Perform a security audit on this Cisco {device.model} configuration.
        Device: {device.name} ({device.ip_address})
        
        Focus on identifying:
        1. Weak or default passwords
        2. Unencrypted protocols
        3. Missing access controls
        4. Insecure service configurations
        5. Authentication vulnerabilities
        6. Authorization bypass risks
        7. Logging and monitoring gaps
        
        Configuration:
        ```
        {config[:8000]}
        ```
        
        Provide detailed security findings with remediation steps.
        Format as JSON array of security findings.
        """
    
    def _analyze_configuration_patterns(
        self, 
        config: str, 
        device: NetworkDevice
    ) -> List[Dict[str, Any]]:
        """Analyze configuration using predefined patterns"""
        
        findings = []
        
        # Check for security issues
        for pattern in self.cisco_patterns['security_issues']:
            matches = re.findall(pattern, config, re.IGNORECASE)
            if matches:
                findings.append({
                    'severity': 'high',
                    'type': 'security_vulnerability',
                    'title': f'Security Issue: {pattern}',
                    'description': f'Found security vulnerability pattern: {pattern}',
                    'section': 'security',
                    'current_config': '\n'.join(matches),
                    'risk_score': 7.0,
                    'remediation_steps': [f'Remove or fix: {pattern}']
                })
        
        # Check for missing best practices
        missing_practices = []
        for pattern in self.cisco_patterns['best_practices']:
            if not re.search(pattern, config, re.IGNORECASE):
                missing_practices.append(pattern)
        
        if missing_practices:
            findings.append({
                'severity': 'medium',
                'type': 'best_practice_violation',
                'title': 'Missing Best Practices',
                'description': f'Missing recommended configurations: {", ".join(missing_practices)}',
                'section': 'best_practices',
                'recommended_config': '\n'.join(missing_practices),
                'risk_score': 4.0,
                'remediation_steps': [f'Add configuration: {practice}' for practice in missing_practices]
            })
        
        return findings
    
    def _combine_findings(
        self, 
        ai_findings: List[Dict[str, Any]], 
        pattern_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine AI and pattern-based findings, removing duplicates"""
        
        all_findings = []
        seen_titles = set()
        
        # Add AI findings first (they're typically more detailed)
        for finding in ai_findings:
            title = finding.get('title', '')
            if title not in seen_titles:
                all_findings.append(finding)
                seen_titles.add(title)
        
        # Add pattern findings that weren't already found by AI
        for finding in pattern_findings:
            title = finding.get('title', '')
            if title not in seen_titles:
                all_findings.append(finding)
                seen_titles.add(title)
        
        return all_findings
    
    def _parse_ai_audit_response(
        self, 
        ai_response: str, 
        device: NetworkDevice
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured findings"""
        
        try:
            # Try to extract JSON from AI response
            if '```json' in ai_response:
                json_start = ai_response.find('```json') + 7
                json_end = ai_response.find('```', json_start)
                json_content = ai_response[json_start:json_end].strip()
            elif '[' in ai_response and ']' in ai_response:
                # Try to find JSON array
                start = ai_response.find('[')
                end = ai_response.rfind(']') + 1
                json_content = ai_response[start:end]
            else:
                # Fallback: create structured finding from text
                return [{
                    'severity': 'info',
                    'type': 'ai_analysis',
                    'title': 'AI Configuration Analysis',
                    'description': ai_response[:1000],  # Limit length
                    'section': 'general',
                    'risk_score': 2.0,
                    'ai_analysis': {'raw_response': ai_response}
                }]
            
            findings = json.loads(json_content)
            
            # Validate and normalize findings
            normalized_findings = []
            for finding in findings:
                if isinstance(finding, dict):
                    normalized_finding = {
                        'severity': finding.get('severity', 'medium').lower(),
                        'type': finding.get('type', 'configuration_issue'),
                        'title': finding.get('title', 'Configuration Issue'),
                        'description': finding.get('description', ''),
                        'section': finding.get('section', 'general'),
                        'current_config': finding.get('current_config', ''),
                        'recommended_config': finding.get('recommended_config', ''),
                        'remediation_steps': finding.get('remediation_steps', []),
                        'risk_score': float(finding.get('risk_score', 0.0)),
                        'compliance_framework': finding.get('compliance_framework', ''),
                        'ai_analysis': finding
                    }
                    normalized_findings.append(normalized_finding)
            
            return normalized_findings
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return [{
                'severity': 'info',
                'type': 'ai_analysis',
                'title': 'AI Configuration Analysis',
                'description': ai_response[:1000],
                'section': 'general',
                'risk_score': 2.0,
                'ai_analysis': {'raw_response': ai_response, 'parse_error': str(e)}
            }]
        except Exception as e:
            logger.error(f"Error parsing AI audit response: {e}")
            return []
    
    def _generate_audit_summary(self, audit_session_id: str) -> Dict[str, Any]:
        """Generate summary statistics for an audit session"""
        
        try:
            # Get all findings for this audit session
            findings = self.db.query(AuditResult).filter(
                AuditResult.audit_session_id == audit_session_id
            ).all()
            
            total_findings = len(findings)
            severity_counts = {}
            type_counts = {}
            device_counts = {}
            
            for finding in findings:
                # Count by severity
                severity = finding.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Count by type
                finding_type = finding.finding_type
                type_counts[finding_type] = type_counts.get(finding_type, 0) + 1
                
                # Count by device
                device_name = finding.device.name if finding.device else 'Unknown'
                device_counts[device_name] = device_counts.get(device_name, 0) + 1
            
            return {
                'total_findings': total_findings,
                'critical_findings': severity_counts.get('critical', 0),
                'high_findings': severity_counts.get('high', 0),
                'medium_findings': severity_counts.get('medium', 0),
                'low_findings': severity_counts.get('low', 0),
                'severity_distribution': severity_counts,
                'finding_types': type_counts,
                'device_distribution': device_counts,
                'audit_session_id': audit_session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to generate audit summary: {e}")
            return {
                'total_findings': 0,
                'critical_findings': 0,
                'error': str(e)
            }
    
    def get_audit_results(
        self, 
        audit_session_id: str, 
        severity_filter: Optional[str] = None,
        device_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get detailed audit results with optional filtering"""
        
        try:
            query = self.db.query(AuditResult).filter(
                AuditResult.audit_session_id == audit_session_id
            )
            
            # Apply filters
            if severity_filter:
                query = query.filter(AuditResult.severity == severity_filter)
            
            if device_filter:
                query = query.filter(AuditResult.device_id == device_filter)
            
            findings = query.order_by(
                AuditResult.severity.desc(),
                AuditResult.risk_score.desc()
            ).all()
            
            # Convert to dictionaries
            results = []
            for finding in findings:
                result = {
                    'id': finding.id,
                    'device_name': finding.device.name if finding.device else 'Unknown',
                    'device_ip': finding.device.ip_address if finding.device else '',
                    'severity': finding.severity,
                    'finding_type': finding.finding_type,
                    'title': finding.finding_title,
                    'description': finding.finding_description,
                    'affected_section': finding.affected_config_section,
                    'current_config': finding.current_config,
                    'recommended_config': finding.recommended_config,
                    'remediation_steps': finding.remediation_steps,
                    'risk_score': finding.risk_score,
                    'compliance_framework': finding.compliance_framework,
                    'status': finding.status,
                    'created_at': finding.created_at.isoformat(),
                    'ai_analysis': finding.ai_analysis
                }
                results.append(result)
            
            summary = self._generate_audit_summary(audit_session_id)
            
            return {
                'audit_session_id': audit_session_id,
                'summary': summary,
                'findings': results,
                'total_count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Failed to get audit results: {e}")
            raise Exception(f"Failed to retrieve audit results: {str(e)}")
    
    def export_audit_results(
        self, 
        audit_session_id: str, 
        export_format: str = 'json'
    ) -> Dict[str, Any]:
        """Export audit results in various formats"""
        
        try:
            results = self.get_audit_results(audit_session_id)
            
            if export_format.lower() == 'json':
                return {
                    'format': 'json',
                    'data': results,
                    'filename': f'audit_results_{audit_session_id}.json'
                }
            elif export_format.lower() == 'csv':
                # Convert to CSV format
                csv_data = self._convert_to_csv(results['findings'])
                return {
                    'format': 'csv',
                    'data': csv_data,
                    'filename': f'audit_results_{audit_session_id}.csv'
                }
            else:
                raise Exception(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
    
    def _convert_to_csv(self, findings: List[Dict[str, Any]]) -> str:
        """Convert findings to CSV format"""
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Device Name', 'Device IP', 'Severity', 'Finding Type', 'Title',
            'Description', 'Risk Score', 'Status', 'Created At'
        ])
        
        # Write data
        for finding in findings:
            writer.writerow([
                finding.get('device_name', ''),
                finding.get('device_ip', ''),
                finding.get('severity', ''),
                finding.get('finding_type', ''),
                finding.get('title', ''),
                finding.get('description', '')[:200],  # Limit description length
                finding.get('risk_score', 0),
                finding.get('status', ''),
                finding.get('created_at', '')
            ])
        
        return output.getvalue()
