from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base

class SavedRecommendation(Base):
    __tablename__ = "saved_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recommendation_plan_id = Column(Integer, ForeignKey("recommendation_plans.id", ondelete="CASCADE"), nullable=True, index=True)
    
    item_name = Column(String(255), nullable=False)
    item_category = Column(String(100), nullable=True)
    platform = Column(String(100), nullable=True)
    estimated_price = Column(Float, nullable=True)
    recommendation_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="saved_recommendations")
    plan = relationship("RecommendationPlan", back_populates="saved_items")

    def __repr__(self):
        return f"<SavedRecommendation(id={self.id}, user_id={self.user_id}, item='{self.item_name}')>"
