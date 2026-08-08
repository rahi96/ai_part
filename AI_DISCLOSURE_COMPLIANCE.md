# AI Disclosure & App Store Compliance Guide

## Overview
This document describes Navelle's AI transparency and medical disclaimer implementation for app store compliance (Apple Health, Google Play Store).

---

## ✅ Compliance Requirements Met

### 1. **Clear AI Attribution**
Every AI response includes a prominent header identifying:
- That the response is AI-generated
- The specific AI model used (GPT-4 or Claude)
- The purpose (educational support, not medical advice)

**Example:**
```
🤖 **AI Response** (Powered by OpenAI GPT-4)

[Response content here...]
```

### 2. **Comprehensive Medical Disclaimer**
All responses include a detailed disclaimer containing:
- ⚕️ Explicit statement that this is AI-generated, not medical advice
- Specific AI model identification
- Medical source attribution
- Emergency contact information (911, 988 Crisis Lifeline)
- Clear guidance to consult healthcare providers

**Full Disclaimer Format:**
```markdown
---
### ⚕️ Important Medical Disclaimer

**This is an AI-generated response and NOT medical advice.**

• **AI Model:** [Specific Model Name]
• **Medical Sources:** Peer-reviewed research on perimenopause/menopause wellness
• **Purpose:** Educational support and general wellness information only
• **Not a substitute for:** Professional medical advice, diagnosis, or treatment

**Always consult your qualified healthcare provider before making health decisions.**

🚨 **Emergency:** If experiencing severe symptoms or crisis, contact emergency 
services (911) or the 988 Suicide & Crisis Lifeline immediately.
---
```

### 3. **Medical Source Transparency**
When medical knowledge is retrieved from the RAG (Retrieval-Augmented Generation) pipeline:
- Sources are explicitly listed
- Topics are named
- Source count is visible

**Example:**
```
**Medical Sources Referenced:** Hot Flashes — Causes & Mechanisms, 
Night Sweats — Sleep Hygiene Strategies
```

### 4. **API Response Metadata**
Every API response includes compliance fields:

```json
{
  "response": "[Full response with embedded AI header and disclaimer]",
  "ai_model": "gpt-4o",
  "ai_attribution": "🤖 **AI Response** (Powered by OpenAI GPT-4)",
  "is_ai_generated": true,
  "medical_disclaimer": "This is AI-generated educational content, not medical advice. Always consult your healthcare provider.",
  "sources": ["Hot Flashes — Causes & Mechanisms", "..."],
  "response_source": "general_knowledge",
  "confidence": 0.87
}
```

---

## 🏥 Medical Safety Features

### Crisis Detection & Emergency Guidance
- System prompt instructs AI to recognize crisis keywords
- Immediate emergency contact information provided for:
  - Self-harm mentions
  - Suicidal ideation
  - Severe mental health symptoms
- 911 and 988 Crisis Lifeline prominently displayed

### No Diagnosis Policy
- AI explicitly instructed to never diagnose conditions
- Gentle redirection to healthcare professionals
- Symptom description vs. diagnosis distinction maintained

### Evidence-Based Information
- 23 curated medical documents on perimenopause/menopause
- Peer-reviewed research backing
- Regular updates to medical knowledge base

---

## 📱 Frontend Implementation Guidelines

### Required UI Elements

1. **Prominent AI Badge**
   ```
   Display: ai_attribution field from API response
   Location: Top of each message bubble
   Styling: Distinct color/icon to differentiate from human messages
   ```

2. **Expandable Disclaimer**
   ```
   Show: Condensed version by default
   Expand: Full disclaimer accessible via tap/click
   Persistence: Visible on every AI message
   ```

3. **Source Attribution (when available)**
   ```
   Display: sources array as expandable list
   Label: "Medical Sources Referenced"
   Action: Allow users to see what knowledge informed the response
   ```

4. **Settings Page Disclosure**
   ```
   Section: "About AI Assistant"
   Content:
   - AI model version
   - Data usage policy
   - Limitations of AI advice
   - Link to full medical disclaimer
   - Emergency contact numbers
   ```

