

import re
import time
import logging
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class HTMLExtractor:
    """Utility class for extracting HTML content from responses"""
    
    @staticmethod
    def extract_html_from_response(text: str) -> Optional[str]:
        """
        Extract HTML content from Claude's response with multiple fallback methods
        
        Args:
            text: Raw response text from Claude
            
        Returns:
            Extracted HTML content or None if not found
        """
        try:
            # Method 1: Standard code block patterns
            patterns = [
                r"```html\n(.*?)\n```",
                r"```html(.*?)```",
                r"```\n(<!DOCTYPE.*?</html>)\n```",
                r"```(<!DOCTYPE.*?</html>)```"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    return match.group(1).strip()
            
            # Method 2: Direct HTML detection
            if "<!DOCTYPE" in text or "<html" in text.lower():
                # Find DOCTYPE or html tag
                start_markers = ["<!DOCTYPE", "<html", "<HTML"]
                end_markers = ["</html>", "</HTML>"]
                
                start_pos = -1
                for marker in start_markers:
                    pos = text.find(marker)
                    if pos != -1 and (start_pos == -1 or pos < start_pos):
                        start_pos = pos
                
                if start_pos != -1:
                    end_pos = -1
                    for marker in end_markers:
                        pos = text.rfind(marker)
                        if pos != -1:
                            end_pos = pos + len(marker)
                            break
                    
                    if end_pos != -1:
                        return text[start_pos:end_pos].strip()
            
            logger.warning("Could not extract HTML from response")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting HTML: {e}")
            return None

class EmailComponentExtractor:
    """Utility class for extracting email components from HTML"""
    
    @staticmethod
    def extract_email_components(html_content: str) -> Dict[str, str]:
        """
        Extract email components with enhanced parsing for realistic sender info
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Dictionary with extracted components
        """
        components = {
            "subject": "Generated Phishing Email",
            "sender_name": "Security Team",
            "sender_email": "security@example.com"
        }
        
        try:
            # Extract subject from multiple sources
            subject_patterns = [
                r"<title[^>]*>(.*?)</title>",
                r"<!--\s*Subject:\s*([^-]+)\s*-->",
                r"<meta\s+name=['\"]subject['\"][^>]*content=['\"]([^'\"]+)['\"]"
            ]
            
            for pattern in subject_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                if match:
                    subject = match.group(1).strip()
                    subject = re.sub(r'<[^>]+>', '', subject)
                    components["subject"] = subject[:100]
                    break
            
            # Enhanced sender info extraction patterns
            sender_patterns = [
                r"<!--\s*From:\s*([^<]+)\s*<([^>]+)>\s*-->",
                r"<!--\s*Sender:\s*([^<]+)\s*<([^>]+)>\s*-->",
                r"<!--\s*From:\s*([^<]+)<([^>]+)>\s*-->",  # Without space before <
                r"From:\s*([^<]+)\s*<([^>]+)>",  # In content
            ]
            
            for pattern in sender_patterns:
                match = re.search(pattern, html_content)
                if match:
                    components["sender_name"] = match.group(1).strip()
                    components["sender_email"] = match.group(2).strip()
                    logger.info(f"Extracted sender: {components['sender_name']} <{components['sender_email']}>")
                    break
            
            # If no sender found, generate a realistic one based on content
            if components["sender_email"] == "security@example.com":
                components = EmailComponentExtractor._generate_realistic_sender(html_content, components)
            
            return components
            
        except Exception as e:
            logger.error(f"Error extracting email components: {e}")
            return components

    @staticmethod
    def _generate_realistic_sender(html_content: str, components: Dict[str, str]) -> Dict[str, str]:
        """
        Generate realistic sender info if not found in HTML
        
        Args:
            html_content: HTML content to analyze
            components: Current components dictionary
            
        Returns:
            Updated components with realistic sender info
        """
        try:
            # Detect industry from content
            content_lower = html_content.lower()
            
            industry_mappings = [
                (['bank', 'account', 'financial', 'credit'], "Security Department", "security@fake-firstnational-bank.com"),
                (['health', 'medical', 'patient', 'clinic'], "Patient Services", "admin@fake-healthsystems.org"),
                (['order', 'shipping', 'delivery', 'purchase'], "Customer Service", "orders@fake-retailservices.com"),
                (['microsoft', 'google', 'tech', 'software', 'cloud'], "Account Security", "noreply@fake-techsupport.com"),
                (['government', 'irs', 'tax', 'official'], "Official Notice", "notifications@fake-government-alerts.gov"),
                (['education', 'university', 'student', 'academic'], "IT Services", "support@fake-university-systems.edu"),
                (['insurance', 'policy', 'claim', 'premium'], "Claims Department", "claims@fake-insurance-services.com")
            ]
            
            for keywords, name, email in industry_mappings:
                if any(word in content_lower for word in keywords):
                    components["sender_name"] = name
                    components["sender_email"] = email
                    break
            else:
                # Generic professional sender
                components["sender_name"] = "Support Team"
                components["sender_email"] = "support@fake-secureservices.net"
            
            logger.info(f"Generated realistic sender: {components['sender_name']} <{components['sender_email']}>")
            return components
            
        except Exception as e:
            logger.error(f"Error generating realistic sender: {e}")
            return components

class ContentAnalyzer:
    """Utility class for analyzing email content"""
    
    @staticmethod
    def calculate_word_count(html_content: str) -> int:
        """
        Calculate word count from HTML content
        
        Args:
            html_content: HTML content
            
        Returns:
            Word count
        """
        try:
            # Remove HTML tags and count words
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            words = text.split()
            return len(words)
        except:
            return 0

    @staticmethod
    def analyze_phishing_indicators(html_content: str) -> Dict[str, int]:
        """
        Analyze content for phishing indicators
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dictionary with indicator counts
        """
        indicators = {
            'urgency_words': 0,
            'suspicious_links': 0,
            'authority_claims': 0,
            'scarcity_language': 0
        }
        
        try:
            content_lower = html_content.lower()
            
            # Urgency indicators
            urgency_words = ['urgent', 'immediate', 'asap', 'expires', 'deadline', 'limited time']
            indicators['urgency_words'] = sum(1 for word in urgency_words if word in content_lower)
            
            # Suspicious links (non-https, suspicious domains)
            link_pattern = r'href=["\']([^"\']+)["\']'
            links = re.findall(link_pattern, html_content, re.IGNORECASE)
            indicators['suspicious_links'] = len([link for link in links if 'fake-' in link or 'phishing-' in link])
            
            # Authority claims
            authority_words = ['security', 'official', 'verify', 'confirm', 'validate']
            indicators['authority_claims'] = sum(1 for word in authority_words if word in content_lower)
            
            # Scarcity language
            scarcity_words = ['limited', 'exclusive', 'only', 'last chance', 'expires']
            indicators['scarcity_language'] = sum(1 for word in scarcity_words if word in content_lower)
            
        except Exception as e:
            logger.error(f"Error analyzing phishing indicators: {e}")
        
        return indicators

class FileManager:
    """Utility class for file operations"""
    
    @staticmethod
    def ensure_directories(*dirs: str) -> None:
        """
        Ensure directories exist, create if they don't
        
        Args:
            *dirs: Directory paths to ensure
        """
        for directory in dirs:
            Path(directory).mkdir(exist_ok=True, parents=True)

    @staticmethod
    def save_template_as_eml(template_data: Dict[str, str], output_dir: str = "output") -> str:
        """
        Save template as .eml file
        
        Args:
            template_data: Template data with required fields
            output_dir: Output directory
            
        Returns:
            File path of saved template
        """
        try:
            FileManager.ensure_directories(output_dir)
            
            eml_content = f"""From: {template_data['sender_name']} <{template_data['sender_email']}>
Subject: {template_data['subject']}
Content-Type: text/html; charset=utf-8
MIME-Version: 1.0

{template_data['html_content']}
"""
            
            filename = f"phishing_template_{template_data['id']}.eml"
            filepath = Path(output_dir) / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(eml_content)
            
            logger.info(f"Saved template as {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving template as EML: {e}")
            raise

class RateLimiter:
    """Simple rate limiting utility"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}

    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if request is allowed
        """
        now = time.time()
        window_start = now - self.time_window
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id] 
                if req_time > window_start
            ]
        else:
            self.requests[client_id] = []
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append(now)
        return True

