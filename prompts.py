
class PhishingPrompts:
    """Collection of prompts for different phishing scenarios"""
    
    BASE_TEMPLATE = """
As an AI specializing in cybersecurity education, generate a realistic HTML-formatted phishing email template for training purposes only. This will be used on a cybersecurity platform to help users identify and avoid phishing attacks.

**Template Requirements:**

1. **HTML Format:** Complete HTML document with professional styling, enclosed in ```html ... ```
2. **Language:** Generate content in {language}
3. **Core Content:**
   - **Subject Line:** Compelling subject that creates {urgency_level} urgency or curiosity
   - **Greeting:** Appropriate greeting for {language} and {tone_style} tone
   - **Body:** Realistic text explaining a problem or opportunity, using {phishing_tactic} tactics
   - **Call-to-Action:** Prominent button/link with fake URL
   - **Realistic Sender Information:** Create a believable sender name and email that looks professional for {target_industry}
     * Use realistic but fake names (e.g., "Sarah Johnson", "Michael Chen", "Robert Anderson")
     * Create professional-looking email addresses that mimic real {target_industry} patterns:
       - Banking: security@fake-firstnational-bank.com, alerts@fake-bankofamerica-security.com
       - Healthcare: admin@fake-healthpartners.org, support@fake-medicalsystems.net
       - Technology: noreply@fake-microsoft-security.com, alerts@fake-google-accounts.com
       - Retail: orders@fake-amazon-fulfillment.com, service@fake-walmart-customer.com
     * Make the sender email look legitimate but clearly fake for training
   - **Footer:** Standard email footer with disclaimer

4. **Visual Authenticity:**
   - Mimic {target_industry} email styling and branding colors
   - Professional appearance with CSS styling that matches industry standards
   - NO actual logos or copyrighted images
   - Focus on layout, fonts, and colors typical of {target_industry}

5. **Phishing Tactics for {phishing_tactic}:**
   - Use {urgency_level} urgency/scarcity language
   - Impersonate {target_industry} authority convincingly
   - Include curiosity/greed elements appropriate to scenario
   - Use realistic terminology and processes from {target_industry}

6. **Safety Constraints:**
   - Use ONLY fake URLs that clearly indicate they're fake (e.g., http://fake-{target_industry}-portal.com, https://phishing-test-{target_industry}.edu)
   - Include training disclaimer: <!-- For training only – not a real phishing email -->
   - No live links or real domain names
   - Clear visual indicators this is for training
   - Sender email must be obviously fake but realistic-looking

7. **Sender Email Examples by Industry:**
   - Banking: security@fake-chase-alerts.com, noreply@fake-wellsfargo-security.net
   - Healthcare: admin@fake-healthsystem.org, billing@fake-medicalbilling.com
   - Retail: orders@fake-ecommerce-orders.com, service@fake-retailsupport.net
   - Technology: security@fake-techsupport.com, alerts@fake-cloudsecurity.org
   - Government: notifications@fake-government-alerts.gov, admin@fake-irs-notices.gov

**Scenario Details:**
- Scenario Type: {scenario_type}
- Target Industry: {target_industry}  
- Urgency Level: {urgency_level}
- Tone Style: {tone_style}
- Language: {language}
- Phishing Tactic: {phishing_tactic}

Generate a complete, realistic HTML email template with a professional-looking but clearly fake sender email that would effectively test users' ability to identify phishing attempts while maintaining ethical training standards.

IMPORTANT: Include the sender information in an HTML comment at the top like this:
<!-- From: [Realistic Name] <[realistic-fake-email]> -->
"""

    ADVANCED_TEMPLATE = """
As an expert cybersecurity trainer, create an advanced phishing email template with sophisticated social engineering elements. This is for advanced cybersecurity training where participants need to identify subtle manipulation tactics.

**Enhanced Requirements:**
- Include multiple persuasion techniques (authority, urgency, social proof)
- Use advanced social engineering psychology
- Implement sophisticated visual design matching {target_industry} standards
- Include realistic but fake contact information and branding
- Add urgency indicators and scarcity elements
- Use industry-specific terminology and processes
- Create believable but fake sender credentials

**Scenario Context:**
- Target Sophistication Level: Advanced
- Training Scenario: {scenario_type}
- Industry Context: {target_industry}
- Psychological Triggers: {urgency_level} urgency, authority, social proof
- Communication Style: {tone_style}
- Cultural Context: {language}
- Primary Tactic: {phishing_tactic}

Create an email that would challenge experienced users while remaining clearly educational and safe for training purposes.

Follow the same HTML format and safety constraints as the base template.
"""

    INDUSTRY_SPECIFIC_PROMPTS = {
        "Banking": """
Focus on financial security concerns, account verification, and transaction alerts.
Use banking terminology, reference specific account types, and include realistic
transaction details. Mimic bank email layouts with professional styling.
""",
        
        "Healthcare": """
Emphasize patient privacy, HIPAA compliance, and medical record security.
Use healthcare terminology, reference medical systems, and include realistic
appointment or billing scenarios. Match healthcare provider email formats.
""",
        
        "Technology": """
Focus on software updates, security patches, and account compromises.
Use technical terminology, reference popular software/services, and include
realistic system alerts. Mimic tech company email designs.
""",
        
        "Government": """
Emphasize official procedures, compliance requirements, and deadlines.
Use formal government language, reference agencies and regulations.
Include realistic official communication formats.
""",
        
        "Education": """
Focus on student services, academic deadlines, and institutional communications.
Use educational terminology, reference campus systems and services.
Match university/school email formatting standards.
"""
    }

    @classmethod
    def get_prompt(cls, template_type: str = "base", **kwargs) -> str:
        """
        Get formatted prompt based on template type and parameters
        
        Args:
            template_type: Type of prompt template ("base", "advanced")
            **kwargs: Template formatting parameters
            
        Returns:
            Formatted prompt string
        """
        if template_type == "advanced":
            base_prompt = cls.ADVANCED_TEMPLATE
        else:
            base_prompt = cls.BASE_TEMPLATE
        
        # Add industry-specific guidance if available
        industry = kwargs.get('target_industry', '')
        if industry in cls.INDUSTRY_SPECIFIC_PROMPTS:
            industry_guidance = f"\n\n**Industry-Specific Guidance for {industry}:**\n"
            industry_guidance += cls.INDUSTRY_SPECIFIC_PROMPTS[industry]
            base_prompt += industry_guidance
        
        # Format the prompt with provided parameters
        try:
            return base_prompt.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt formatting: {e}")

    @classmethod
    def get_fallback_sender_info(cls, industry: str) -> tuple:
        """
        Get realistic sender information for fallback templates
        
        Args:
            industry: Target industry
            
        Returns:
            Tuple of (sender_name, sender_email)
        """
        industry_senders = {
            "Banking": ("Security Department", "security@fake-firstnational-alerts.com"),
            "Healthcare": ("Patient Services", "admin@fake-healthpartners.org"),
            "Online Retail": ("Customer Service", "orders@fake-ecommerce-orders.com"),
            "Technology": ("Account Security", "noreply@fake-techsupport.com"),
            "Government": ("Official Notice", "notifications@fake-government-alerts.gov"),
            "Education": ("IT Services", "support@fake-university-systems.edu"),
            "Insurance": ("Claims Department", "claims@fake-insurance-services.com"),
            "Retail": ("Customer Support", "service@fake-retailsupport.net"),
            "Cloud Service": ("Security Team", "alerts@fake-cloudsecurity.org"),
            "Social Media": ("Account Safety", "security@fake-socialmedia.com"),
            "Shipping Company": ("Delivery Notice", "tracking@fake-shipping.com")
        }
        
        return industry_senders.get(
            industry, 
            ("Support Team", "support@fake-secureservices.net")
        )

    @classmethod
    def validate_parameters(cls, params: dict) -> bool:
        """
        Validate that all required parameters are present
        
        Args:
            params: Dictionary of parameters
            
        Returns:
            True if all required parameters present
        """
        required_params = [
            'language', 'urgency_level', 'tone_style', 'phishing_tactic',
            'target_industry', 'scenario_type'
        ]
        
        missing_params = [param for param in required_params if param not in params]
        
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        return True