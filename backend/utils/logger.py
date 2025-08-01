import logging
import os
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """
    Function to setup a logger with file and console handlers
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, log_file))
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers for different components
api_logger = setup_logger('api', 'api.log')
db_logger = setup_logger('database', 'database.log')
network_logger = setup_logger('network', 'network.log')
ai_logger = setup_logger('ai', 'ai.log')
security_logger = setup_logger('security', 'security.log')

def log_api_request(method, url, status_code, user_id=None):
    """
    Log API requests
    """
    api_logger.info(f"API Request: {method} {url} - Status: {status_code} - User: {user_id}")

def log_db_operation(operation, table, user_id=None):
    """
    Log database operations
    """
    db_logger.info(f"DB Operation: {operation} on {table} - User: {user_id}")

def log_network_activity(activity, device_ip, status, user_id=None):
    """
    Log network activities
    """
    network_logger.info(f"Network Activity: {activity} on {device_ip} - Status: {status} - User: {user_id}")

def log_ai_interaction(interaction_type, model, prompt_length, response_length, user_id=None):
    """
    Log AI interactions
    """
    ai_logger.info(f"AI Interaction: {interaction_type} with {model} - Prompt: {prompt_length} chars, Response: {response_length} chars - User: {user_id}")

def log_security_event(event_type, description, user_id=None):
    """
    Log security events
    """
    security_logger.warning(f"Security Event: {event_type} - {description} - User: {user_id}")