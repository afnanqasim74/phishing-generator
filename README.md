# Phishing Email Template Generator

A sophisticated AI-powered phishing email template generator designed for cybersecurity training and awareness programs. This tool helps security professionals create realistic phishing email templates to test and train users on identifying phishing attempts.

## 🛡️ Purpose

This application generates realistic but clearly fake phishing email templates for:
- **Cybersecurity Training**: Educational purposes to help users identify phishing attempts
- **Security Awareness Programs**: Training employees to recognize social engineering tactics
- **Penetration Testing**: Creating controlled phishing scenarios for security assessments
- **Research & Education**: Understanding phishing tactics and attack vectors

## ⚠️ Important Disclaimer

**FOR EDUCATIONAL AND TRAINING PURPOSES ONLY**

This tool is designed exclusively for legitimate cybersecurity training, education, and authorized security testing. All generated templates include clear indicators that they are for training purposes and use obviously fake URLs and sender information.

## 🚀 Features

### Core Functionality
- **AI-Powered Generation**: Uses Claude AI to create realistic phishing email templates
- **Multiple Scenarios**: Supports various phishing scenarios (password reset, invoice fraud, account lockout, etc.)
- **Industry Targeting**: Templates can mimic different industries (banking, healthcare, retail, etc.)
- **Customizable Parameters**: Adjust urgency level, tone, language, and phishing tactics
- **Safety-First Design**: All templates include training disclaimers and fake URLs

### Advanced Features
- **Real-time Preview**: Live preview of generated email templates
- **Template Library**: Store and manage generated templates
- **Multiple Export Formats**: Download as .eml or .html files
- **Generation History**: Track all generation attempts and parameters
- **Fallback Templates**: Backup template generation when AI is unavailable
- **Rate Limiting**: Prevents abuse with built-in rate limiting
- **Performance Monitoring**: Track generation times and system performance

### Phishing Tactics Supported
- **Credential Harvesting**: Tricks users into entering login credentials
- **Invoice Fraud**: False billing or payment requests
- **Account Takeover**: Claims of suspicious account activity
- **Prize/Lottery Scams**: False prize notifications
- **Tech Support Scams**: False technical issues requiring action
- **Executive Impersonation**: Impersonating company executives

## 🏗️ Architecture

### Backend Components
- **FastAPI**: Modern Python web framework for the API
- **Anthropic Claude**: AI model for generating realistic email content
- **Modular Services**: Separated business logic for maintainability
- **Template Management**: In-memory storage with persistence options

### Frontend Components
- **Alpine.js**: Lightweight JavaScript framework for interactivity
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Responsive Design**: Works on desktop and mobile devices

### File Structure
```
phishing-generator/
├── main.py                 # Main FastAPI application
├── models.py              # Data models and Pydantic schemas
├── services.py            # Business logic services
├── prompts.py             # AI prompt templates
├── utils.py               # Utility functions and helpers
├── templates/
│   └── index.html         # Frontend interface
├── static/                # Static assets
├── output/                # Generated template downloads
└── .env                   # Environment variables
```

## 📋 Prerequisites

- Python 3.8 or higher
- Anthropic API key (Claude AI access)
- Modern web browser
- 2GB+ RAM recommended

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd phishing-generator
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 5. Create Required Directories
```bash
mkdir static templates output logs
```

## 🚀 Running the Application

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Generate Template
```http
POST /api/generate
Content-Type: application/json

{
  "scenario_type": "Password Reset",
  "target_industry": "Banking",
  "urgency_level": "High",
  "tone_style": "Formal",
  "language": "English",
  "phishing_tactic": "credential_harvesting"
}
```

#### Get All Templates
```http
GET /api/templates
```

#### Download Template
```http
GET /api/templates/{template_id}/download
```

#### Health Check
```http
GET /health
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude AI API key | Required |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_REQUESTS_PER_MINUTE` | Rate limit | `10` |

### Supported Parameters

#### Scenario Types
- Password Reset
- Invoice Overdue
- Account Lock
- Prize Notification
- Urgent Document Review
- Security Alert
- System Maintenance
- Payment Failed

