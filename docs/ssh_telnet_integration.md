# SSH/Telnet Integration Plan

## Overview
This document outlines the integration strategy for SSH and Telnet connectivity to network devices using Python libraries including Netmiko, Nonir modules, and Cisco Genie with PyATS. These libraries will enable the application to push and retrieve router configurations.

## Network Connection Architecture

### 1. Connection Manager
```python
class ConnectionManager:
    def __init__(self):
        self.connections = {}
        self.connection_pools = {}
    
    def get_connection(self, device: Device) -> NetworkDeviceConnection:
        # Create connection key
        conn_key = f"{device.ip_address}:{device.port}:{device.protocol}"
        
        # Return existing connection if available
        if conn_key in self.connections:
            return self.connections[conn_key]
        
        # Create new connection based on protocol
        if device.protocol == "ssh":
            connection = SSHConnection(device)
        elif device.protocol == "telnet":
            connection = TelnetConnection(device)
        else:
            raise ValueError(f"Unsupported protocol: {device.protocol}")
        
        # Store connection
        self.connections[conn_key] = connection
        return connection
    
    def close_connection(self, device: Device):
        conn_key = f"{device.ip_address}:{device.port}:{device.protocol}"
        if conn_key in self.connections:
            self.connections[conn_key].close()
            del self.connections[conn_key]
```

## SSH Integration with Netmiko

### 1. Netmiko Connection Adapter
```python
from netmiko import ConnectHandler
import time

class SSHConnection:
    def __init__(self, device: Device):
        self.device = device
        self.connection = None
        self.connect()
    
    def connect(self):
        device_params = {
            'device_type': self._get_netmiko_device_type(),
            'host': self.device.ip_address,
            'username': self.device.username,
            'password': self.device.password,
            'port': self.device.port,
        }
        
        try:
            self.connection = ConnectHandler(**device_params)
        except Exception as e:
            raise ConnectionError(f"Failed to establish SSH connection: {str(e)}")
    
    def _get_netmiko_device_type(self) -> str:
        """Map device type to Netmiko device type"""
        mapping = {
            'ios': 'cisco_ios',
            'iosxr': 'cisco_xr',
            'iosxe': 'cisco_xe'
        }
        return mapping.get(self.device.device_type, 'cisco_ios')
    
    def send_command(self, command: str, expect_string: str = None) -> str:
        """Send command and return output"""
        if not self.connection:
            raise ConnectionError("No active connection")
        
        try:
            if expect_string:
                return self.connection.send_command(command, expect_string=expect_string)
            else:
                return self.connection.send_command(command)
        except Exception as e:
            raise ConnectionError(f"Failed to send command: {str(e)}")
    
    def send_config_set(self, config_commands: list) -> str:
        """Send configuration commands"""
        if not self.connection:
            raise ConnectionError("No active connection")
        
        try:
            return self.connection.send_config_set(config_commands)
        except Exception as e:
            raise ConnectionError(f"Failed to send config: {str(e)}")
    
    def save_config(self) -> str:
        """Save running configuration"""
        return self.send_command("write memory")
    
    def get_running_config(self) -> str:
        """Retrieve running configuration"""
        return self.send_command("show running-config")
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.disconnect()
            self.connection = None
```

## Telnet Integration

