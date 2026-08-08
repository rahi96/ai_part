# Navelle AI Module

**AI-Powered Perimenopause & Menopause Wellness Companion**

Navelle provides empathetic, evidence-based support through "Mennie™" — an AI assistant powered by OpenAI GPT-4 and AWS Bedrock Claude, designed to help women navigate perimenopause and menopause with confidence.

---

## 🌟 Features

- **🤖 AI Chat Companion** - Conversational support with RAG (Retrieval-Augmented Generation)
- **📊 Health Analytics** - Symptom tracking, trends, and insights
- **🏥 Medical History Analysis** - Condition analysis with comorbidities
- **💪 Wellness Tools** - Mood tracking, humor breaks, journey planning
- **📚 Evidence-Based Knowledge** - 23 curated medical documents on perimenopause/menopause

## ⚕️ Medical AI Compliance

**App Store Ready:** Full compliance with Apple Health and Google Play Store requirements for medical AI applications.

✅ **Clear AI Attribution** - Every response labeled with AI model  
✅ **Comprehensive Disclaimers** - Medical disclaimers in all responses  
✅ **Source Transparency** - Medical sources clearly referenced  
✅ **Emergency Guidance** - 911 and 988 Crisis Lifeline info included  
✅ **No Diagnosis Policy** - AI never diagnoses, always directs to healthcare providers

See [`AI_DISCLOSURE_COMPLIANCE.md`](AI_DISCLOSURE_COMPLIANCE.md) for complete compliance documentation.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API Key OR AWS Bedrock access
- Pinecone API Key (for vector search)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rahi96/ai_part.git
   cd ai_part
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   BACKEND_URL=http://your-backend-url
   CUSTOMER_TOKEN=your_customer_token
   ADMIN_TOKEN=your_admin_token
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

5. **Test it**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 🐳 Docker Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete Docker and AWS EC2 deployment instructions.

**Quick Docker Run:**
```bash
docker-compose up -d
```

---

## 📡 API Endpoints

### Chat
- `POST /api/ai/chat/message` - Send message to AI companion
- `GET /api/ai/chat/thread/{thread_id}/history` - Get conversation history
- `DELETE /api/ai/chat/thread/{thread_id}` - Clear conversation thread

### Wellness
- `POST /api/ai/mood/select` - Record mood check-in
- `GET /api/ai/humor-break/{user_id}` - Get wellness humor break

### Analytics
- `GET /api/ai/analytics/most-used-questions` - Popular queries
- `GET /api/ai/analytics/recent-queries` - Recent query analysis

### Medical History
- `POST /api/ai/medical-history/{user_id}/analyze` - Analyze medical history

### Health Analysis
- `POST /api/ai/analyze` - Comprehensive health analysis
- `GET /api/ai/wellness/dashboard/{user_id}` - Wellness dashboard

---

## 🔧 Configuration

All settings in `ai/config.py` with environment variable support:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key (GPT-4) | Yes* |
| `AWS_ACCESS_KEY_ID` | AWS access key (Bedrock) | Yes* |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (Bedrock) | Yes* |
| `PINECONE_API_KEY` | Pinecone vector DB key | Yes |
| `BACKEND_URL` | Navelle backend API URL | Yes |
| `CUSTOMER_TOKEN` | Backend customer auth token | Yes |
| `ADMIN_TOKEN` | Backend admin auth token | Yes |

\* Either OpenAI OR AWS Bedrock credentials required

---

## 🏗️ Architecture

```
ai/
├── routes/          # FastAPI route handlers
├── services/        # Business logic layer
├── utils/           # RAG pipeline, LLM clients, helpers
├── workflows/       # LangGraph chat workflow (4-node state machine)
├── models/          # Pydantic schemas
└── config.py        # Configuration management
```

**Key Technologies:**
- **FastAPI** - Modern async web framework
- **LangChain** - LLM orchestration
- **LangGraph** - State machine workflow (classify → respond → disclaimer → thread)
- **Pinecone** - Vector database for RAG
- **OpenAI GPT-4** - Primary LLM
- **AWS Bedrock Claude** - Fallback LLM

---

## 📋 API Response Example

```json
{
  "response": "🤖 **AI Response** (Powered by OpenAI GPT-4)\n\nHot flashes are...",
  "ai_model": "gpt-4o",
  "ai_attribution": "🤖 **AI Response** (Powered by OpenAI GPT-4)",
  "is_ai_generated": true,
  "medical_disclaimer": "This is AI-generated educational content...",
  "sources": ["Hot Flashes — Causes & Mechanisms"],
  "response_source": "general_knowledge",
  "confidence": 0.87,
  "thread_id": "abc-123",
  "intent": "medical_query"
}
```

---

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat message
curl -X POST http://localhost:8000/api/ai/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "I am experiencing hot flashes. What can I do?"
  }'
```

---

## 📝 Documentation

- **[AI Disclosure & Compliance](AI_DISCLOSURE_COMPLIANCE.md)** - App store compliance guide
- **[Deployment Guide](DEPLOYMENT.md)** - Docker & AWS EC2 deployment
- **[Medical History API](MEDICAL_HISTORY_API_GUIDE.md)** - Medical history analysis endpoint

---

## 🔒 Security & Privacy

- ✅ HIPAA-compliant API tier available (OpenAI)
- ✅ No AI training on user data
- ✅ 30-day conversation thread retention
- ✅ User-deletable chat history
- ⚠️ Update CORS settings before production
- ⚠️ Add rate limiting before production

---

## 🚨 Emergency Resources

The AI always provides emergency contact information:
- **911** - Emergency Services
- **988** - Suicide & Crisis Lifeline
- **National Women's Health Hotline** - 1-800-994-9662

---

## 📊 Analytics

All queries tracked in `analytics_store.json`:
- Question frequency
- Confidence scores
- Intent classification
- Response sources

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

[Your License Here]

---

## 📞 Contact

- **Technical Support:** [Your Email]
- **Medical Advisor:** [Advisor Name]
- **Website:** [Your Website]

---

**Built with ❤️ for women navigating perimenopause and menopause**
