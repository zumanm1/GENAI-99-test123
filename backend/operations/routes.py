from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel
import uuid
import asyncio
import json

from backend.database.database import get_db
from backend.operations.service import OperationService
from backend.operations.cisco_audit_service import CiscoAuditService
from backend.database.models import OperationLog, NetworkDevice, AuditResult
from backend.websocket_manager import connection_manager, command_executor

router = APIRouter()

# Pydantic models for request/response
class AuditRequest(BaseModel):
    device_ids: List[str]
    audit_type: str  # comprehensive, security, compliance, performance
    audit_options: Optional[Dict[str, Any]] = {}

class TroubleshootRequest(BaseModel):
    problem_description: str
    problem_domain: str  # connectivity, performance, routing, security, hardware
    affected_devices: List[str]
    symptoms: List[str] = []

class BaselineRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    device_ids: List[str]
    baseline_type: str  # golden, environment, device_specific
    environment: Optional[str] = "prod"

@router.get("/")
async def get_operations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    operation_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get operations with optional filtering"""
    try:
        operation_service = OperationService(db)
        operations = operation_service.get_operations(
            skip=skip,
            limit=limit,
            status=status,
            operation_type=operation_type
        )
        
        return [
            {
                'id': op.id,
                'operation_type': op.operation_type,
                'status': op.status,
                'device_name': op.device.name if op.device else 'System',
                'command': op.command,
                'result': op.result,
                'error_message': op.error_message,
                'execution_time_ms': op.execution_time_ms,
                'created_at': op.created_at.isoformat(),
                'user_id': op.user_id,
                'device_id': op.device_id
            }
            for op in operations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{operation_id}")
async def get_operation(operation_id: str, db: Session = Depends(get_db)):
    """Get operation by ID"""
    try:
        operation = db.query(OperationLog).filter(OperationLog.id == operation_id).first()
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        return {
            'id': operation.id,
            'operation_type': operation.operation_type,
            'status': operation.status,
            'device_name': operation.device.name if operation.device else 'System',
            'command': operation.command,
            'result': operation.result,
            'error_message': operation.error_message,
            'execution_time_ms': operation.execution_time_ms,
            'created_at': operation.created_at.isoformat(),
            'user_id': operation.user_id,
            'device_id': operation.device_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_operation(
    operation_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new operation"""
    try:
        operation = OperationLog(
            operation_type=operation_data.get('operation_type'),
            status=operation_data.get('status', 'pending'),
            command=operation_data.get('command'),
            user_id=operation_data.get('user_id'),
            device_id=operation_data.get('device_id'),
            result=operation_data.get('result'),
            error_message=operation_data.get('error_message'),
            execution_time_ms=operation_data.get('execution_time_ms'),
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        
        return {
            'id': operation.id,
            'operation_type': operation.operation_type,
            'status': operation.status,
            'message': 'Operation created successfully'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/summary")
async def get_operation_statistics(db: Session = Depends(get_db)):
    """Get operation statistics summary"""
    try:
        operation_service = OperationService(db)
        stats = operation_service.get_operation_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{operation_id}")
async def delete_operation(operation_id: str, db: Session = Depends(get_db)):
    """Delete operation by ID"""
    try:
        operation = db.query(OperationLog).filter(OperationLog.id == operation_id).first()
        if not operation:
            raise HTTPException(status_code=404, detail="Operation not found")
        
        db.delete(operation)
        db.commit()
        
        return {"message": "Operation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# GENAI Operations - Audit Endpoints
@router.post("/audit/start")
async def start_audit(
    audit_request: AuditRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start configuration audit for selected devices"""
    try:
        # Validate devices exist
        devices = db.query(NetworkDevice).filter(
            NetworkDevice.id.in_(audit_request.device_ids)
        ).all()
        
        if len(devices) != len(audit_request.device_ids):
            raise HTTPException(
                status_code=400, 
                detail="One or more devices not found"
            )
        
        audit_service = CiscoAuditService(db)
        
        # For now, use a default user_id - in production this would come from authentication
        user_id = "admin-user-id"  # TODO: Get from current_user when auth is implemented
        
        # Start audit asynchronously
        result = await audit_service.start_comprehensive_audit(
            device_ids=audit_request.device_ids,
            audit_type=audit_request.audit_type,
            user_id=user_id,
            audit_options=audit_request.audit_options
        )
        
        return {
            "status": "success",
            "message": "Audit started successfully",
            "audit_session_id": result["audit_session_id"],
            "operation_id": result["operation_id"],
            "devices_audited": result["devices_audited"],
            "estimated_completion_time": result["estimated_completion_time"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

@router.get("/audit/{audit_id}/status")
async def get_audit_status(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """Get real-time audit progress"""
    try:
        # Get audit results count
        findings_count = db.query(AuditResult).filter(
            AuditResult.audit_session_id == audit_id
        ).count()
        
        # Check if audit is complete (simplified check)
        operation = db.query(OperationLog).filter(
            OperationLog.operation_type.like("audit_%")
        ).order_by(OperationLog.created_at.desc()).first()
        
        status = "completed" if operation and operation.status == "success" else "running"
        
        return {
            "audit_session_id": audit_id,
            "status": status,
            "progress_percentage": 100 if status == "completed" else 75,
            "findings_count": findings_count,
            "current_device": "Analysis complete" if status == "completed" else "Processing..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/{audit_id}/results")
async def get_audit_results(
    audit_id: str,
    severity_filter: Optional[str] = Query(None),
    device_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get detailed audit results"""
    try:
        audit_service = CiscoAuditService(db)
        results = audit_service.get_audit_results(
            audit_session_id=audit_id,
            severity_filter=severity_filter,
            device_filter=device_filter
        )
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/audit/{audit_id}/export")
async def export_audit_results(
    audit_id: str,
    export_format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Export audit results to various formats"""
    try:
        audit_service = CiscoAuditService(db)
        export_data = audit_service.export_audit_results(
            audit_session_id=audit_id,
            export_format=export_format
        )
        
        return {
            "status": "success",
            "format": export_data["format"],
            "filename": export_data["filename"],
            "download_url": f"/api/operations/audit/{audit_id}/download/{export_data['filename']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GENAI Operations - Troubleshooting Endpoints
@router.post("/troubleshoot/start")
async def start_troubleshooting(
    troubleshoot_request: TroubleshootRequest,
    db: Session = Depends(get_db)
):
    """Start AI-powered troubleshooting session"""
    try:
        from backend.ai.ai_service import AIService
        
        ai_service = AIService()
        
        # Prepare troubleshooting data
        scenario_data = {
            "problem_description": troubleshoot_request.problem_description,
            "problem_domain": troubleshoot_request.problem_domain,
            "affected_devices": troubleshoot_request.affected_devices,
            "symptoms": troubleshoot_request.symptoms
        }
        
        # Get AI analysis
        analysis_result = ai_service.analyze_troubleshooting_scenario(scenario_data)
        
        # Create troubleshooting session record
        from backend.database.models import TroubleshootingSession
        import uuid
        
        session = TroubleshootingSession(
            session_name=f"Troubleshooting - {troubleshoot_request.problem_domain}",
            user_id="admin-user-id",  # TODO: Get from current_user
            problem_description=troubleshoot_request.problem_description,
            problem_domain=troubleshoot_request.problem_domain,
            affected_devices=troubleshoot_request.affected_devices,
            symptoms=troubleshoot_request.symptoms,
            ai_analysis=analysis_result,
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "status": "success",
            "session_id": session.id,
            "initial_analysis": analysis_result,
            "message": "Troubleshooting session started successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Troubleshooting failed: {str(e)}")

@router.get("/troubleshoot/{session_id}/progress")
async def get_troubleshooting_progress(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get troubleshooting progress and findings"""
    try:
        from backend.database.models import TroubleshootingSession
        
        session = db.query(TroubleshootingSession).filter(
            TroubleshootingSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Troubleshooting session not found")
        
        return {
            "session_id": session.id,
            "status": session.status,
            "current_step": "Analysis completed" if session.ai_analysis else "Analyzing...",
            "findings": session.ai_analysis if session.ai_analysis else {},
            "recommendations": session.resolution_steps if session.resolution_steps else [],
            "progress_percentage": 100 if session.status == "resolved" else 75
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GENAI Operations - Baseline Management Endpoints
@router.post("/baseline/create")
async def create_baseline(
    baseline_request: BaselineRequest,
    db: Session = Depends(get_db)
):
    """Create new configuration baseline"""
    try:
        from backend.database.models import BaselineConfig
        from backend.ai.ai_service import AIService
        
        # Get device information for baseline generation
        devices = db.query(NetworkDevice).filter(
            NetworkDevice.id.in_(baseline_request.device_ids)
        ).all()
        
        if not devices:
            raise HTTPException(status_code=400, detail="No devices found")
        
        # Prepare device data for AI analysis
        devices_data = [{
            "name": device.name,
            "ip_address": device.ip_address,
            "model": device.model,
            "status": device.status
        } for device in devices]
        
        # Generate AI-powered baseline recommendations
        ai_service = AIService()
        recommendations = ai_service.generate_baseline_recommendations(devices_data)
        
        # Create baseline configuration
        baseline = BaselineConfig(
            name=baseline_request.name,
            description=baseline_request.description,
            baseline_type=baseline_request.baseline_type,
            environment=baseline_request.environment,
            config_template=recommendations.get("recommendations", ""),
            config_sections={"ai_generated": True},
            user_id="admin-user-id",  # TODO: Get from current_user
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(baseline)
        db.commit()
        db.refresh(baseline)
        
        return {
            "status": "success",
            "baseline_id": baseline.id,
            "creation_status": "completed",
            "message": "Baseline created successfully",
            "recommendations": recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Baseline creation failed: {str(e)}")

@router.get("/baseline/{baseline_id}/drift")
async def get_baseline_drift(
    baseline_id: str,
    db: Session = Depends(get_db)
):
    """Get configuration drift analysis"""
    try:
        from backend.database.models import BaselineConfig, ConfigurationDrift
        
        baseline = db.query(BaselineConfig).filter(
            BaselineConfig.id == baseline_id
        ).first()
        
        if not baseline:
            raise HTTPException(status_code=404, detail="Baseline not found")
        
        # Get drift records for this baseline
        drifts = db.query(ConfigurationDrift).filter(
            ConfigurationDrift.baseline_id == baseline_id
        ).all()
        
        drift_analysis = []
        affected_devices = set()
        
        for drift in drifts:
            drift_analysis.append({
                "id": drift.id,
                "device_name": drift.device.name if drift.device else "Unknown",
                "drift_type": drift.drift_type,
                "config_section": drift.config_section,
                "description": drift.drift_description,
                "risk_level": drift.risk_level,
                "detected_at": drift.detected_at.isoformat()
            })
            affected_devices.add(drift.device_id)
        
        # Calculate risk assessment
        high_risk_count = len([d for d in drifts if d.risk_level == "high"])
        medium_risk_count = len([d for d in drifts if d.risk_level == "medium"])
        
        risk_assessment = {
            "overall_risk": "high" if high_risk_count > 0 else "medium" if medium_risk_count > 0 else "low",
            "total_drifts": len(drifts),
            "high_risk_drifts": high_risk_count,
            "medium_risk_drifts": medium_risk_count,
            "affected_devices_count": len(affected_devices)
        }
        
        return {
            "baseline_id": baseline_id,
            "baseline_name": baseline.name,
            "drift_analysis": drift_analysis,
            "affected_devices": list(affected_devices),
            "risk_assessment": risk_assessment
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@router.websocket("/ws/operations")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time operations updates"""
    client_id = str(uuid.uuid4())
    
    try:
        await connection_manager.connect(websocket, client_id, "command_execution")
        
        while True:
            # Keep the connection alive and handle incoming messages
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, client_id)
                elif message.get("type") == "subscribe":
                    operation_type = message.get("operation_type", "command_execution")
                    if operation_type in connection_manager.operation_connections:
                        connection_manager.operation_connections[operation_type].add(client_id)
                        await connection_manager.send_personal_message({
                            "type": "subscribed",
                            "operation_type": operation_type,
                            "message": f"Subscribed to {operation_type} updates"
                        }, client_id)
                        
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                # Invalid JSON, ignore
                pass
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        connection_manager.disconnect(client_id)

# Command execution with real-time updates
@router.post("/execute-command")
async def execute_command_on_device(
    device_id: str,
    command: str,
    db: Session = Depends(get_db)
):
    """Execute command on device with real-time WebSocket updates"""
    try:
        # Get device info
        device = db.query(NetworkDevice).filter(NetworkDevice.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Execute command with real-time updates
        result = await command_executor.execute_command_with_updates(
            device_id=device_id,
            device_name=device.name,
            command=command
        )
        
        # Log the operation
        operation = OperationLog(
            operation_type="command_execution",
            status="success" if result["success"] else "error",
            command=command,
            result=result.get("result", ""),
            error_message=result.get("error", ""),
            execution_time_ms=int(result.get("execution_time", 0) * 1000),
            device_id=device_id,
            user_id="admin-user-id",  # TODO: Get from current_user
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(operation)
        db.commit()
        db.refresh(operation)
        
        return {
            "status": "success" if result["success"] else "error",
            "operation_id": operation.id,
            "result": result.get("result", ""),
            "execution_time": result.get("execution_time", 0),
            "error": result.get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command execution failed: {str(e)}")
