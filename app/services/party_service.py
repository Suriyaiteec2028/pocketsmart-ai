import json
import logging
from typing import Dict, Any, List
from app.schemas.party import PartyPlannerRequest
from app.services.gemini_service import gemini_service
from app.utils.budget import calculate_budget_totals, rebalance_recommendations_if_exceeded

logger = logging.getLogger("pocketsmart.party")

PARTY_FALLBACK_DATABASE = {
    "catering": [
        {"name": "Swiggy Gourmet Vegetarian Celebration Buffet", "category": "Catering", "platform": "Swiggy", "per_person": 350, "reason": "Wide assortment of appetizers, 3 main curries, breads, biryani, and gulab jamun.", "image_url": "https://images.unsplash.com/photo-1555244162-803834f70033?w=500&auto=format&fit=crop", "product_url": "https://www.swiggy.com"},
        {"name": "Zomato Grand Feast Live Counter Catering", "category": "Catering", "platform": "Zomato", "per_person": 480, "reason": "Fresh live tandoor and chaat counters with veg and non-veg options.", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&auto=format&fit=crop", "product_url": "https://www.zomato.com"},
        {"name": "High-Tea Celebration Snack Box Package", "category": "Catering", "platform": "Swiggy", "per_person": 180, "reason": "Budget-friendly finger foods, sliders, samosas, and beverages for casual gatherings.", "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop", "product_url": "https://www.swiggy.com"}
    ],
    "venue": [
        {"name": "OYO Townhouse Banquet & Celebration Hall", "category": "Venue", "platform": "OYO", "price_ratio": 0.30, "reason": "Centrally located AC hall with seating capacity, lighting, and stage setup.", "image_url": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=500&auto=format&fit=crop", "product_url": "https://www.oyorooms.com"},
        {"name": "Skyline Rooftop Party Deck", "category": "Venue", "platform": "Zomato", "price_ratio": 0.35, "reason": "Scenic rooftop ambiance with open-air terrace seating.", "image_url": "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=500&auto=format&fit=crop", "product_url": "https://www.zomato.com"},
        {"name": "Private Garden Lawn & Gazebo", "category": "Venue", "platform": "Local Event Partner", "price_ratio": 0.28, "reason": "Spacious lawn area ideal for outdoor photography and interactive games.", "image_url": "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=500&auto=format&fit=crop", "product_url": "https://www.google.com/search?q=event+venues+near+me"}
    ],
    "decoration": [
        {"name": "Themed Balloon Arch & Fairy Light Backdrop", "category": "Decoration", "platform": "Local Decor Partner", "price_ratio": 0.12, "reason": "Vibrant color-coordinated backdrop with fairy lights for photo sessions.", "image_url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=party+decorations"},
        {"name": "Elegant Floral Centerpieces & Welcome Board", "category": "Decoration", "platform": "Local Florist", "price_ratio": 0.15, "reason": "Fresh flower arrangements that add sophisticated elegance to guest tables.", "image_url": "https://images.unsplash.com/photo-1519225424982-f0da3d6cbb15?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=floral+decorations"}
    ],
    "entertainment": [
        {"name": "Professional DJ with Sound & Dance Floor Lights", "category": "Entertainment", "platform": "Local Partner", "price_ratio": 0.10, "reason": "Experienced party DJ keeping guests energized with hit music tracks.", "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500&auto=format&fit=crop", "product_url": "https://www.google.com/search?q=dj+for+party"},
        {"name": "Acoustic Live Music Duo & Singer", "category": "Entertainment", "platform": "Local Artist Guild", "price_ratio": 0.12, "reason": "Warm acoustic guitar and melodic vocal performances for upscale dinners.", "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop", "product_url": "https://www.google.com/search?q=live+music+artists"},
        {"name": "Bluetooth Party Sound System & Wireless Mics", "category": "Entertainment", "platform": "Amazon", "price_ratio": 0.05, "reason": "Cost-effective plug-and-play sound for DIY playlists and speeches.", "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=party+speaker"}
    ],
    "accommodation": [
        {"name": "Townhouse Deluxe Guest Rooms (OYO)", "category": "Accommodation", "platform": "OYO", "price_per_room": 1650, "reason": "Comfortable AC rooms within walking distance for outstation guests.", "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&auto=format&fit=crop", "product_url": "https://www.oyorooms.com"}
    ]
}

class PartyService:
    @staticmethod
    def _build_prompt(req: PartyPlannerRequest) -> tuple[str, str]:
        system_instruction = (
            "You are PocketSmart AI, an expert event and party budget planner. "
            "Your mission is to dynamically allocate the user's budget across Venue, Catering, "
            "Decoration, Entertainment, and Accommodation (if needed). "
            "CRITICAL RULES:\n"
            "1. You MUST NEVER exceed the total budget. Total estimated spending must be <= budget.\n"
            "2. Factor in the guest count accurately when calculating food & catering costs.\n"
            "3. If accommodation is requested, calculate room costs sensibly.\n"
            "4. Return ONLY valid JSON matching the specified schema."
        )

        user_content = {
            "budget": req.budget,
            "currency": req.currency,
            "event_type": req.event_type,
            "guest_count": req.guest_count,
            "event_date": req.event_date or "Flexible",
            "venue_type": req.venue_type,
            "location": req.location,
            "catering_preference": req.catering_preference,
            "decoration_level": req.decoration_level,
            "entertainment": req.entertainment,
            "need_accommodation": req.need_accommodation,
            "room_count": req.room_count,
            "additional_requirements": req.additional_requirements or "None"
        }

        prompt = (
            f"Generate a complete, realistic party budget plan strictly in JSON.\n"
            f"Event Details:\n{json.dumps(user_content, indent=2)}\n\n"
            f"Schema:\n"
            f"{{\n"
            f'  "planner": "party",\n'
            f'  "budget": {req.budget},\n'
            f'  "allocated_budget": {{\n'
            f'    "Venue": 0,\n'
            f'    "Catering": 0,\n'
            f'    "Decoration": 0,\n'
            f'    "Entertainment": 0,\n'
            f'    "Accommodation": 0,\n'
            f'    "Miscellaneous": 0\n'
            f'  }},\n'
            f'  "recommendations": [\n'
            f'    {{\n'
            f'      "category": "Catering",\n'
            f'      "product_name": "Package Name",\n'
            f'      "platform": "Swiggy / Zomato",\n'
            f'      "estimated_price": 400,\n'
            f'      "quantity": {req.guest_count},\n'
            f'      "total_price": {400 * req.guest_count},\n'
            f'      "reason": "Why this catering fits the event",\n'
            f'      "priority": "High",\n'
            f'      "product_url": "https://www.swiggy.com"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "summary": "Summary of budget allocation and vendor choices"\n'
            f"}}\n"
            f"Ensure all recommendations sum to <= {req.budget}. Return ONLY JSON."
        )
        return system_instruction, prompt

    @classmethod
    def generate_fallback_plan(cls, req: PartyPlannerRequest) -> Dict[str, Any]:
        """Realistic party plan generator when AI service is unavailable."""
        logger.info(f"Generating realistic fallback party plan for {req.event_type}, budget: {req.budget}")
        
        # Calculate dynamic allocation percentages based on event and guest count
        # If accommodation is needed, allocate ~15% for rooms
        need_rooms = req.need_accommodation and req.room_count and req.room_count > 0
        if need_rooms:
            venue_pct = 0.25
            food_pct = 0.35
            decor_pct = 0.12
            ent_pct = 0.08
            acc_pct = 0.15
            misc_pct = 0.05
        else:
            venue_pct = 0.30
            food_pct = 0.40
            decor_pct = 0.15
            ent_pct = 0.10
            acc_pct = 0.0
            misc_pct = 0.05

        allocated = {
            "Venue": round(req.budget * venue_pct, 2),
            "Catering": round(req.budget * food_pct, 2),
            "Decoration": round(req.budget * decor_pct, 2),
            "Entertainment": round(req.budget * ent_pct, 2),
            "Miscellaneous": round(req.budget * misc_pct, 2)
        }
        if need_rooms:
            allocated["Accommodation"] = round(req.budget * acc_pct, 2)

        recommendations: List[Dict[str, Any]] = []

        # 1. Catering
        catering_budget = allocated["Catering"]
        target_per_person = catering_budget / max(1, req.guest_count)
        per_person = round(max(150, min(target_per_person, 600)))
        total_food = per_person * req.guest_count
        food_vendor = "Swiggy" if req.catering_preference in ["Vegetarian", "Snacks Only"] else "Zomato"
        recommendations.append({
            "category": "Catering",
            "product_name": f"{food_vendor} {req.catering_preference} Celebration Buffet",
            "platform": food_vendor,
            "estimated_price": float(per_person),
            "quantity": req.guest_count,
            "total_price": float(total_food),
            "reason": f"Complete {req.catering_preference.lower()} menu configured at ₹{per_person}/guest for {req.guest_count} guests.",
            "priority": "High",
            "product_url": "https://www.swiggy.com" if food_vendor == "Swiggy" else "https://www.zomato.com",
            "image_url": "https://images.unsplash.com/photo-1555244162-803834f70033?w=500&auto=format&fit=crop"
        })

        # 2. Venue
        venue_budget = allocated["Venue"]
        venue_name = f"OYO Banquet Space ({req.venue_type} Style)" if req.venue_type != "Home" else "Home Decor & Setup Arrangements"
        venue_price = round(venue_budget * 0.90)
        recommendations.append({
            "category": "Venue",
            "product_name": venue_name,
            "platform": "OYO" if req.venue_type != "Home" else "Local Setup",
            "estimated_price": float(venue_price),
            "quantity": 1,
            "total_price": float(venue_price),
            "reason": f"Comfortably accommodates {req.guest_count} guests in {req.location or 'your selected area'}.",
            "priority": "High",
            "product_url": "https://www.oyorooms.com",
            "image_url": "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=500&auto=format&fit=crop"
        })

        # 3. Decoration
        decor_budget = allocated["Decoration"]
        decor_price = round(decor_budget * 0.85)
        recommendations.append({
            "category": "Decoration",
            "product_name": f"{req.decoration_level} Theme Decor & Photo Booth Setup",
            "platform": "Event Decor Partner",
            "estimated_price": float(decor_price),
            "quantity": 1,
            "total_price": float(decor_price),
            "reason": f"{req.decoration_level} aesthetic with focal balloon/floral backdrop tailored for {req.event_type}.",
            "priority": "Medium",
            "product_url": "https://www.amazon.in/s?k=party+decor",
            "image_url": "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=500&auto=format&fit=crop"
        })

        # 4. Entertainment
        if req.entertainment and req.entertainment.lower() != "none":
            ent_budget = allocated["Entertainment"]
            ent_price = round(ent_budget * 0.85)
            ent_name = f"Party Sound System & {req.entertainment}"
            recommendations.append({
                "category": "Entertainment",
                "product_name": ent_name,
                "platform": "Sound & DJ Hub",
                "estimated_price": float(ent_price),
                "quantity": 1,
                "total_price": float(ent_price),
                "reason": f"Provides curated audio and party atmosphere suited for {req.guest_count} guests.",
                "priority": "Medium",
                "product_url": "https://www.amazon.in/s?k=party+speakers",
                "image_url": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=500&auto=format&fit=crop"
            })

        # 5. Accommodation (if needed)
        if need_rooms:
            rooms = req.room_count or 1
            rate = round(allocated.get("Accommodation", req.budget * 0.15) / rooms)
            rate = max(1200, min(rate, 2500))
            tot_rooms = rate * rooms
            recommendations.append({
                "category": "Accommodation",
                "product_name": f"OYO Townhouse Guest Rooms ({rooms} Rooms)",
                "platform": "OYO",
                "estimated_price": float(rate),
                "quantity": rooms,
                "total_price": float(tot_rooms),
                "reason": f"Dedicated stay for outstation guests with complimentary breakfast.",
                "priority": "Medium",
                "product_url": "https://www.oyorooms.com",
                "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=500&auto=format&fit=crop"
            })

        validated = rebalance_recommendations_if_exceeded(req.budget, recommendations)

        return {
            "planner": "party",
            "budget": req.budget,
            "allocated_budget": allocated,
            "recommendations": validated["items"],
            "estimated_total": validated["estimated_total"],
            "remaining_budget": validated["remaining_budget"],
            "event_summary": {
                "event_type": req.event_type,
                "guest_count": req.guest_count,
                "date": req.event_date or "Flexible",
                "location": req.location or "City Center",
                "venue_type": req.venue_type
            },
            "summary": (
                f"Planned {req.event_type} for {req.guest_count} guests within ₹{int(req.budget):,}. "
                f"Balanced across catering, {req.venue_type} venue, {req.decoration_level.lower()} decoration, "
                f"and entertainment."
            ),
            "is_fallback": True
        }

    @classmethod
    async def generate_plan(cls, req: PartyPlannerRequest) -> Dict[str, Any]:
        """Generate smart party budget with Gemini AI and fallback validation."""
        system_instruction, prompt = cls._build_prompt(req)

        ai_response = await gemini_service.generate_text_plan(prompt, system_instruction)
        if ai_response and isinstance(ai_response, dict) and ai_response.get("recommendations"):
            try:
                raw_recs = ai_response.get("recommendations", [])
                validated = rebalance_recommendations_if_exceeded(req.budget, raw_recs)

                # Ensure image & product URLs
                for item in validated["items"]:
                    if not item.get("product_url"):
                        cat = item.get("category", "party").lower()
                        if "catering" in cat or "food" in cat:
                            item["product_url"] = "https://www.swiggy.com"
                        elif "venue" in cat or "accommodation" in cat:
                            item["product_url"] = "https://www.oyorooms.com"
                        else:
                            item["product_url"] = "https://www.amazon.in/s?k=party"
                    if not item.get("image_url"):
                        item["image_url"] = "https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=500&auto=format&fit=crop"

                alloc = ai_response.get("allocated_budget")
                if not isinstance(alloc, dict) or not alloc:
                    alloc = {
                        "Venue": round(req.budget * 0.30, 2),
                        "Catering": round(req.budget * 0.40, 2),
                        "Decoration": round(req.budget * 0.15, 2),
                        "Entertainment": round(req.budget * 0.10, 2),
                        "Miscellaneous": round(req.budget * 0.05, 2)
                    }

                return {
                    "planner": "party",
                    "budget": req.budget,
                    "allocated_budget": alloc,
                    "recommendations": validated["items"],
                    "estimated_total": validated["estimated_total"],
                    "remaining_budget": validated["remaining_budget"],
                    "event_summary": {
                        "event_type": req.event_type,
                        "guest_count": req.guest_count,
                        "date": req.event_date or "Flexible",
                        "location": req.location or "City Center",
                        "venue_type": req.venue_type
                    },
                    "summary": ai_response.get("summary", f"{req.event_type} budget plan for {req.guest_count} guests"),
                    "is_fallback": False
                }
            except Exception as e:
                logger.error(f"Error validating AI party response: {str(e)}. Using fallback.")

        return cls.generate_fallback_plan(req)
