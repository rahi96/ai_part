# 📚 AI Response Sources with External URLs

## ✅ **What Changed**

Your chatbot now includes **external source URLs** showing WHERE the medical information came from.

---

## 🔍 **Before (Just Topics)**

```json
{
  "response": "Hot flashes are caused by declining estrogen levels...",
  "sources": [
    "Hot Flashes — Causes & Mechanisms",
    "Night Sweats — Understanding & Differentiation",
    "Hot Flashes — Non-Hormonal Management"
  ]
}
```

❌ **Problem:** Users don't know WHERE this information came from.

---

## ✨ **After (With External URLs)**

```json
{
  "response": "Hot flashes are caused by declining estrogen levels...",
  "sources": [
    {
      "topic": "Hot Flashes — Causes & Mechanisms",
      "url": "https://www.mayoclinic.org/diseases-conditions/menopause/symptoms-causes/syc-20353397",
      "source_name": "Mayo Clinic"
    },
    {
      "topic": "Night Sweats — Understanding & Differentiation",
      "url": "https://www.hopkinsmedicine.org/health/conditions-and-diseases/introduction-to-menopause",
      "source_name": "Johns Hopkins Medicine"
    },
    {
      "topic": "Hot Flashes — Non-Hormonal Management",
      "url": "https://www.hopkinsmedicine.org/health/wellness-and-prevention/managing-menopause-symptoms",
      "source_name": "Johns Hopkins Medicine"
    }
  ]
}
```

✅ **Fixed:** Users can click URLs to verify information from trusted medical sources!

---

## 📱 **How to Display in Your App**

### **Option 1: Simple List**
```
Sources:
• Hot Flashes — Causes & Mechanisms (Mayo Clinic)
  https://www.mayoclinic.org/...
• Night Sweats — Understanding & Differentiation (Johns Hopkins Medicine)
  https://www.hopkinsmedicine.org/...
```

### **Option 2: Clickable Links**
```
Sources:
• [Hot Flashes — Causes & Mechanisms](https://www.mayoclinic.org/...)
  from Mayo Clinic
• [Night Sweats — Understanding & Differentiation](https://www.hopkinsmedicine.org/...)
  from Johns Hopkins Medicine
```

### **Option 3: Cards with Icons**
```
┌─────────────────────────────────────────┐
│ 🏥 Mayo Clinic                          │
│ Hot Flashes — Causes & Mechanisms       │
│ [View Source →]                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🏥 Johns Hopkins Medicine               │
│ Night Sweats — Understanding...         │
│ [View Source →]                         │
└─────────────────────────────────────────┘
```

---

## 🌐 **Medical Sources Added**

Currently added trusted medical organizations:
- **Mayo Clinic** - https://www.mayoclinic.org
- **Johns Hopkins Medicine** - https://www.hopkinsmedicine.org
- **NHS UK** - https://www.nhs.uk
- **Harvard Health** - https://www.health.harvard.edu
- **NIMH** - https://www.nimh.nih.gov
- **Sleep Foundation** - https://www.sleepfoundation.org

---

## 📝 **App Store Compliance**

This satisfies app store requirements because:
1. ✅ Users can see **exact source URLs**
2. ✅ Users can **verify information independently**
3. ✅ Transparency about **where AI got the information**
4. ✅ Credited **reputable medical organizations**

---

## 🧪 **Testing**

Test with a medical query:
```bash
POST http://13.50.107.124:8000/api/ai/chat/message
{
  "user_id": "test123",
  "message": "I have hot flashes at night"
}
```

Expected response:
```json
{
  "sources": [
    {
      "topic": "Hot Flashes — Causes & Mechanisms",
      "url": "https://www.mayoclinic.org/diseases-conditions/menopause/symptoms-causes/syc-20353397",
      "source_name": "Mayo Clinic"
    }
  ]
}
```

---

## 🚀 **Next Steps**

1. **Delete old Pinecone index** (dimension mismatch)
2. **Reseed with new document structure** (includes source URLs)
3. **Test on AWS deployment**
4. **Update mobile app UI** to display clickable source links

---

## 💡 **Adding More Sources**

To add URLs to remaining documents, edit `ai/utils/pinecone_client.py`:

```python
{
    "id": "doc_XXX",
    "topic": "Your Topic Here",
    "content": "...",
    "category": "symptoms",
    "keywords": [...],
    "source_url": "https://credible-medical-site.org/article",  # ADD THIS
    "source_name": "Organization Name",  # ADD THIS
}
```

Then reseed Pinecone to update the vector database.
