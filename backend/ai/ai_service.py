import openai
import anthropic
from backend.database.models import AIConversation, NetworkDevice, OperationLog, User
from backend.database.database import get_db
from sqlalchemy.orm import Session
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service class for AI operations matching PRD specifications"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI service clients"""
        try:
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key and openai_key != 'your_openai_api_key':
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        try:
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            if anthropic_key and anthropic_key != 'your_anthropic_api_key':
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Anthropic client: {e}")
    
    def get_response(self, user_message: str, session_id: str, user_id: str, db: Session) -> str:
        """Get AI response to user message"""
        try:
            # Get conversation context
            context = self._get_conversation_context(session_id, user_id, db)
            
            # Get system context (device info, recent operations)
            system_context = self._get_system_context(user_id, db)
            
            # Prepare messages for AI
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a GENAI network assistant specialized in Cisco network automation. 
                    You help with network configuration, troubleshooting, and automation tasks.
                    
                    Current system context:
                    {json.dumps(system_context, indent=2)}
                    
                    Provide helpful, accurate responses about network operations. If you need to perform 
                    actions on devices, explain what you would do but note that actual device operations 
                    require manual confirmation."""
                }
            ]
            
            # Add conversation history
            for msg in context:
                messages.append({
                    "role": msg.message_role,
                    "content": msg.message_content
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Try OpenAI first
            if self.openai_client:
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        max_tokens=1000,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.warning(f"OpenAI request failed: {e}")
            
            # Fallback to Anthropic Claude
            if self.anthropic_client:
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1000,
                        messages=messages[1:],  # Claude doesn't need system message in messages array
                        system=messages[0]["content"]
                    )
                    return response.content[0].text
                except Exception as e:
                    logger.warning(f"Anthropic request failed: {e}")
            
            # Fallback response
            return "I apologize, but I'm experiencing technical difficulties connecting to AI services. Please check your API configuration and try again later."
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return f"An error occurred while processing your request: {str(e)}"
    
    def _get_conversation_context(self, session_id: str, user_id: str, db: Session, limit: int = 10) -> List[AIConversation]:
        """Get recent conversation context"""
        try:
            return db.query(AIConversation).filter(
                AIConversation.session_id == session_id,
                AIConversation.user_id == user_id
            ).order_by(
                AIConversation.created_at.desc()
            ).limit(limit).all()[::-1]  # Reverse to get chronological order
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []
    
    def _get_system_context(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get current system context for AI"""
        try:
            # Get device information for this user
            devices = db.query(NetworkDevice).filter(NetworkDevice.owner_id == user_id).all()
            device_summary = []
            
            for device in devices:
                device_summary.append({
                    'name': device.name,
                    'ip': device.ip_address,
                    'model': device.model,
                    'status': device.status,
                    'uptime': device.uptime_formatted
                })
            
            # Get recent operations for this user
            recent_operations = db.query(OperationLog).filter(
                OperationLog.user_id == user_id
            ).order_by(
                OperationLog.created_at.desc()
            ).limit(5).all()
            
            operation_summary = []
            for op in recent_operations:
                operation_summary.append({
                    'type': op.operation_type,
                    'status': op.status,
                    'device': op.device.name if op.device else 'Unknown',
                    'timestamp': op.created_at.isoformat(),
                    'error': op.error_message
                })
            
            return {
                'devices': device_summary,
                'recent_operations': operation_summary,
                'total_devices': len(devices),
                'online_devices': len([d for d in devices if d.status == 'online'])
            }
        except Exception as e:
            logger.error(f"Error getting system context: {e}")
            return {'devices': [], 'recent_operations': [], 'total_devices': 0, 'online_devices': 0}
    
    def generate_configuration(self, config_type: str, parameters: Dict[str, Any]) -> str:
        """Generate network configuration using AI"""
        prompt = f"""Generate a Cisco IOS configuration for {config_type} with the following parameters:
        {json.dumps(parameters, indent=2)}
        
        Provide a complete, production-ready configuration with:
        1. Proper syntax and commands
        2. Security best practices
        3. Comments explaining key sections
        4. Error handling where applicable
        
        Format the response as a code block with proper indentation."""
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Cisco network engineer. Generate accurate, secure, and production-ready configurations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3  # Lower temperature for more consistent technical output
                )
                return response.choices[0].message.content
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are an expert Cisco network engineer. Generate accurate, secure, and production-ready configurations."
                )
                return response.content[0].text
            
            else:
                raise Exception("No AI service available")
                
        except Exception as e:
            logger.error(f"Configuration generation error: {e}")
            raise Exception(f"Failed to generate configuration: {str(e)}")
    
    async def generate_configuration_async(self, requirements: Dict[str, Any], device_type: str) -> str:
        """Asynchronous configuration generation using AI"""
        return self.generate_configuration("ai_generated", requirements)

    async def validate_configuration_async(self, config: str, device_type: str, validation_level: str) -> Dict[str, Any]:
        """Asynchronous configuration validation"""
        validation = self.validate_configuration(config, device_type)
        validation['level'] = validation_level
        return validation

    async def optimize_configuration(self, config: str, device_type: str, validation_result: Dict[str, Any]) -> str:
        """Asynchronous configuration optimization"""
        # Assume some optimization is performed based on validation
        if validation_result.get("valid", False):
            return config  # No optimization needed if valid

        # Placeholder for actual optimization logic
        optimized_config = config + "\n! Optimized Configuration\n"
        return optimized_config

    async def enhance_requirements(self, requirements: str, device_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance user requirements with AI analysis"""
        try:
            prompt = f"""Analyze and enhance these network requirements:
            
            Requirements: {requirements}
            Device Type: {device_type}
            Parameters: {json.dumps(params, indent=2)}
            
            Provide enhanced requirements with:
            1. Missing technical details
            2. Best practice recommendations
            3. Security considerations
            4. Implementation steps
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network design expert. Enhance user requirements with technical depth and best practices."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.4
                )
                
                return {
                    "original": requirements,
                    "enhanced": response.choices[0].message.content,
                    "device_type": device_type,
                    "parameters": params
                }
            
            # Fallback if no AI available
            return {
                "original": requirements,
                "enhanced": requirements,
                "device_type": device_type,
                "parameters": params
            }
        except Exception as e:
            logger.error(f"Requirements enhancement error: {e}")
            return {
                "original": requirements,
                "enhanced": requirements,
                "device_type": device_type,
                "parameters": params
            }

    def save_conversation(self, user_id: str, session_id: str, role: str, content: str, db: Session, metadata: Optional[Dict] = None) -> AIConversation:
        try:
            conversation = AIConversation(
                user_id=user_id,
                session_id=session_id,
                message_role=role,
                message_content=content,
                metadata=metadata
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            db.rollback()
            raise
    
    def validate_configuration(self, config_content: str, device_type: str = "ios") -> Dict[str, Any]:
        """Validate network configuration using AI"""
        prompt = f"""Analyze the following {device_type.upper()} configuration for:
        1. Syntax errors
        2. Security vulnerabilities
        3. Best practice violations
        4. Potential issues
        
        Configuration:
        ```
        {config_content}
        ```
        
        Provide a structured analysis with:
        - Overall status (valid/invalid/warning)
        - List of issues found
        - Recommendations for improvement
        - Risk level assessment
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network security expert. Analyze configurations thoroughly for errors, security issues, and best practices."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.2
                )
                
                # Parse response and structure it
                analysis_text = response.choices[0].message.content
                return {
                    'status': 'analyzed',
                    'analysis': analysis_text,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': 'AI validation service unavailable',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return {
                'status': 'error',
                'message': f'Validation failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_configuration_analysis(self, prompt: str) -> str:
        """Get AI analysis for configuration audit"""
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert Cisco network engineer and security analyst. Provide detailed, structured analysis of network configurations with specific findings, recommendations, and risk assessments."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.3
                )
                return response.choices[0].message.content
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are an expert Cisco network engineer and security analyst. Provide detailed, structured analysis of network configurations with specific findings, recommendations, and risk assessments."
                )
                return response.content[0].text
            
            else:
                return "AI configuration analysis service is currently unavailable. Please check your API configuration."
                
        except Exception as e:
            logger.error(f"Configuration analysis error: {e}")
            return f"Configuration analysis failed: {str(e)}"
    
    def analyze_troubleshooting_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered troubleshooting analysis"""
        try:
            prompt = f"""
            Analyze this network troubleshooting scenario and provide AI-powered diagnosis:
            
            Problem Description: {scenario_data.get('problem_description', '')}
            Problem Domain: {scenario_data.get('problem_domain', '')}
            Affected Devices: {scenario_data.get('affected_devices', [])}
            Symptoms: {scenario_data.get('symptoms', [])}
            
            Provide:
            1. Likely root causes (ranked by probability)
            2. Diagnostic steps to confirm the issue
            3. Resolution procedures
            4. Prevention recommendations
            5. Estimated resolution time
            
            Format the response as JSON with structured diagnostic information.
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a senior network engineer with expertise in Cisco technologies and network troubleshooting. Provide systematic, actionable troubleshooting guidance."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2000,
                    temperature=0.4
                )
                
                analysis_text = response.choices[0].message.content
                
                return {
                    'status': 'completed',
                    'analysis': analysis_text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are a senior network engineer with expertise in Cisco technologies and network troubleshooting. Provide systematic, actionable troubleshooting guidance."
                )
                
                return {
                    'status': 'completed',
                    'analysis': response.content[0].text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': 'AI troubleshooting service unavailable',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Troubleshooting analysis error: {e}")
            return {
                'status': 'error',
                'message': f'Troubleshooting analysis failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def generate_baseline_recommendations(self, devices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered baseline configuration recommendations"""
        try:
            prompt = f"""
            Analyze these network devices and generate baseline configuration recommendations:
            
            Devices: {json.dumps(devices_data, indent=2)}
            
            Generate:
            1. Golden configuration template
            2. Security hardening recommendations
            3. Performance optimization settings
            4. Compliance configuration (PCI-DSS, NIST)
            5. Monitoring and logging setup
            
            Format as structured JSON with separate sections for each recommendation category.
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a network architecture expert specializing in Cisco technologies. Generate comprehensive, production-ready baseline configurations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=2500,
                    temperature=0.3
                )
                
                return {
                    'status': 'completed',
                    'recommendations': response.choices[0].message.content,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2500,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    system="You are a network architecture expert specializing in Cisco technologies. Generate comprehensive, production-ready baseline configurations."
                )
                
                return {
                    'status': 'completed',
                    'recommendations': response.content[0].text,
                    'confidence': 'high',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    'status': 'error',
                    'message': 'AI baseline service unavailable',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"Baseline generation error: {e}")
            return {
                'status': 'error',
                'message': f'Baseline generation failed: {str(e)}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Global AI service instance
ai_service = AIService()
