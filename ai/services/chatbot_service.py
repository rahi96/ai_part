"""
Chatbot service for Mennie™ AI companion
Handles: chat message processing, response generation, conversation management
"""
from datetime import datetime
import uuid
import random
from typing import Tuple
from ai.models.schemas import ChatMessageResponse
from ai.utils.helpers import generate_confidence_score


class ChatbotService:
    """Service for chatbot operations"""
    
    # Mock response templates for common topics
    RESPONSE_TEMPLATES = {
        "hot flash": [
            "Hot flashes are one of the most common perimenopause symptoms. They can be triggered by stress, caffeine, alcohol, or spicy foods. Try keeping a fan nearby and wearing breathable clothing. Many women find relief through regular exercise and stress management techniques like yoga or meditation.",
            "During a hot flash, your body temperature rises suddenly, which is why you feel that intense heat. It typically lasts 30 seconds to 10 minutes. Some helpful strategies include staying hydrated, limiting caffeine, and practicing deep breathing techniques when you feel one coming on.",
            "Night flashes are basically hot flashes that happen while you're sleeping, causing night sweats. They can seriously disrupt your sleep quality. Consider keeping your bedroom cool, using cotton sheets, and having a water bottle nearby. If they're severe, a healthcare provider can suggest more targeted treatments.",
        ],
        "sleep": [
            "Sleep disturbances are very common during perimenopause due to hormonal changes and night sweats. To improve sleep: maintain a consistent bedtime, keep your bedroom cool, avoid caffeine after 2 PM, and try relaxation techniques before bed. Some women also benefit from magnesium supplements—consult your doctor about this.",
            "Insomnia during perimenopause can be frustrating, but you're not alone. Try creating a bedtime routine, limiting screen time 1 hour before sleep, and avoiding large meals close to bedtime. If issues persist, cognitive behavioral therapy for insomnia (CBT-I) can be very effective.",
            "If you're waking up multiple times during the night, it could be due to hormonal fluctuations, night sweats, or general anxiety. Keep your bedroom environment optimal: dark, quiet, and cool. Try journaling before bed to clear your mind, and consider discussing sleep aids with your healthcare provider.",
        ],
        "mood": [
            "Mood swings during perimenopause are real and caused by fluctuating estrogen levels. Give yourself grace—your brain chemistry is shifting. Regular exercise, especially aerobic activities, can help stabilize mood. Don't hesitate to reach out to friends, family, or a therapist for support.",
            "Anxiety and irritability often peak during perimenopause. Mindfulness meditation, yoga, and deep breathing exercises can help. It's also important to maintain social connections and express your feelings. If anxiety is overwhelming, talking to a healthcare provider about options like therapy or hormone therapy can help.",
            "Emotional resilience during this time comes from self-compassion and support. Journal your feelings, practice being gentle with yourself, and know that these intense emotions are temporary. Your hormones are in flux, which makes everything feel bigger—that's normal and valid.",
        ],
        "brain fog": [
            "Brain fog (also called 'brain fuzz' or 'menopause brain') happens due to fluctuating estrogen affecting cognitive function. To cope: write things down, use phone reminders, break tasks into smaller steps, and get adequate sleep. Regular exercise and staying mentally active also help maintain cognitive clarity.",
            "If you're struggling with focus and memory, you're experiencing a very common perimenopause symptom. Omega-3 fatty acids, adequate hydration, and consistent sleep are crucial. Also, be patient with yourself—cognitive changes are usually temporary and improve after menopause.",
            "Working with brain fog can be frustrating, but there are practical strategies: minimize distractions, use to-do lists, take regular breaks, and stay organized. Some women find that limiting multitasking helps. If severe, discuss with a doctor to rule out other causes like thyroid issues.",
        ],
        "weight": [
            "Weight gain during perimenopause is common due to slower metabolism and hormonal changes. Focus on strength training to maintain muscle mass, eating protein with each meal, and mindful eating. Rather than restrictive dieting, aim for sustainable healthy habits that support your hormonal health.",
            "Metabolism slows during perimenopause, which is frustrating when scales don't budge despite effort. Regular physical activity (both cardio and strength training), adequate sleep, stress management, and balanced nutrition are your best tools. Consider consulting a dietitian familiar with perimenopause.",
            "Building muscle through resistance training is empowering during perimenopause because muscle tissue burns more calories at rest. Combined with consistent cardiovascular exercise and a nutritious diet, you can maintain a healthy weight. Remember, health is about more than the number on the scale.",
        ],
        "default": [
            "Thank you for reaching out! I'm Mennie™, your AI wellness companion. I'm here to support you through perimenopause and menopause. Whether you're dealing with hot flashes, sleep issues, mood changes, or any other symptoms, remember you're not alone. Tell me more about what you're experiencing, and I'll do my best to help.",
            "Hi there! I'm glad you're here. Navigating perimenopause can feel overwhelming, but with the right information and support, you can thrive during this transition. What's been on your mind recently? I'm here to listen and provide helpful suggestions.",
            "Hello! I'm Mennie™, your wellness companion. Whether you have questions about symptoms, lifestyle changes, or just need a listening ear, I'm here for you. Remember, this phase is temporary, and you're stronger than you think. What can I help you with today?",
        ]
    }
    
    @staticmethod
    def generate_response(message: str) -> Tuple[str, float]:
        """
        Generate AI response based on user message
        
        Args:
            message: User's chat message
            
        Returns:
            Tuple of (response_text, confidence_score)
        """
        message_lower = message.lower()
        
        # Determine topic from message
        topic = "default"
        for key in ChatbotService.RESPONSE_TEMPLATES.keys():
            if key in message_lower:
                topic = key
                break
        
        # Select random response for topic
        responses = ChatbotService.RESPONSE_TEMPLATES[topic]
        response = random.choice(responses)
        
        # Generate confidence score (higher for recognized topics)
        if topic == "default":
            confidence = generate_confidence_score() * 0.9  # Lower confidence for generic responses
        else:
            confidence = generate_confidence_score()  # Higher confidence for specific topics
        
        return response, round(confidence, 2)
    
    @staticmethod
    def send_message(
        user_id: int,
        message: str,
        thread_id: str = None
    ) -> ChatMessageResponse:
        """
        Send chat message and get AI response
        
        Args:
            user_id: User identifier
            message: User's chat message
            thread_id: Existing conversation thread ID (optional)
            
        Returns:
            ChatMessageResponse with AI response and metadata
        """
        # Generate new thread ID if not provided
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        # Generate AI response
        response_text, confidence = ChatbotService.generate_response(message)
        
        return ChatMessageResponse(
            response=response_text,
            confidence_score=confidence,
            timestamp=datetime.utcnow(),
            thread_id=thread_id,
        )
    
    @staticmethod
    def get_conversation_history(user_id: int, thread_id: str):
        """
        Get conversation history for a thread
        
        Args:
            user_id: User identifier
            thread_id: Conversation thread ID
            
        Returns:
            List of messages in thread (empty - using LangGraph in-memory storage)
        """
        # Note: Conversation history is now handled by LangGraph workflow in-memory storage
        # This method is kept for compatibility but returns empty list
        return []