#### Target Industries
- Banking
- Online Retail
- Cloud Service
- Social Media
- Shipping Company
- Healthcare
- Government
- Education
- Technology

#### Urgency Levels
- Normal
- High

#### Tone Styles
- Formal
- Casual
- Urgent
- Informative

#### Languages
- English
- Spanish
- French
- German
- Chinese
- Japanese

## 🔒 Security Features

### Safety Measures
- **Fake URLs Only**: All generated links use obviously fake domains
- **Training Disclaimers**: Every template includes training notices
- **Content Validation**: Automatic checks for real company references
- **Rate Limiting**: Prevents abuse and overuse
- **Input Sanitization**: All user inputs are sanitized and validated

### Best Practices
- Never use generated templates for actual phishing attacks
- Always include training context when using templates
- Regularly review generated content for appropriateness
- Maintain logs for audit and compliance purposes

## 🧪 Testing

### Manual Testing
1. Access the web interface at `http://localhost:8000`
2. Fill out the generation form with test parameters
3. Verify template generation and preview functionality
4. Test download features (.eml and .html formats)
5. Check template library and history features

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test template generation
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"scenario_type":"Security Alert","target_industry":"Banking","urgency_level":"High","tone_style":"Formal","language":"English"}'
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Anthropic API Errors
- **Problem**: `API key not configured` or `Anthropic client not available`
- **Solution**: Check your `.env` file and ensure `ANTHROPIC_API_KEY` is set correctly

#### 2. Template Generation Fails
- **Problem**: Generation returns error or empty content
- **Solution**: Check API key validity and try with different parameters. Fallback templates will be used if AI fails.

#### 3. Downloads Not Working
- **Problem**: Download buttons don't work or files are corrupted
- **Solution**: Ensure the `output` directory exists and has write permissions

#### 4. Frontend Not Loading
- **Problem**: Blank page or JavaScript errors
- **Solution**: Check that `templates/index.html` exists and CDN resources are accessible

### Debug Mode
Enable debug logging by setting the log level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring & Analytics

### Available Metrics
- Total templates generated
- Success/failure rates
- Average generation time
- Popular scenarios and industries
- API response times

### Health Monitoring
The `/health` endpoint provides system status:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "templates_count": 42,
  "anthropic_available": true,
  "api_key_configured": true
}
```

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
1. **Update Dependencies**: Regularly update Python packages
2. **Monitor API Usage**: Track Anthropic API usage and costs
3. **Review Generated Content**: Periodically audit generated templates
4. **Clean Storage**: Remove old templates and logs as needed
5. **Security Updates**: Keep all dependencies and libraries updated

### Backup Recommendations
- Export important templates regularly
- Backup generation history for compliance
- Keep configuration files in version control

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all functions
- Include docstrings for public methods
- Write meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal and Ethical Use

### Permitted Uses
- Cybersecurity training and education
- Authorized penetration testing
- Security awareness programs
- Academic research (with proper disclosure)

### Prohibited Uses
- Actual phishing attacks against individuals or organizations
- Unauthorized testing of systems you don't own
- Creating templates for malicious purposes
- Any illegal or unethical activities

### Compliance
Users are responsible for ensuring their use of this tool complies with:
- Local and federal laws
- Organizational policies
- Industry regulations
- Ethical guidelines for cybersecurity research

## 📞 Support

### Getting Help
- Check this README and documentation first
- Review the troubleshooting section
- Check GitHub issues for known problems
- Create a new issue with detailed information if needed

### Reporting Issues
When reporting issues, please include:
- Python version and operating system
- Complete error messages and stack traces
- Steps to reproduce the problem
- Expected vs. actual behavior

## 🙏 Acknowledgments

- **Anthropic**: For providing the Claude AI API
- **FastAPI Team**: For the excellent web framework
- **Cybersecurity Community**: For inspiration and best practices


---

**Remember**: This tool is designed to make the internet safer by helping people recognize and avoid phishing attempts. Please use it responsibly and ethically.