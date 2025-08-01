from crewai import Agent, Task, Crew
from .llm_manager import llm_manager

class NetworkAutomationCrew:
    """Manages the crew of AI agents for network automation tasks."""
    def __init__(self):
        # Use the globally managed LLM provider
        self.llm = llm_manager.current_provider

        # Define Agents
        self.config_generator = Agent(
            role='Network Configuration Generator',
            goal='Generate technically accurate and complete network configurations based on given requirements.',
            backstory='An expert in Cisco IOS, IOS-XE, and IOS-XR network device configurations with a deep understanding of routing, switching, and security best practices.',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        self.config_validator = Agent(
            role='Configuration Validator',
            goal='Validate network configurations for syntax errors, security vulnerabilities, and adherence to best practices.',
            backstory='A meticulous network engineer who specializes in auditing configurations to ensure they are secure, efficient, and compliant with network policies.',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

        # In a real-world scenario, this agent would have tools to connect to devices.
        self.config_deployer = Agent(
            role='Configuration Deployer',
            goal='Deploy validated configurations to network devices safely and efficiently.',
            backstory='A seasoned network operations specialist with expertise in deploying changes to live environments with minimal disruption, using pre-check and post-check validations.',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def generate_and_validate_config(self, requirements: str, device_type: str):
        """Creates and runs a crew to generate and validate a configuration."""

        # Define Tasks
        generate_task = Task(
            description=f"Generate a complete Cisco {device_type} configuration based on the following requirements: {requirements}",
            agent=self.config_generator,
            expected_output=f"A complete, ready-to-use Cisco {device_type} configuration script."
        )

        validate_task = Task(
            description="Validate the generated configuration for correctness, security, and best practices. Provide a report of findings and the final, validated configuration.",
            agent=self.config_validator,
            expected_output="A JSON object with two keys: 'validation_report' (a string detailing the findings) and 'validated_config' (the final configuration script).",
            context=[generate_task]
        )

        # Assemble and run the crew
        config_crew = Crew(
            agents=[self.config_generator, self.config_validator],
            tasks=[generate_task, validate_task],
            verbose=2
        )

        result = config_crew.kickoff()
        return result
