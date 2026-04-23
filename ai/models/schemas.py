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


class ChatMessageResponse(BaseModel):
    """Response from chatbot"""
    response: str  # AI-generated reply
    confidence_score: float  # 0-1, displayed as percentage
    timestamp: datetime
    thread_id: str  # Generated or existing thread ID
    
    class Config:
        from_attributes = True


# ==================== Common Models ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None


# ==================== Journey - Health Goals ====================

class GoalProgressItem(BaseModel):
    """Individual health goal progress"""
    title: str
    target_description: str
    current_value: float
    target_value: float
    progress_percentage: float  # 0-100


class HealthGoalCreateRequest(BaseModel):
    """Request to create a health goal"""
    goal_title: str
    measurement: str  # e.g., "kg", "hours", "steps"
    current_value: float
    target_value: float
    notes: Optional[str] = None


class JourneyPlanResponse(BaseModel):
    """Response for journey plan generation"""
    plan_title: str = "EMPOWER YOUR PERIMENOPAUSE JOURNEY"
    username: str
    created_at: str
    welcome_message: str
    why_plan_description: str
    goals: List[GoalProgressItem]
    recommended_actions: List[str]
    next_review_date: str


# ==================== Medical History Analysis ====================

class MedicalHistoryEntry(BaseModel):
    """Single medical history entry"""
    condition_name: str
    category: str  # e.g., "Hormonal", "Metabolic", "Mental Health"
    start: Optional[str] = None
    date_diagnosed: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistoryAnalysisRequest(BaseModel):
    """Request to analyze medical history"""
    medical_history: MedicalHistoryEntry


class RelatedCondition(BaseModel):
    """Related condition with overlap info"""
    name: str
    match_percentage: int  # 0-100
    severity: str  # low, medium, high
    color: str
    shared_symptoms: List[str]


class SymptomOverlap(BaseModel):
    """Symptom overlap percentages"""
    Hormonal: int = 0
    Mental: int = 0
    Metabolic: int = 0
    Fatigue: int = 0
    Immune: int = 0


class MedicalHistoryAnalysisDetail(BaseModel):
    """Detailed analysis result"""
    title: str
    description: str
    symptom_overlap: SymptomOverlap
    conditions: List[RelatedCondition]


class MedicalHistoryAnalysisResponse(BaseModel):
    """Response for medical history analysis"""
    analysis: MedicalHistoryAnalysisDetail
