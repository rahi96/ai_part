"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== Health Report - Page 1 ====================

# 1. Wellness Dashboard
class WellnessDashboardResponse(BaseModel):
    """Response for wellness dashboard metrics"""
    overall_score: int  # 0-101
    logged_days: int  # e.g., 7 out of 7
    total_days: int  # e.g., 7
    avg_severity: float  # 0-10 scale
    
    class Config:
        from_attributes = True


# 2. Symptom Trend
class TrendDataPoint(BaseModel):
    """Single day trend data"""
    day: str  # "Tue", "Wed", etc.
    date: str  # "2024-01-15"
    symptom_count: int
    medication_mentions: int


class SymptomTrendResponse(BaseModel):
    """Response for symptom trend analysis"""
    trend_data: List[TrendDataPoint]
    total_symptoms_week: int
    most_frequent_symptom: Optional[str]
    trend_direction: str  # "up", "down", "stable"
    
    class Config:
        from_attributes = True


# 3. Top Symptoms
class TopSymptomsItem(BaseModel):
    """Individual symptom with trend info"""
    symptom_name: str
    frequency_count: int
    trend_percentage: str  # "↑16%", "↓8%"
    severity_level: int  # 1-10
    

class TopSymptomsResponse(BaseModel):
    """Response for top symptoms analysis"""
    symptoms: List[TopSymptomsItem]
    analysis_period_days: int
    
    class Config:
        from_attributes = True


# 4. Trigger Warnings
class TriggerWarningsRequest(BaseModel):
    """Request for trigger warning analysis"""
    user_id: int


class TriggerWarningsResponse(BaseModel):
    """Response for trigger warnings"""
    warning_text: str  # AI-generated insight
    trigger_factor: str  # e.g., "caffeine intake"
    recommendation: str  # Actionable recommendation
    confidence_score: float  # 0-1
    
    class Config:
        from_attributes = True


# ==================== Home/Dashboard - Page 2 ====================

# 1. Mood Selector
class MoodSelectorRequest(BaseModel):
    """Request for mood selection"""
    mood: str  # CALM, SAD, ANGRY, NEED_TO_TALK


class MoodSelectorResponse(BaseModel):
    """Response for mood selection"""
    mood_recorded: bool
    mood: str
    timestamp: datetime
    message: str = "Mood recorded successfully"


# 2. Humor Break
class HumorBreakResponse(BaseModel):
    """Response for humor break endpoint"""
    humor_text: str  # Funny joke or health fact
    suggestion: str  # Self-care tip
    category: str  # "mood-related" or "symptom-related"
    timestamp: datetime


# ==================== Analytics - Page 3 ====================

# 1. Most Used Questions
class QuestionItem(BaseModel):
    """Individual question with metrics"""
    question_text: str
    ask_count: int
    trend: str  # "↑18%", "↓1%", "→0%"
    threads_processed: int


class MostUsedQuestionsResponse(BaseModel):
    """Response for most used questions"""
    questions: List[QuestionItem]
    total_unique_questions: int
    analysis_period: str  # "7d" or "30d"
    timestamp: datetime
    
    class Config:
        from_attributes = True


# 2. Recent Queries Analysis
class RecentQueryItem(BaseModel):
    """Individual recent query with performance metrics"""
    question_text: str
    confidence_score: float  # 0-1, displayed as percentage
    threads_processed: int
    timestamp: datetime


class RecentQueriesResponse(BaseModel):
    """Response for recent queries analysis"""
    queries: List[RecentQueryItem]
    total_queries_analyzed: int
    avg_confidence: float
    analysis_period: str  # "7d" or "30d"
    
    class Config:
        from_attributes = True


# ==================== Chatbot - Page 4 ====================

# 1. Chat Message
class ChatMessageRequest(BaseModel):
    """Request to send a chat message"""
    message: str  # User query/message
    thread_id: Optional[str] = None  # Existing thread ID (optional)