### 1. Telnet Connection Adapter
```python
import telnetlib
import time

class TelnetConnection:
    def __init__(self, device: Device):
        self.device = device
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = telnetlib.Telnet(self.device.ip_address, self.device.port)
            
            # Handle login prompt
            self.connection.read_until(b"login: ", 10)
            self.connection.write(self.device.username.encode('ascii') + b"\n")
            
            # Handle password prompt
            self.connection.read_until(b"Password: ", 10)
            self.connection.write(self.device.password.encode('ascii') + b"\n")
            
            # Wait for prompt
            time.sleep(1)
            self.connection.read_very_eager()  # Clear buffer
        except Exception as e:
            raise ConnectionError(f"Failed to establish Telnet connection: {str(e)}")
    
    def send_command(self, command: str) -> str:
        """Send command and return output"""
        if not self.connection:
            raise ConnectionError("No active connection")
        
        try:
            self.connection.write(command.encode('ascii') + b"\n")
            time.sleep(2)  # Wait for command to execute
            output = self.connection.read_very_eager().decode('ascii')
            return output
        except Exception as e:
            raise ConnectionError(f"Failed to send command: {str(e)}")
    
    def send_config_set(self, config_commands: list) -> str:
        """Send configuration commands"""
        output = ""
        try:
            # Enter config mode
            output += self.send_command("configure terminal")
            
            # Send each command
            for command in config_commands:
                output += self.send_command(command)
            
            # Exit config mode
            output += self.send_command("end")
            
            return output
        except Exception as e:
            raise ConnectionError(f"Failed to send config: {str(e)}")
    
    def save_config(self) -> str:
        """Save running configuration"""
        return self.send_command("write memory")
    
    def get_running_config(self) -> str:
        """Retrieve running configuration"""
        return self.send_command("show running-config")
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.write(b"exit\n")
            self.connection.close()
            self.connection = None
```

## Cisco Genie and PyATS Integration

### 1. Genie Parser Integration
```python
from genie.conf import Genie
from genie.libs.parser.utils import get_parser
from pyats.topology import loader

class GenieIntegration:
    def __init__(self):
        self.testbed = None
    
    def initialize_testbed(self, device_info: dict):
        """Initialize PyATS testbed"""
        testbed_data = {
            'devices': {
                device_info['name']: {
                    'connections': {
                        'cli': {
                            'protocol': device_info['protocol'],
                            'ip': device_info['ip_address'],
                            'port': device_info['port'],
                        }
                    },
                    'os': device_info['device_type'],
                    'type': 'router',
                    'credentials': {
                        'default': {
                            'username': device_info['username'],
                            'password': device_info['password']
                        }
                    }
                }
            }
        }
        
        # Create testbed from data
        self.testbed = loader.load(testbed_data)
    
    def parse_output(self, device_name: str, command: str, output: str):
        """Parse command output using Genie parsers"""
        try:
            # Get parser for the command
            parser = get_parser(command, self.testbed.devices[device_name])
            
            # Parse the output
            parsed_output = parser.parse(output)
            return parsed_output
        except Exception as e:
            raise ParsingError(f"Failed to parse output: {str(e)}")
    
    def get_parsed_running_config(self, device_name: str):
        """Get parsed running configuration"""
        # First get raw config
        connection = ConnectionManager().get_connection(device_name)
        raw_config = connection.get_running_config()
        
        # Parse the config
        return self.parse_output(device_name, "show running-config", raw_config)
```

## Nonir Modules Integration

### 1. Nonir Adapter
```python
# Assuming Nonir is a custom or third-party library for network operations
class NonirIntegration:
    def __init__(self):
        self.nonir_client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Nonir client"""
        try:
            # Import Nonir modules
            import nonir
            
            # Initialize client
            self.nonir_client = nonir.Client()
        except ImportError:
            raise ImportError("Nonir library not installed")
        except Exception as e:
            raise InitializationError(f"Failed to initialize Nonir: {str(e)}")
    
    def execute_nonir_operation(self, operation: str, params: dict):
        """Execute Nonir operation"""
        if not self.nonir_client:
            raise InitializationError("Nonir client not initialized")
        
        try:
            # Execute operation based on type
            if operation == "config_push":
                return self.nonir_client.push_config(**params)
            elif operation == "config_pull":
                return self.nonir_client.pull_config(**params)
            elif operation == "device_facts":
                return self.nonir_client.get_facts(**params)
            else:
                raise ValueError(f"Unsupported Nonir operation: {operation}")
        except Exception as e:
            raise OperationError(f"Nonir operation failed: {str(e)}")
```

## Unified Network Device Interface

