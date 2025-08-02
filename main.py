
import os
import logging
from typing import List
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import our modular components - NO DUPLICATION!
from models import (
    PhishingRequest, EmailTemplate, GenerationResponse, 
    HealthCheckResponse, APITestResponse, DeleteResponse
)
from services import AnthropicService, TemplateService, PhishingGeneratorService
from utils import FileManager, RateLimiter

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services (initialized in lifespan)
anthropic_service: AnthropicService = None
template_service: TemplateService = None
generator_service: PhishingGeneratorService = None
rate_limiter: RateLimiter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - NO BUSINESS LOGIC HERE"""
    logger.info("🚀 Starting Phishing Email Generator...")
    
    global anthropic_service, template_service, generator_service, rate_limiter
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY found in environment")
    
    # Create directories
    FileManager.ensure_directories("static", "templates", "output", "logs")
    
    # Initialize services (this is just orchestration, not business logic)
    anthropic_service = AnthropicService(api_key)
    template_service = TemplateService()
    generator_service = PhishingGeneratorService(anthropic_service, template_service)
    rate_limiter = RateLimiter(max_requests=10, time_window=60)
    
    logger.info(f"✅ Services initialized - Anthropic available: {anthropic_service.is_available()}")
    
    yield
    
    logger.info("👋 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Phishing Email Template Generator",
    description="AI-powered phishing email template generator for cybersecurity training",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency functions
def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def check_rate_limit(client_ip: str = Depends(get_client_ip)) -> str:
    """Check rate limit for client"""
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    return client_ip

# ==================== API ROUTES ONLY ====================
# No business logic here - just HTTP handling!

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface"""
    try:
        # Simple phishing tactics for template (could be moved to a config file)
        phishing_tactics = {
            "credential_harvesting": {
                "name": "Credential Harvesting",
                "description": "Tricks users into entering login credentials on fake websites"
            },
            "invoice_fraud": {
                "name": "Invoice Fraud", 
                "description": "False billing or payment requests to steal money or information"
            },
            "account_takeover": {
                "name": "Account Takeover",
                "description": "Claims of suspicious account activity requiring verification"
            },
            "prize_scam": {
                "name": "Prize/Lottery Scam",
                "description": "False prize notifications to gather personal information"
            },
            "tech_support": {
                "name": "Tech Support Scam",
                "description": "False technical issues requiring immediate action"
            },
            "executive_impersonation": {
                "name": "Executive Impersonation",
                "description": "Impersonating company executives to request sensitive actions"
            }
        }
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "phishing_tactics": phishing_tactics
        })
    except Exception as e:
        logger.error(f"Error serving home page: {e}")
        return HTMLResponse(
            content="<h1>Error</h1><p>Could not load home page.</p>", 
            status_code=500
        )

@app.post("/api/generate", response_model=GenerationResponse)
async def generate_email(
    request: PhishingRequest,
    client_ip: str = Depends(check_rate_limit)
):
    """Generate a new phishing email template - DELEGATE to service"""
    try:
        logger.info(f"Generation request from {client_ip}: {request.scenario_type} - {request.target_industry}")
        
        if not generator_service:
            raise HTTPException(status_code=503, detail="Generator service not available")
        
        # ALL business logic is in the service - this is just HTTP handling
        result = await generator_service.generate_template(request, client_ip)
        
        if result.success:
            logger.info(f"✅ Generated template {result.template.id}")
        else:
            logger.error(f"❌ Generation failed: {result.error}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_email: {str(e)}")
        return GenerationResponse(success=False, error=f"Unexpected error: {str(e)}")

@app.get("/api/templates", response_model=List[EmailTemplate])
async def get_templates():
    """Get all generated templates - DELEGATE to service"""
    try:
        if not template_service:
            raise HTTPException(status_code=503, detail="Template service not available")
        
        return template_service.get_all_templates()
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates/{template_id}", response_model=EmailTemplate)
async def get_template(template_id: str):
    """Get a specific template by ID - DELEGATE to service"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

@app.get("/api/templates/{template_id}/preview", response_class=HTMLResponse)
async def preview_template(template_id: str):
    """Preview a template as HTML - DELEGATE to service"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return HTMLResponse(content=template.html_content)