class TemplateGenerator:
    """Utility class for generating fallback templates"""
    
    @staticmethod
    def create_fallback_template(request_data: Dict[str, str]) -> str:
        """
        Create a simple fallback template if AI generation fails
        
        Args:
            request_data: Request parameters
            
        Returns:
            HTML template string
        """
        from prompts import PhishingPrompts
        
        # Generate realistic sender info based on industry
        sender_name, sender_email = PhishingPrompts.get_fallback_sender_info(
            request_data.get('target_industry', 'Technology')
        )
        
        scenario_type = request_data.get('scenario_type', 'Security Alert')
        target_industry = request_data.get('target_industry', 'Technology')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urgent: {scenario_type} Required</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
            line-height: 1.6;
        }}
        .container {{ 
            max-width: 600px; 
            margin: 0 auto; 
            background: white; 
            padding: 0; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{ 
            background: linear-gradient(135deg, #1f4e79 0%, #2c5aa0 100%); 
            color: white; 
            padding: 20px; 
            text-align: center; 
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            padding: 30px;
        }}
        .alert-box {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .button {{ 
            display: inline-block;
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); 
            color: white; 
            padding: 14px 28px; 
            text-decoration: none; 
            border-radius: 6px; 
            font-weight: bold;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        .button:hover {{
            background: linear-gradient(135deg, #c82333 0%, #a71e2a 100%);
            transform: translateY(-2px);
        }}
        .footer {{ 
            background-color: #f8f9fa;
            padding: 20px; 
            text-align: center; 
            font-size: 12px; 
            color: #6c757d;
            border-radius: 0 0 8px 8px;
            border-top: 1px solid #dee2e6;
        }}
        .urgent {{
            color: #dc3545;
            font-weight: bold;
        }}
        .company-logo {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
    </style>
</head>
<body>
    <!-- From: {sender_name} <{sender_email}> -->
    <!-- For training only – not a real phishing email -->
    
    <div class="container">
        <div class="header">
            <div class="company-logo">{target_industry}</div>
            <p>Security & Compliance Department</p>
        </div>
        
        <div class="content">
            <h2 class="urgent">⚠️ Urgent: {scenario_type} Required</h2>
            
            <p>Dear Valued Customer,</p>
            
            <p>We have detected unusual activity on your account that requires immediate verification. 
            To protect your account security and maintain compliance with our security policies, 
            please take action within the next <strong>24 hours</strong>.</p>
            
            <div class="alert-box">
                <strong>🔒 Security Notice:</strong> Your account access has been temporarily restricted 
                due to suspicious activity detected from an unrecognized device.
            </div>
            
            <p><strong>Action Required:</strong> Click the button below to verify your account information 
            and restore full access to your services.</p>
            
            <div style="text-align: center;">
                <a href="http://fake-{target_industry.lower().replace(' ', '')}-verification.com/verify" class="button">
                    🔐 Verify Account Now
                </a>
            </div>
            
            <p><strong class="urgent">Important:</strong> If you do not complete this verification 
            within 24 hours, your account may be permanently suspended for security reasons.</p>
            
            <p>This verification process is mandatory and must be completed to ensure the safety 
            of your personal information and account assets.</p>
            
            <p>Thank you for your immediate attention to this critical security matter.</p>
            
            <p>Best regards,<br>
            <strong>{sender_name}</strong><br>
            {target_industry} Security Team</p>
        </div>
        
        <div class="footer">
            <p>This is an automated security message. Please do not reply to this email.</p>
            <p>{target_industry} | Security Department | Compliance Division</p>
            <p>© 2024 {target_industry}. All rights reserved.</p>
            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 15px 0;">
            <p><em><strong>Training Notice:</strong> This is a simulated phishing email for cybersecurity training purposes only.</em></p>
        </div>
    </div>
</body>
</html>"""

class ValidationHelper:
    """Utility class for validation functions"""
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid format
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return bool(re.match(pattern, email))

    @staticmethod
    def sanitize_input(text: str, max_length: int = 500) -> str:
        """
        Sanitize user input
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters that could be problematic
        text = re.sub(r'[<>&"\']', '', text)
        
        # Limit length
        text = text[:max_length]
        
        return text.strip()

    @staticmethod
    def validate_html_safety(html_content: str) -> Tuple[bool, List[str]]:
        """
        Validate HTML content for safety (training purposes)
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        
        # Check for training disclaimer
        if "For training only" not in html_content:
            issues.append("Missing training disclaimer")
        
        # Check for fake URLs
        url_pattern = r'href=["\']([^"\']+)["\']'
        urls = re.findall(url_pattern, html_content, re.IGNORECASE)
        real_domains = [url for url in urls if not any(fake in url.lower() for fake in ['fake-', 'phishing-', 'test-', 'training-'])]
        
        if real_domains:
            issues.append(f"Contains potentially real URLs: {real_domains}")
        
        # Check for real company names (basic check)
        real_companies = ['microsoft.com', 'google.com', 'amazon.com', 'apple.com', 'facebook.com']
        for company in real_companies:
            if company in html_content.lower():
                issues.append(f"Contains reference to real company: {company}")
        
        return len(issues) == 0, issues

class PerformanceMonitor:
    """Utility class for performance monitoring"""
    
    def __init__(self):
        self.metrics = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation"""
        self.metrics[operation] = {'start': time.time()}

    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.metrics and 'start' in self.metrics[operation]:
            duration = time.time() - self.metrics[operation]['start']
            self.metrics[operation]['duration'] = duration
            return duration
        return 0.0

    def get_metrics(self) -> Dict[str, float]:
        """Get all recorded metrics"""
        return {op: data.get('duration', 0.0) for op, data in self.metrics.items()}

# Export utility classes
__all__ = [
    "HTMLExtractor",
    "EmailComponentExtractor", 
    "ContentAnalyzer",
    "FileManager",
    "RateLimiter",
    "TemplateGenerator",
    "ValidationHelper",
    "PerformanceMonitor"
]