### 1. Abstract Device Interface
```python
class NetworkDevice:
    def __init__(self, device_info: dict):
        self.device_info = device_info
        self.connection_manager = ConnectionManager()
        self.genie_integration = GenieIntegration()
        self.nonir_integration = NonirIntegration()
    
    def get_connection(self):
        """Get appropriate connection based on device protocol"""
        return self.connection_manager.get_connection(self.device_info)
    
    def push_configuration(self, config_lines: list) -> dict:
        """Push configuration to device"""
        connection = self.get_connection()
        
        try:
            # Send configuration
            output = connection.send_config_set(config_lines)
            
            # Save configuration
            save_output = connection.save_config()
            
            return {
                "success": True,
                "output": output,
                "save_output": save_output
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def retrieve_configuration(self) -> dict:
        """Retrieve configuration from device"""
        connection = self.get_connection()
        
        try:
            # Get running configuration
            config = connection.get_running_config()
            
            # Parse with Genie if needed
            parsed_config = self.genie_integration.parse_output(
                self.device_info['name'], 
                "show running-config", 
                config
            )
            
            return {
                "success": True,
                "raw_config": config,
                "parsed_config": parsed_config
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_command(self, command: str) -> dict:
        """Execute arbitrary command on device"""
        connection = self.get_connection()
        
        try:
            output = connection.send_command(command)
            return {
                "success": True,
                "output": output
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_connectivity(self) -> dict:
        """Test device connectivity"""
        try:
            connection = self.get_connection()
            output = connection.send_command("show version")
            
            # Parse version info with Genie
            parsed_version = self.genie_integration.parse_output(
                self.device_info['name'], 
                "show version", 
                output
            )
            
            return {
                "success": True,
                "status": "online",
                "version_info": parsed_version
            }
        except Exception as e:
            return {
                "success": False,
                "status": "offline",
                "error": str(e)
            }
```

## Connection Pooling and Management

### 1. Connection Pool
```python
import threading
from queue import Queue

class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.active_connections = {}
        self.lock = threading.Lock()
    
    def get_connection(self, device: Device):
        """Get connection from pool or create new one"""
        with self.lock:
            conn_key = f"{device.ip_address}:{device.port}:{device.protocol}"
            
            # Check if we have an active connection
            if conn_key in self.active_connections:
                return self.active_connections[conn_key]
            
            # Try to get from pool
            try:
                connection = self.pool.get_nowait()
                self.active_connections[conn_key] = connection
                return connection
            except:
                # Create new connection if pool is empty
                if device.protocol == "ssh":
                    connection = SSHConnection(device)
                else:
                    connection = TelnetConnection(device)
                
                self.active_connections[conn_key] = connection
                return connection
    
    def return_connection(self, device: Device, connection):
        """Return connection to pool"""
        with self.lock:
            conn_key = f"{device.ip_address}:{device.port}:{device.protocol}"
            
            if conn_key in self.active_connections:
                del self.active_connections[conn_key]
            
            # Try to put back in pool
            try:
                self.pool.put_nowait(connection)
            except:
                # Pool is full, close connection
                connection.close()
```

## Error Handling and Retry Logic

### 1. Robust Connection Handling
```python
import time
import random

class RobustConnectionManager:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_manager = ConnectionManager()
    
    def execute_with_retry(self, device: Device, operation: callable, *args, **kwargs):
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                connection = self.connection_manager.get_connection(device)
                result = operation(connection, *args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Wait before retry with exponential backoff
                    wait_time = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    
                    # Close and recreate connection
                    try:
                        self.connection_manager.close_connection(device)
                    except:
                        pass
        
        # All retries failed
        raise last_exception
```

## Security Considerations

1. Device credentials encrypted at rest
2. Secure connection establishment with proper authentication
3. Input validation for all commands sent to devices
4. Connection timeout settings to prevent hanging connections
5. Secure logging that doesn't expose sensitive information
6. Regular credential rotation capabilities

## Performance Optimization

1. Connection pooling to reduce connection overhead
2. Asynchronous operations for concurrent device access
3. Caching of frequently accessed data
4. Efficient parsing of command outputs
5. Proper resource cleanup to prevent memory leaks

## Monitoring and Logging

1. Connection status monitoring
2. Operation success/failure tracking
3. Performance metrics collection
4. Error logging with context
5. Audit trail for all device interactions