@app.get("/api/templates/{template_id}/download")
async def download_template(template_id: str):
    """Download template as .eml file - DELEGATE to service + utils"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        # Prepare data and use utility function - NO business logic here
        template_data = {
            "id": template.id,
            "sender_name": template.sender_name,
            "sender_email": template.sender_email,
            "subject": template.subject,
            "html_content": template.html_content
        }
        
        filepath = FileManager.save_template_as_eml(template_data)
        
        return FileResponse(
            path=filepath,
            filename=f"phishing_template_{template_id}.eml",
            media_type="message/rfc822"
        )
    except Exception as e:
        logger.error(f"Error creating download file: {e}")
        raise HTTPException(status_code=500, detail="Failed to create download file")

@app.get("/api/templates/{template_id}/download-html")
async def download_template_html(template_id: str):
    """Download template as .html file - DELEGATE to service + utils"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        # Use utility function for file operations
        template_data = {
            "id": template.id,
            "html_content": template.html_content
        }
        
        filepath = FileManager.save_template_as_html(template_data)
        
        return FileResponse(
            path=filepath,
            filename=f"phishing_template_{template_id}.html",
            media_type="text/html"
        )
    except Exception as e:
        logger.error(f"Error creating HTML download file: {e}")
        raise HTTPException(status_code=500, detail="Failed to create HTML download file")

@app.delete("/api/templates/{template_id}", response_model=DeleteResponse)
async def delete_template(template_id: str):
    """Delete a template - DELEGATE to service"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    if template_service.delete_template(template_id):
        return DeleteResponse(message="Template deleted successfully", deleted_id=template_id)
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@app.post("/api/regenerate/{template_id}", response_model=GenerationResponse)
async def regenerate_template(
    template_id: str,
    client_ip: str = Depends(check_rate_limit)
):
    """Regenerate a template - DELEGATE to service"""
    try:
        if not generator_service:
            raise HTTPException(status_code=503, detail="Generator service not available")
        
        result = await generator_service.regenerate_template(template_id)
        
        if result.success:
            logger.info(f"✅ Regenerated template: {result.template.id}")
        else:
            logger.error(f"❌ Regeneration failed: {result.error}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in regenerate: {str(e)}")
        return GenerationResponse(success=False, error=str(e))

@app.get("/api/tactics")
async def get_phishing_tactics():
    """Get available phishing tactics - COULD be moved to service"""
    return {
        "credential_harvesting": {
            "name": "Credential Harvesting",
            "description": "Tricks users into entering login credentials on fake websites",
            "risk_level": "High"
        },
        "invoice_fraud": {
            "name": "Invoice Fraud",
            "description": "False billing or payment requests to steal money or information",
            "risk_level": "High"
        },
        "account_takeover": {
            "name": "Account Takeover",
            "description": "Claims of suspicious account activity requiring verification",
            "risk_level": "Medium"
        },
        "prize_scam": {
            "name": "Prize/Lottery Scam",
            "description": "False prize notifications to gather personal information",
            "risk_level": "Medium"
        },
        "tech_support": {
            "name": "Tech Support Scam",
            "description": "False technical issues requiring immediate action",
            "risk_level": "Medium"
        },
        "executive_impersonation": {
            "name": "Executive Impersonation",
            "description": "Impersonating company executives to request sensitive actions",
            "risk_level": "High"
        }
    }

@app.get("/api/history")
async def get_generation_history():
    """Get generation history - DELEGATE to service"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    return template_service.get_generation_history()

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics - DELEGATE to service"""
    if not template_service:
        raise HTTPException(status_code=503, detail="Template service not available")
    
    return template_service.get_system_stats()

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint - minimal logic"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        templates_count=len(template_service.templates) if template_service else 0,
        anthropic_available=anthropic_service.is_available() if anthropic_service else False,
        anthropic_client_initialized=anthropic_service is not None,
        api_key_configured=bool(os.getenv("ANTHROPIC_API_KEY"))
    )

@app.get("/api/test", response_model=APITestResponse)
async def test_anthropic():
    """Test Anthropic connection - DELEGATE to service"""
    if not anthropic_service:
        return APITestResponse(
            status="error",
            anthropic_configured=False,
            error="Anthropic service not initialized"
        )
    
    if not anthropic_service.is_available():
        return APITestResponse(
            status="error",
            anthropic_configured=False,
            error="Anthropic client not available"
        )
    
    try:
        response = await anthropic_service.generate_content(
            "Say 'API Test Successful'", 
            max_tokens=50
        )
        
        return APITestResponse(
            status="success",
            anthropic_configured=True,
            claude_test_response=response[:100]
        )
    except Exception as e:
        return APITestResponse(
            status="error",
            anthropic_configured=True,
            error=str(e)
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": request.url.path}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Phishing Email Generator...")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )