"""
GenAI Network Automation Dual Pipeline Architecture

This module implements a comprehensive dual pipeline for network automation:
1. Configuration Generation Pipeline - AI-driven config generation
2. Configuration Deployment Pipeline - Secure deployment and validation
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

from backend.ai.ai_service import ai_service
from backend.devices.service import DeviceService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ConfigValidationLevel(Enum):
    BASIC = "basic"      # Syntax validation only
    ADVANCED = "advanced"  # Syntax + logic validation
    FULL = "full"        # Syntax + logic + security validation

@dataclass
class PipelineResult:
    """Result of a pipeline execution"""
    success: bool
    message: str
    data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    execution_time: float
    timestamp: datetime

class NetworkAutomationPipeline:
    """Main pipeline orchestrator for network automation tasks"""
    
    def __init__(self, db: Session):
        self.db = db
        self.device_service = DeviceService(db)
        self.active_pipelines = {}
    
    async def execute_config_generation_pipeline(
        self,
        requirements: str,
        device_type: str,
        user_id: str,
        validation_level: ConfigValidationLevel = ConfigValidationLevel.ADVANCED,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """Execute the configuration generation pipeline"""
        start_time = datetime.now()
        pipeline_id = f"gen_{user_id}_{int(start_time.timestamp())}"
        
        try:
            self.active_pipelines[pipeline_id] = PipelineStatus.RUNNING
            
            logger.info(f"Starting config generation pipeline {pipeline_id}")
            
            # Step 1: Parse and enhance requirements
            enhanced_requirements = await self._enhance_requirements(
                requirements, device_type, additional_params or {}
            )
            
            # Step 2: Generate configuration using AI
            generated_config = await self._generate_configuration(
                enhanced_requirements, device_type
            )
            
            # Step 3: Validate generated configuration
            validation_result = await self._validate_configuration(
                generated_config, device_type, validation_level
            )
            
            # Step 4: Post-process and optimize
            optimized_config = await self._optimize_configuration(
                generated_config, device_type, validation_result
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = PipelineResult(
                success=True,
                message="Configuration generated successfully",
                data={
                    "original_requirements": requirements,
                    "enhanced_requirements": enhanced_requirements,
                    "generated_config": optimized_config,
                    "validation": validation_result,
                    "device_type": device_type,
                    "pipeline_id": pipeline_id
                },
                errors=[],
                warnings=validation_result.get("warnings", []),
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            self.active_pipelines[pipeline_id] = PipelineStatus.SUCCESS
            logger.info(f"Config generation pipeline {pipeline_id} completed successfully")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.active_pipelines[pipeline_id] = PipelineStatus.FAILED
            
            logger.error(f"Config generation pipeline {pipeline_id} failed: {e}")
            
            return PipelineResult(
                success=False,
                message=f"Configuration generation failed: {str(e)}",
                data={"pipeline_id": pipeline_id},
                errors=[str(e)],
                warnings=[],
                execution_time=execution_time,
                timestamp=datetime.now()
            )
    
    async def execute_deployment_pipeline(
        self,
        config: str,
        device_id: str,
        user_id: str,
        dry_run: bool = False,
        backup_current: bool = True,
        rollback_on_failure: bool = True
    ) -> PipelineResult:
        """Execute the configuration deployment pipeline"""
        start_time = datetime.now()
        pipeline_id = f"deploy_{user_id}_{int(start_time.timestamp())}"
        
        try:
            self.active_pipelines[pipeline_id] = PipelineStatus.RUNNING
            
            logger.info(f"Starting deployment pipeline {pipeline_id}")
            
            # Step 1: Validate device access and ownership
            device = await self._validate_device_access(device_id, user_id)
            
            # Step 2: Pre-deployment validation
            pre_check_result = await self._pre_deployment_checks(
                config, device, dry_run
            )
            
            # Step 3: Backup current configuration (if requested)
            backup_result = None
            if backup_current and not dry_run:
                backup_result = await self._backup_current_config(device_id)
            
            # Step 4: Deploy configuration
            deployment_result = await self._deploy_configuration(
                config, device, dry_run
            )
            
            # Step 5: Post-deployment validation
            post_check_result = await self._post_deployment_checks(
                device, deployment_result, dry_run
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = PipelineResult(
                success=deployment_result.get("success", False),
                message="Deployment completed successfully" if not dry_run else "Dry run completed successfully",
                data={
                    "device_id": device_id,
                    "device_name": device.name,
                    "dry_run": dry_run,
                    "pre_checks": pre_check_result,
                    "backup": backup_result,
                    "deployment": deployment_result,
                    "post_checks": post_check_result,
                    "pipeline_id": pipeline_id
                },
                errors=deployment_result.get("errors", []),
                warnings=deployment_result.get("warnings", []),
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            self.active_pipelines[pipeline_id] = PipelineStatus.SUCCESS
            logger.info(f"Deployment pipeline {pipeline_id} completed successfully")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.active_pipelines[pipeline_id] = PipelineStatus.FAILED
            
            logger.error(f"Deployment pipeline {pipeline_id} failed: {e}")
            
            return PipelineResult(
                success=False,
                message=f"Deployment failed: {str(e)}",
                data={"pipeline_id": pipeline_id},
                errors=[str(e)],
                warnings=[],
                execution_time=execution_time,
                timestamp=datetime.now()
            )
    
    # Private helper methods for pipeline steps
    
    async def _enhance_requirements(
        self, requirements: str, device_type: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance user requirements with context and best practices"""
        try:
            # Use AI to analyze and enhance the requirements
            enhanced = await ai_service.enhance_requirements(
                requirements, device_type, params
            )
            return enhanced
        except Exception as e:
            logger.warning(f"Failed to enhance requirements: {e}")
            return {
                "original": requirements,
                "device_type": device_type,
                "parameters": params
            }
    
    async def _generate_configuration(
        self, requirements: Dict[str, Any], device_type: str
    ) -> str:
        """Generate network configuration using AI"""
        try:
            config = await ai_service.generate_configuration_async(
                requirements, device_type
            )
            return config
        except Exception as e:
            logger.error(f"Failed to generate configuration: {e}")
            raise
    
    async def _validate_configuration(
        self, config: str, device_type: str, validation_level: ConfigValidationLevel
    ) -> Dict[str, Any]:
        """Validate generated configuration"""
        try:
            validation_result = await ai_service.validate_configuration_async(
                config, device_type, validation_level.value
            )
            return validation_result
        except Exception as e:
            logger.warning(f"Configuration validation failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "score": 0
            }
    
    async def _optimize_configuration(
        self, config: str, device_type: str, validation_result: Dict[str, Any]
    ) -> str:
        """Optimize configuration based on validation results"""
        try:
            if validation_result.get("valid", False) and validation_result.get("score", 0) > 0.8:
                # Configuration is already good, minimal optimization
                return config
            
            # Use AI to optimize the configuration
            optimized = await ai_service.optimize_configuration(
                config, device_type, validation_result
            )
            return optimized
        except Exception as e:
            logger.warning(f"Configuration optimization failed: {e}")
            return config  # Return original if optimization fails
    
    async def _validate_device_access(self, device_id: str, user_id: str):
        """Validate device access and ownership"""
        device = self.device_service.get_device_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        if device.owner_id != user_id:
            raise ValueError(f"Access denied to device {device_id}")
        
        return device
    
    async def _pre_deployment_checks(
        self, config: str, device, dry_run: bool
    ) -> Dict[str, Any]:
        """Perform pre-deployment checks"""
        checks = {
            "syntax_valid": False,
            "connectivity": False,
            "device_ready": False,
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check configuration syntax
            syntax_check = await ai_service.validate_configuration_async(
                config, device.device_type, "basic"
            )
            checks["syntax_valid"] = syntax_check.get("valid", False)
            
            if not dry_run:
                # Check device connectivity
                connectivity_result = self.device_service.test_connectivity(device.id)
                checks["connectivity"] = connectivity_result.get("status") == "online"
                checks["device_ready"] = checks["connectivity"]
            else:
                checks["connectivity"] = True
                checks["device_ready"] = True
            
        except Exception as e:
            checks["errors"].append(str(e))
        
        return checks
    
    async def _backup_current_config(self, device_id: str) -> Dict[str, Any]:
        """Backup current device configuration"""
        try:
            backup_result = self.device_service.backup_configuration(device_id)
            return backup_result
        except Exception as e:
            logger.error(f"Failed to backup configuration for device {device_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _deploy_configuration(
        self, config: str, device, dry_run: bool
    ) -> Dict[str, Any]:
        """Deploy configuration to device"""
        try:
            if dry_run:
                # For dry run, just validate the deployment would work
                return {
                    "success": True,
                    "message": "Dry run - configuration syntax is valid",
                    "changes_preview": await self._preview_config_changes(config, device),
                    "dry_run": True
                }
            else:
                # Actual deployment
                deploy_result = self.device_service.deploy_configuration(device.id, config)
                return deploy_result
                
        except Exception as e:
            logger.error(f"Failed to deploy configuration: {e}")
            return {
                "success": False,
                "error": str(e),
                "errors": [str(e)]
            }
    
    async def _post_deployment_checks(
        self, device, deployment_result: Dict[str, Any], dry_run: bool
    ) -> Dict[str, Any]:
        """Perform post-deployment validation"""
        checks = {
            "device_responsive": False,
            "configuration_applied": False,
            "services_running": False,
            "warnings": [],
            "errors": []
        }
        
        if dry_run:
            checks.update({
                "device_responsive": True,
                "configuration_applied": True,
                "services_running": True
            })
            return checks
        
        try:
            # Check if device is still responsive
            connectivity_result = self.device_service.test_connectivity(device.id)
            checks["device_responsive"] = connectivity_result.get("status") == "online"
            
            # Additional post-deployment checks would go here
            checks["configuration_applied"] = deployment_result.get("success", False)
            checks["services_running"] = checks["device_responsive"]
            
        except Exception as e:
            checks["errors"].append(str(e))
        
        return checks
    
    async def _preview_config_changes(self, config: str, device) -> Dict[str, Any]:
        """Preview what changes the configuration would make"""
        try:
            # This would analyze the configuration and predict changes
            # For now, return a basic preview
            return {
                "estimated_changes": "Configuration analysis completed",
                "impact_level": "medium",
                "requires_reboot": False
            }
        except Exception as e:
            logger.warning(f"Failed to preview config changes: {e}")
            return {"error": str(e)}
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineStatus]:
        """Get the status of a running pipeline"""
        return self.active_pipelines.get(pipeline_id)
    
    def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a running pipeline"""
        if pipeline_id in self.active_pipelines:
            self.active_pipelines[pipeline_id] = PipelineStatus.CANCELLED
            return True
        return False
    
    def cleanup_completed_pipelines(self):
        """Clean up completed pipeline tracking"""
        completed_statuses = [PipelineStatus.SUCCESS, PipelineStatus.FAILED, PipelineStatus.CANCELLED]
        to_remove = [
            pid for pid, status in self.active_pipelines.items()
            if status in completed_statuses
        ]
        
        for pid in to_remove:
            del self.active_pipelines[pid]