class SourceReference(BaseModel):
    """External source reference with URL"""
    topic: str  # Document topic/title
    url: str  # External source URL (website, journal, etc.)
    source_name: str  # Organization name (e.g., "Mayo Clinic")


class ChatMessageResponse(BaseModel):
    """Response from chatbot with AI attribution for app store compliance"""
    response: str  # AI-generated reply with embedded disclaimer
    confidence_score: float  # 0-1, displayed as percentage
    timestamp: datetime
    thread_id: str  # Generated or existing thread ID
    # App Store Compliance Fields
    ai_model: str  # Specific AI model used (e.g., "gpt-4o", "claude-opus-4")
    ai_attribution: str  # AI attribution header for UI display
    is_ai_generated: bool = True  # Always True - indicates AI-generated content
    medical_disclaimer: str  # Short disclaimer for quick reference
    sources: Optional[List[SourceReference]] = []  # External source references with URLs
    response_source: str  # "general_knowledge" | "template" | etc.
    
    class Config:
        from_attributes = True


# ==================== Health Journey - New Section ====================

# 1. Health Goal Creation
class HealthGoalCreateRequest(BaseModel):
    """Request to create a new health goal (Image 1)"""
    goal_title: str  # e.g., "Reduce hot flashes frequency"
    measurement: str  # e.g., "Wellbeing"
    current_value: float  # e.g., 5
    target_value: float  # e.g., 2
    start_date: str  # e.g., "2026-04-20"
    target_date: Optional[str] = None
    notes: Optional[str] = None


class GoalProgressItem(BaseModel):
    """Goal progress for the plan view (Image 2)"""
    title: str
    target_description: str
    current_value: float
    target_value: float
    progress_percentage: float  # 0-100


class JourneyPlanResponse(BaseModel):
    """Response for the perimenopause journey plan (Image 2)"""
    plan_title: str = "EMPOWER YOUR PERIMENOPAUSE JOURNEY"
    username: str
    created_at: str  # "February 19th, 2026"
    welcome_message: str
    why_plan_title: str = "WHY THIS PLAN"
    why_plan_description: str
    goals: List[GoalProgressItem]
    recommended_actions: List[str]
    next_review_date: str  # "MARCH 5TH, 2026"

    class Config:
        from_attributes = True


# ==================== Medical History Analysis ====================

# Medical History Input
class MedicalHistoryInput(BaseModel):
    """Single medical history entry"""
    condition_name: str
    start: str  # YYYY-MM format
    category: str
    date_diagnosed: str  # YYYY-MM-DD format
    notes: str


class MedicalHistoryAnalysisRequest(BaseModel):
    """Request for medical history analysis"""
    medical_history: MedicalHistoryInput


# Symptom Overlap Response
class SymptomOverlapData(BaseModel):
    """Symptom overlap percentages"""
    Hormonal: Optional[int] = None
    Mental: Optional[int] = None
    PCOS: Optional[int] = None
    Metabolic: Optional[int] = None
    Fatigue: Optional[int] = None
    Immune: Optional[int] = None
    
    class Config:
        extra = "allow"  # Allow additional fields


# Related Condition
class RelatedCondition(BaseModel):
    """Individual related condition with analysis"""
    name: str
    match_percentage: int  # 0-100
    severity: str  # "low", "medium", "high"
    color: str  # Color code for UI (e.g., "red", "orange")
    shared_symptoms: Optional[List[str]] = None


# Medical History Analysis Response
class MedicalHistoryAnalysisResponse(BaseModel):
    """Response with AI-generated medical history analysis"""
    
    class Analysis(BaseModel):
        title: str  # e.g., "Conditions That Matter, Menopause"
        description: str  # Explanation of symptom overlap
        symptom_overlap: SymptomOverlapData  # Percentages for each category
        conditions: List[RelatedCondition]  # List of related conditions
        
        class Config:
            from_attributes = True
    
    analysis: Analysis
    
    class Config:
        from_attributes = True


# ==================== Common Models ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