### Example UI Mockup
```
┌─────────────────────────────────────┐
│ 🤖 AI Response (GPT-4)              │
├─────────────────────────────────────┤
│                                     │
│ [Response content here...]          │
│                                     │
│ Sources: 2 medical documents ▼      │
│                                     │
│ ⚕️ Medical Disclaimer ▼             │
├─────────────────────────────────────┤
│ Confidence: 87%                     │
└─────────────────────────────────────┘
```

---

## 🔍 App Store Review Checklist

### Apple Health Review
- [ ] AI attribution visible in every message
- [ ] Medical disclaimer present and accessible
- [ ] Emergency contact info included
- [ ] "Not medical advice" statement prominent
- [ ] Specific AI model identified
- [ ] Crisis detection implemented
- [ ] Healthcare provider guidance included

### Google Play Store
- [ ] AI disclosure in app description
- [ ] Medical disclaimer in every response
- [ ] Source transparency implemented
- [ ] Emergency resources provided
- [ ] Data privacy policy includes AI processing
- [ ] User consent for AI interaction

---

## 📝 App Store Description Template

### Suggested Text for App Listings

**About AI Features:**
```
Navelle uses artificial intelligence (OpenAI GPT-4 / Anthropic Claude) to 
provide personalized perimenopause wellness support. All AI responses:

✓ Clearly labeled as AI-generated
✓ Include medical disclaimers
✓ Reference peer-reviewed sources
✓ Are for educational purposes only
✓ Direct you to healthcare providers for medical decisions

IMPORTANT: This app provides wellness information and emotional support. 
It is NOT a substitute for professional medical advice, diagnosis, or treatment.

For medical emergencies, call 911.
For mental health crisis, call 988.
```

---

## 🔧 Technical Implementation

### API Endpoint
```
POST /api/ai/chat/message
```

### Response Schema
See `ai/models/schemas.py` - `ChatMessageResponse` for complete schema with all compliance fields.

### Key Files
- `ai/utils/langchain_rag.py` - AI attribution & disclaimer implementation
- `ai/workflows/chat_workflow.py` - Workflow with disclaimer injection
- `ai/routes/chat.py` - API response with compliance metadata
- `ai/models/schemas.py` - Response schema documentation

---

## 🛡️ Privacy & Data Handling

### User Data
- Health data used for personalization only
- Not stored by AI service (OpenAI/AWS)
- Processed in real-time, not retained beyond session

### AI Model
- OpenAI GPT-4: HIPAA-compliant API tier available
- AWS Bedrock Claude: Enterprise compliance
- No training on user data

### Conversation Threads
- 30-day retention maximum
- User can delete threads anytime
- No sharing of conversations between users

---

## 📞 Support & Compliance Contacts

**For App Store Reviewers:**
- Technical Contact: [Your Email]
- Medical Advisor: [Advisor Name/Credentials]
- Privacy Officer: [Privacy Contact]

**Emergency Resources Provided to Users:**
- 911 (Emergency Services)
- 988 (Suicide & Crisis Lifeline)
- National Women's Health Hotline: 1-800-994-9662

---

## 🔄 Updates & Maintenance

### AI Model Updates
- Version tracked in `ai/config.py`
- Changelog maintained for model changes
- Users notified of significant AI updates

### Medical Content
- Knowledge base reviewed quarterly
- Sources updated based on latest research
- Expert medical review for accuracy

### Compliance Monitoring
- Regular audits of AI responses
- User feedback on clarity of disclaimers
- Updates based on regulatory changes

---

## ✨ Summary

Navelle's AI implementation prioritizes:
1. **Transparency** - Users always know they're talking to AI
2. **Safety** - Clear medical disclaimers and emergency guidance
3. **Trust** - Source attribution and evidence-based information
4. **Compliance** - Meeting app store requirements for medical AI

Every response makes it crystal clear that this is AI-generated educational content, 
not medical advice, with prominent guidance to consult healthcare professionals.

---

**Last Updated:** 2026-08-08  
**Compliance Version:** 1.0  
**AI Model:** OpenAI GPT-4o / Anthropic Claude Opus 4.5
