"""
Business logic services for the phishing email generator
Separates business logic from API routes for better maintainability
"""

import uuid
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

import anthropic

from models import (
    PhishingRequest, EmailTemplate, GenerationResponse, 
    GenerationHistoryEntry, SystemStats, PhishingTacticInfo
)
from prompts import PhishingPrompts
from utils import (
    HTMLExtractor, EmailComponentExtractor, ContentAnalyzer,
    TemplateGenerator, ValidationHelper, PerformanceMonitor
)

logger = logging.getLogger(__name__)

class AnthropicService:
    """Service for handling Anthropic API interactions"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic service
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """
        Initialize Anthropic client with error handling
        
        Returns:
            True if successful
        """
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            
            # Test the connection
            test_response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use fast model for testing
                max_tokens=50,
                messages=[{"role": "user", "content": "Hello, respond with 'API Working'"}]
            )
            
            logger.info("✅ Anthropic client initialized and tested successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Anthropic client: {e}")
            self.client = None
            return False

    def is_available(self) -> bool:
        """Check if Anthropic service is available"""
        return self.client is not None

    async def generate_content(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate content using Claude
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated content
            
        Raises:
            Exception: If generation fails
        """
        if not self.client:
            raise Exception("Anthropic client not available")

        # Try multiple models for compatibility
        models_to_try = [
            "claude-3-haiku-20240307",      # Fastest
            "claude-3-sonnet-20240229",     # Balanced
            "claude-3-5-sonnet-20241022"    # Most capable
        ]
        
        last_error = None
        
        for model in models_to_try:
            try:
                logger.info(f"Attempting generation with model: {model}")
                
                message = self.client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = message.content[0].text
                logger.info(f"✅ Successfully generated with model: {model}")
                return response_text
                
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e
                continue
        
        # If all models failed
        raise Exception(f"All models failed. Last error: {last_error}")

class TemplateService:
    """Service for managing email templates"""
    
    def __init__(self):
        """Initialize template service"""
        self.templates: Dict[str, EmailTemplate] = {}
        self.generation_history: List[GenerationHistoryEntry] = []
        self.performance_monitor = PerformanceMonitor()

    def get_all_templates(self) -> List[EmailTemplate]:
        """Get all templates"""
        return list(self.templates.values())

    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def delete_template(self, template_id: str) -> bool:
        """Delete template by ID"""
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"Deleted template: {template_id}")
            return True
        return False

    def get_generation_history(self) -> List[Dict[str, Any]]:
        """Get generation history as dictionaries"""
        return [
            {
                "timestamp": entry.timestamp.isoformat(),
                "request": entry.request,
                "template_id": entry.template_id,
                "success": entry.success,
                "error": entry.error,
                "generation_time": entry.generation_time
            }
            for entry in self.generation_history
        ]

    def get_system_stats(self) -> SystemStats:
        """Get system statistics"""
        successful = sum(1 for entry in self.generation_history if entry.success)
        failed = len(self.generation_history) - successful
        
        # Calculate average generation time
        successful_times = [entry.generation_time for entry in self.generation_history if entry.success and entry.generation_time > 0]
        avg_time = sum(successful_times) / len(successful_times) if successful_times else 0.0
        
        # Popular scenarios and industries
        scenarios = Counter([entry.request.get('scenario_type', 'Unknown') for entry in self.generation_history])
        industries = Counter([entry.request.get('target_industry', 'Unknown') for entry in self.generation_history])
        
        # Available tactics
        tactics = {
            "credential_harvesting": {"name": "Credential Harvesting", "description": "Tricks users into entering login credentials"},
            "invoice_fraud": {"name": "Invoice Fraud", "description": "False billing requests"},
            "account_takeover": {"name": "Account Takeover", "description": "Claims of suspicious activity"},
            "prize_scam": {"name": "Prize/Lottery Scam", "description": "False prize notifications"},
            "tech_support": {"name": "Tech Support Scam", "description": "False technical issues"},
            "executive_impersonation": {"name": "Executive Impersonation", "description": "Impersonating executives"}
        }
        
        return SystemStats(
            total_templates=len(self.templates),
            successful_generations=successful,
            failed_generations=failed,
            average_generation_time=avg_time,
            popular_scenarios=dict(scenarios.most_common(10)),
            popular_industries=dict(industries.most_common(10)),
            supported_languages=["English", "Spanish", "French", "German", "Chinese", "Japanese"],
            available_tactics=tactics
        )

