"""
WebSocket Manager for Real-time Operations Updates
Handles WebSocket connections, message broadcasting, and device command execution updates
"""
import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by session/user
        self.active_connections: Dict[str, WebSocket] = {}
        # Track connections by operation type for targeted broadcasting
        self.operation_connections: Dict[str, Set[str]] = {
            'audit': set(),
            'troubleshoot': set(),
            'baseline': set(),
            'command_execution': set()
        }

    async def connect(self, websocket: WebSocket, client_id: str, operation_type: str = None):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if operation_type and operation_type in self.operation_connections:
            self.operation_connections[operation_type].add(client_id)
            
        logger.info(f"Client {client_id} connected for {operation_type or 'general'} operations")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_confirmed",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to real-time updates"
        }, client_id)

    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
        # Remove from all operation types
        for operation_type in self.operation_connections:
            self.operation_connections[operation_type].discard(client_id)
            
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast_to_operation(self, message: dict, operation_type: str):
        """Broadcast message to all clients subscribed to specific operation type"""
        if operation_type not in self.operation_connections:
            return
            
        disconnected_clients = []
        for client_id in self.operation_connections[operation_type].copy():
            try:
                await self.send_personal_message(message, client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        for client_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(message, client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)

    async def send_operation_update(self, operation_id: str, operation_type: str, status: str, 
                                  progress: int = None, message: str = None, data: dict = None):
        """Send standardized operation update"""
        update = {
            "type": "operation_update",
            "operation_id": operation_id,
            "operation_type": operation_type,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "progress": progress,
            "message": message,
            "data": data or {}
        }
        
        await self.broadcast_to_operation(update, operation_type)

    async def send_device_status(self, device_id: str, device_name: str, status: str, 
                               details: dict = None):
        """Send device status update"""
        update = {
            "type": "device_status",
            "device_id": device_id,
            "device_name": device_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        await self.broadcast_to_operation(update, "command_execution")

    async def send_command_result(self, device_id: str, command: str, result: str, 
                                success: bool, execution_time: float = None):
        """Send command execution result"""
        update = {
            "type": "command_result",
            "device_id": device_id,
            "command": command,
            "result": result,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_operation(update, "command_execution")


# Global connection manager instance
connection_manager = ConnectionManager()


class DeviceCommandExecutor:
    """Handles real-time device command execution with WebSocket updates"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        
    async def execute_command_with_updates(self, device_id: str, device_name: str, 
                                         command: str, timeout: int = 30):
        """Execute command on device with real-time WebSocket updates"""
        
        # Send start notification
        await self.connection_manager.send_device_status(
            device_id=device_id,
            device_name=device_name,
            status="connecting",
            details={"command": command}
        )
        
        try:
            # Simulate device connection (replace with actual device connection logic)
            await asyncio.sleep(1)  # Simulate connection time
            
            await self.connection_manager.send_device_status(
                device_id=device_id,
                device_name=device_name,
                status="connected",
                details={"command": command}
            )
            
            # Execute command (replace with actual command execution)
            start_time = datetime.now()
            
            # Simulate command execution
            await asyncio.sleep(2)  # Simulate command execution time
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Mock command result (replace with actual result)
            mock_result = f"""
Router#show version
Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.1(4)M4
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2012 by Cisco Systems, Inc.

ROM: System Bootstrap, Version 15.0(1r)M15, RELEASE SOFTWARE (fc1)

Router uptime is 2 days, 14 hours, 23 minutes
System returned to ROM by power-on
System restarted at 09:15:32 UTC Mon Jan 1 2024
System image file is "flash0:c2900-universalk9-mz.SPA.151-4.M4.bin"
            """
            
            # Send success result
            await self.connection_manager.send_command_result(
                device_id=device_id,
                command=command,
                result=mock_result.strip(),
                success=True,
                execution_time=execution_time
            )
            
            await self.connection_manager.send_device_status(
                device_id=device_id,
                device_name=device_name,
                status="command_completed",
                details={
                    "command": command,
                    "execution_time": execution_time,
                    "success": True
                }
            )
            
            return {
                "success": True,
                "result": mock_result.strip(),
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Send error result
            await self.connection_manager.send_command_result(
                device_id=device_id,
                command=command,
                result=str(e),
                success=False
            )
            
            await self.connection_manager.send_device_status(
                device_id=device_id,
                device_name=device_name,
                status="error",
                details={
                    "command": command,
                    "error": str(e)
                }
            )
            
            return {
                "success": False,
                "error": str(e)
            }

# Global command executor instance
command_executor = DeviceCommandExecutor(connection_manager)
