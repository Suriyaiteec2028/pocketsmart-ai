from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base

class RecommendationPlan(Base):
    __tablename__ = "recommendation_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    planner_type = Column(String(50), nullable=False, index=True)  # 'home', 'party', 'jewelry'
    title = Column(String(200), nullable=False)
    budget = Column(Float, nullable=False)
    estimated_total = Column(Float, nullable=False)
    remaining_budget = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    
    # Store complete input and structured AI result
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    
    is_fallback = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="plans")
    saved_items = relationship("SavedRecommendation", back_populates="plan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RecommendationPlan(id={self.id}, type='{self.planner_type}', budget={self.budget})>"