class PhishingGeneratorService:
    """Main service for generating phishing email templates"""
    
    def __init__(self, anthropic_service: AnthropicService, template_service: TemplateService):
        """
        Initialize phishing generator service
        
        Args:
            anthropic_service: Anthropic API service
            template_service: Template management service
        """
        self.anthropic_service = anthropic_service
        self.template_service = template_service
        self.html_extractor = HTMLExtractor()
        self.component_extractor = EmailComponentExtractor()
        self.content_analyzer = ContentAnalyzer()

    async def generate_template(self, request: PhishingRequest, client_ip: str = "unknown") -> GenerationResponse:
        """
        Generate a phishing email template
        
        Args:
            request: Generation request parameters
            client_ip: Client IP for logging
            
        Returns:
            Generation response with template or error
        """
        start_time = time.time()
        template_id = str(uuid.uuid4())
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Check if Anthropic service is available
            if not self.anthropic_service.is_available():
                return self._handle_fallback_generation(request, template_id, start_time)
            
            # Generate prompt
            prompt = self._create_prompt(request)
            
            # Generate content using Anthropic
            logger.info(f"Generating template for {request.scenario_type} - {request.target_industry}")
            response_text = await self.anthropic_service.generate_content(prompt)
            
            # Extract HTML content
            html_content = self.html_extractor.extract_html_from_response(response_text)
            
            if not html_content:
                logger.warning("Could not extract HTML, using fallback")
                return self._handle_fallback_generation(request, template_id, start_time)
            
            # Validate content safety
            is_safe, safety_issues = ValidationHelper.validate_html_safety(html_content)
            if not is_safe:
                logger.warning(f"Safety issues detected: {safety_issues}")
                # Continue but log the issues
            
            # Extract email components
            components = self.component_extractor.extract_email_components(html_content)
            
            # Create template
            generation_time = time.time() - start_time
            word_count = self.content_analyzer.calculate_word_count(html_content)
            
            template = EmailTemplate(
                id=template_id,
                subject=components["subject"],
                sender_name=components["sender_name"],
                sender_email=components["sender_email"],
                html_content=html_content,
                scenario_type=request.scenario_type.value,
                target_industry=request.target_industry.value,
                urgency_level=request.urgency_level.value,
                tone_style=request.tone_style.value,
                language=request.language.value,
                created_at=datetime.now(),
                phishing_tactic=request.phishing_tactic.value if request.phishing_tactic else None,
                advanced_mode=request.advanced_mode,
                generation_time=generation_time,
                word_count=word_count
            )
            
            # Store template
            self.template_service.templates[template_id] = template
            
            # Record success in history
            self._record_generation_history(request, template_id, True, None, generation_time)
            
            logger.info(f"✅ Successfully generated template {template_id} in {generation_time:.2f}s")
            return GenerationResponse(
                success=True, 
                template=template, 
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Failed to generate template: {str(e)}"
            logger.error(error_msg)
            
            # Record failure in history
            self._record_generation_history(request, None, False, error_msg, generation_time)
            
            return GenerationResponse(
                success=False, 
                error=error_msg, 
                generation_time=generation_time
            )

    def _validate_request(self, request: PhishingRequest) -> None:
        """Validate generation request"""
        # Basic validation - Pydantic handles most of this
        if not request.scenario_type or not request.target_industry:
            raise ValueError("Scenario type and target industry are required")

    def _create_prompt(self, request: PhishingRequest) -> str:
        """Create formatted prompt for generation"""
        # Determine phishing tactic
        tactic = request.phishing_tactic.value if request.phishing_tactic else "credential_harvesting"
        
        # Get prompt template
        template_type = "advanced" if request.advanced_mode else "base"
        
        prompt_params = {
            "language": request.language.value,
            "urgency_level": request.urgency_level.value,
            "tone_style": request.tone_style.value,
            "phishing_tactic": tactic.replace("_", " ").title(),
            "target_industry": request.target_industry.value,
            "scenario_type": request.scenario_type.value
        }
        
        return PhishingPrompts.get_prompt(template_type, **prompt_params)

    def _handle_fallback_generation(self, request: PhishingRequest, template_id: str, start_time: float) -> GenerationResponse:
        """Handle fallback template generation when AI fails"""
        try:
            logger.info("Using fallback template generation")
            
            # Create fallback template
            request_dict = {
                "scenario_type": request.scenario_type.value,
                "target_industry": request.target_industry.value,
                "urgency_level": request.urgency_level.value,
                "tone_style": request.tone_style.value
            }
            
            html_content = TemplateGenerator.create_fallback_template(request_dict)
            components = self.component_extractor.extract_email_components(html_content)
            
            generation_time = time.time() - start_time
            word_count = self.content_analyzer.calculate_word_count(html_content)
            
            template = EmailTemplate(
                id=template_id,
                subject=components["subject"],
                sender_name=components["sender_name"],
                sender_email=components["sender_email"],
                html_content=html_content,
                scenario_type=request.scenario_type.value,
                target_industry=request.target_industry.value,
                urgency_level=request.urgency_level.value,
                tone_style=request.tone_style.value,
                language=request.language.value,
                created_at=datetime.now(),
                phishing_tactic=request.phishing_tactic.value if request.phishing_tactic else None,
                advanced_mode=request.advanced_mode,
                generation_time=generation_time,
                word_count=word_count
            )
            
            # Store template
            self.template_service.templates[template_id] = template
            
            # Record success in history
            self._record_generation_history(request, template_id, True, None, generation_time)
            
            logger.info(f"✅ Generated fallback template {template_id}")
            return GenerationResponse(
                success=True, 
                template=template, 
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Fallback generation failed: {str(e)}"
            logger.error(error_msg)
            
            self._record_generation_history(request, None, False, error_msg, generation_time)
            
            return GenerationResponse(
                success=False, 
                error=error_msg, 
                generation_time=generation_time
            )

    def _record_generation_history(self, request: PhishingRequest, template_id: Optional[str], 
                                 success: bool, error: Optional[str], generation_time: float) -> None:
        """Record generation attempt in history"""
        history_entry = GenerationHistoryEntry(
            timestamp=datetime.now(),
            request=request.dict(),
            template_id=template_id,
            success=success,
            error=error,
            generation_time=generation_time
        )
        
        self.template_service.generation_history.append(history_entry)
        
        # Keep history limited to prevent memory issues
        max_history = 1000
        if len(self.template_service.generation_history) > max_history:
            self.template_service.generation_history = self.template_service.generation_history[-max_history:]

    async def regenerate_template(self, template_id: str) -> GenerationResponse:
        """
        Regenerate an existing template with the same parameters
        
        Args:
            template_id: ID of template to regenerate
            
        Returns:
            Generation response with new template or error
        """
        logger.info(f"Regenerate request for template: {template_id}")
        logger.info(f"Available templates: {list(self.template_service.templates.keys())}")
        
        # Get original template
        original_template = self.template_service.get_template(template_id)
        if not original_template:
            error_msg = f"Template {template_id} not found"
            logger.error(error_msg)
            return GenerationResponse(success=False, error=error_msg)
        
        logger.info(f"Found original template: {original_template.scenario_type}")
        
        # Create new request from original template
        try:
            from models import ScenarioType, TargetIndustry, UrgencyLevel, ToneStyle, Language, PhishingTactic
            
            request = PhishingRequest(
                scenario_type=ScenarioType(original_template.scenario_type),
                target_industry=TargetIndustry(original_template.target_industry),
                urgency_level=UrgencyLevel(original_template.urgency_level),
                tone_style=ToneStyle(original_template.tone_style),
                language=Language(original_template.language),
                phishing_tactic=PhishingTactic(original_template.phishing_tactic) if original_template.phishing_tactic else None,
                advanced_mode=original_template.advanced_mode
            )
            
            # Generate new template
            result = await self.generate_template(request)
            
            if result.success:
                logger.info(f"✅ Successfully regenerated template: {result.template.id}")
            else:
                logger.error(f"❌ Failed to regenerate template: {result.error}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error regenerating template: {str(e)}"
            logger.error(error_msg)
            return GenerationResponse(success=False, error=error_msg)

# Export services
__all__ = [
    "AnthropicService",
    "TemplateService", 
    "PhishingGeneratorService"
]