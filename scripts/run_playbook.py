#!/usr/bin/env python3
"""
Network Automation Playbook Runner
Executes network automation tasks via Telnet using Nornir/Netmiko
"""

import sys
import argparse
from pathlib import Path
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from nornir.core.exceptions import NornirExecutionError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_inventory_files():
    """Check if inventory files exist"""
    required_files = ['hosts.yaml', 'groups.yaml', 'defaults.yaml']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing inventory files: {', '.join(missing_files)}")
        return False
    
    logger.info("All inventory files found")
    return True

def collect_interface_status(nr, device_filter=None):
    """Collect interface status from devices"""
    logger.info("Starting interface status collection...")
    
    # Apply device filter if specified
    if device_filter:
        filtered_nr = nr.filter(name=device_filter)
        if not filtered_nr.inventory.hosts:
            logger.error(f"No devices found with name: {device_filter}")
            return None
    else:
        # Filter devices using Telnet protocol
        filtered_nr = nr.filter(F(groups__contains='telnet_devices'))
        if not filtered_nr.inventory.hosts:
            logger.warning("No telnet devices found, trying all devices...")
            filtered_nr = nr
    
    logger.info(f"Collecting interface status from {len(filtered_nr.inventory.hosts)} device(s)")
    
    try:
        # Task to collect interface status
        result = filtered_nr.run(
            task=netmiko_send_command, 
            command_string='show interfaces',
            name="Collect Interface Status"
        )
        
        logger.info("Interface status collection completed")
        return result
        
    except NornirExecutionError as e:
        logger.error(f"Nornir execution error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        return None

def collect_device_info(nr, device_filter=None):
    """Collect basic device information"""
    logger.info("Starting device information collection...")
    
    # Apply device filter if specified
    if device_filter:
        filtered_nr = nr.filter(name=device_filter)
        if not filtered_nr.inventory.hosts:
            logger.error(f"No devices found with name: {device_filter}")
            return None
    else:
        # Filter devices using Telnet protocol
        filtered_nr = nr.filter(F(groups__contains='telnet_devices'))
        if not filtered_nr.inventory.hosts:
            logger.warning("No telnet devices found, trying all devices...")
            filtered_nr = nr
    
    logger.info(f"Collecting device info from {len(filtered_nr.inventory.hosts)} device(s)")
    
    try:
        # Task to collect device version information
        result = filtered_nr.run(
            task=netmiko_send_command, 
            command_string='show version',
            name="Collect Device Information"
        )
        
        logger.info("Device information collection completed")
        return result
        
    except NornirExecutionError as e:
        logger.error(f"Nornir execution error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during execution: {e}")
        return None

def list_devices(nr):
    """List all available devices in inventory"""
    logger.info("Available devices in inventory:")
    for host_name, host_obj in nr.inventory.hosts.items():
        protocol = 'telnet' if host_obj.port == 23 else 'ssh'
        logger.info(f"  - {host_name}: {host_obj.hostname}:{host_obj.port} ({protocol})")

def main():
    """Main function to execute network automation tasks"""
    parser = argparse.ArgumentParser(description='Network Automation Playbook Runner')
    parser.add_argument('--task', choices=['interfaces', 'device-info', 'list'], 
                       default='interfaces', help='Task to execute')
    parser.add_argument('--device', help='Target specific device by name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting Network Automation Playbook Runner")
    
    # Check if inventory files exist
    if not check_inventory_files():
        logger.error("Cannot proceed without inventory files")
        sys.exit(1)
    
    try:
        # Initialize Nornir
        logger.info("Initializing Nornir...")
        nr = InitNornir(config_file="config.yaml")
        
        logger.info(f"Nornir initialized with {len(nr.inventory.hosts)} device(s)")
        
        # Execute requested task
        if args.task == 'list':
            list_devices(nr)
            
        elif args.task == 'interfaces':
            result = collect_interface_status(nr, args.device)
            if result:
                print("\n" + "=" * 60)
                print("INTERFACE STATUS COLLECTION RESULTS")
                print("=" * 60)
                print_result(result)
                
                # Summary
                successful = len([host for host, result in result.items() if not result.failed])
                failed = len([host for host, result in result.items() if result.failed])
                logger.info(f"Task completed: {successful} successful, {failed} failed")
            
        elif args.task == 'device-info':
            result = collect_device_info(nr, args.device)
            if result:
                print("\n" + "=" * 60)
                print("DEVICE INFORMATION COLLECTION RESULTS")
                print("=" * 60)
                print_result(result)
                
                # Summary
                successful = len([host for host, result in result.items() if not result.failed])
                failed = len([host for host, result in result.items() if result.failed])
                logger.info(f"Task completed: {successful} successful, {failed} failed")
    
    except Exception as e:
        logger.error(f"Error initializing Nornir: {e}")
        sys.exit(1)
    
    logger.info("Network automation task completed")

if __name__ == "__main__":
    main()
