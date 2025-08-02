

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

# ==================== ENUMS ====================

class ScenarioType(str, Enum):
    """Available phishing scenarios"""
    PASSWORD_RESET = "Password Reset"
    INVOICE_OVERDUE = "Invoice Overdue"
    ACCOUNT_LOCK = "Account Lock"
    PRIZE_NOTIFICATION = "Prize Notification"
    URGENT_DOCUMENT_REVIEW = "Urgent Document Review"
    SECURITY_ALERT = "Security Alert"
    SYSTEM_MAINTENANCE = "System Maintenance"
    PAYMENT_FAILED = "Payment Failed"

class TargetIndustry(str, Enum):
    """Available target industries"""
    BANKING = "Banking"
    ONLINE_RETAIL = "Online Retail"
    CLOUD_SERVICE = "Cloud Service"
    SOCIAL_MEDIA = "Social Media"
    SHIPPING_COMPANY = "Shipping Company"
    HEALTHCARE = "Healthcare"
    GOVERNMENT = "Government"
    EDUCATION = "Education"
    TECHNOLOGY = "Technology"
    INSURANCE = "Insurance"
    RETAIL = "Retail"

class UrgencyLevel(str, Enum):
    """Urgency levels for phishing emails"""
    NORMAL = "Normal"
    HIGH = "High"

class ToneStyle(str, Enum):
    """Tone styles for phishing emails"""
    FORMAL = "Formal"
    CASUAL = "Casual"
    URGENT = "Urgent"
    INFORMATIVE = "Informative"

class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "English"
    SPANISH = "Spanish"
    FRENCH = "French"
    GERMAN = "German"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"

class PhishingTactic(str, Enum):
    """Available phishing tactics"""
    CREDENTIAL_HARVESTING = "credential_harvesting"
    INVOICE_FRAUD = "invoice_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    PRIZE_SCAM = "prize_scam"
    TECH_SUPPORT = "tech_support"
    EXECUTIVE_IMPERSONATION = "executive_impersonation"

# ==================== REQUEST MODELS ====================

class PhishingRequest(BaseModel):
    """Request model for generating phishing email templates"""
    scenario_type: ScenarioType = Field(..., description="Type of phishing scenario")
    target_industry: TargetIndustry = Field(..., description="Target industry or brand to mimic")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.NORMAL, description="Urgency level")
    tone_style: ToneStyle = Field(default=ToneStyle.FORMAL, description="Tone style")
    language: Language = Field(default=Language.ENGLISH, description="Language for the email")
    phishing_tactic: Optional[PhishingTactic] = Field(default=None, description="Specific phishing tactic")
    advanced_mode: bool = Field(default=False, description="Use advanced template generation")

# ==================== RESPONSE MODELS ====================

class EmailTemplate(BaseModel):
    """Email template model"""
    id: str
    subject: str
    sender_name: str
    sender_email: str
    html_content: str
    scenario_type: str
    target_industry: str
    urgency_level: str
    tone_style: str
    language: str
    created_at: datetime
    phishing_tactic: Optional[str] = None
    advanced_mode: bool = False
    generation_time: float = 0.0
    word_count: int = 0

class GenerationResponse(BaseModel):
    """Response model for template generation"""
    success: bool
    template: Optional[EmailTemplate] = None
    error: Optional[str] = None
    generation_time: float = 0.0

class DeleteResponse(BaseModel):
    """Response model for template deletion"""
    message: str
    deleted_id: str

# ==================== HISTORY & STATS MODELS ====================

class GenerationHistoryEntry(BaseModel):
    """Single generation history entry"""
    timestamp: datetime
    request: Dict[str, Any]
    template_id: Optional[str] = None
    success: bool
    error: Optional[str] = None
    generation_time: float = 0.0

class PhishingTacticInfo(BaseModel):
    """Information about a phishing tactic"""
    name: str
    description: str
    risk_level: str = "Medium"

class SystemStats(BaseModel):
    """System statistics and metrics"""
    total_templates: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    average_generation_time: float = 0.0
    popular_scenarios: Dict[str, int] = {}
    popular_industries: Dict[str, int] = {}
    supported_languages: List[str] = []
    available_tactics: Dict[str, PhishingTacticInfo] = {}

# ==================== HEALTH CHECK MODELS ====================

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    templates_count: int = 0
    anthropic_available: bool = False
    anthropic_client_initialized: bool = False
    api_key_configured: bool = False

class APITestResponse(BaseModel):
    """API test response model"""
    status: str
    anthropic_configured: bool = False
    claude_test_response: Optional[str] = None
    error: Optional[str] = None

# ==================== UTILITY FUNCTIONS ====================

def get_default_phishing_tactics() -> Dict[str, PhishingTacticInfo]:
    """Get default phishing tactics configuration"""
    return {
        "credential_harvesting": PhishingTacticInfo(
            name="Credential Harvesting",
            description="Tricks users into entering login credentials on fake websites",
            risk_level="High"
        ),
        "invoice_fraud": PhishingTacticInfo(
            name="Invoice Fraud",
            description="False billing or payment requests to steal money or information",
            risk_level="High"
        ),
        "account_takeover": PhishingTacticInfo(
            name="Account Takeover",
            description="Claims of suspicious account activity requiring verification",
            risk_level="Medium"
        ),
        "prize_scam": PhishingTacticInfo(
            name="Prize/Lottery Scam",
            description="False prize notifications to gather personal information",
            risk_level="Medium"
        ),
        "tech_support": PhishingTacticInfo(
            name="Tech Support Scam",
            description="False technical issues requiring immediate action",
            risk_level="Medium"
        ),
        "executive_impersonation": PhishingTacticInfo(
            name="Executive Impersonation",
            description="Impersonating company executives to request sensitive actions",
            risk_level="High"
        )
    }

# Export all models for easy importing
__all__ = [
    # Enums
    "ScenarioType", "TargetIndustry", "UrgencyLevel", "ToneStyle", 
    "Language", "PhishingTactic",
    
    # Request/Response Models
    "PhishingRequest", "EmailTemplate", "GenerationResponse", "DeleteResponse",
    
    # History & Stats
    "GenerationHistoryEntry", "PhishingTacticInfo", "SystemStats",
    
    # Health Check
    "HealthCheckResponse", "APITestResponse",
    
    # Utility Functions
    "get_default_phishing_tactics"
]