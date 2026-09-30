import json
import logging
from typing import Dict, Any, List
from app.schemas.home import HomePlannerRequest
from app.services.gemini_service import gemini_service
from app.services.platforms import amazon_adapter, flipkart_adapter, ikea_adapter
from app.utils.budget import calculate_budget_totals, rebalance_recommendations_if_exceeded

logger = logging.getLogger("pocketsmart.home")

HOME_FALLBACK_DATABASE = {
    "living_room": [
        {"name": "Solimo Fabric 3-Seater Sofa (Grey)", "category": "Sofa", "platform": "Amazon", "base_ratio": 0.35, "min_price": 12000, "priority": "High", "reason": "Comfortable 3-seater suited for everyday family seating and modern aesthetic.", "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=sofa+3+seater"},
        {"name": "IKEA LACK Minimalist Coffee Table", "category": "Coffee Table", "platform": "IKEA", "base_ratio": 0.06, "min_price": 1490, "priority": "Medium", "reason": "Space-saving clean design that pairs well with modern living spaces.", "image_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=500&auto=format&fit=crop", "product_url": "https://www.ikea.com/in/en/search/?q=coffee+table"},
        {"name": "Wipro Smart LED Warm White Floor Lamp", "category": "Lighting", "platform": "Amazon", "base_ratio": 0.05, "min_price": 1800, "priority": "Medium", "reason": "Ambient warm light perfect for cozy living room atmosphere.", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=floor+lamp"},
        {"name": "Urban Ladder Engineered Wood TV Unit", "category": "TV Unit", "platform": "Flipkart", "base_ratio": 0.12, "min_price": 4500, "priority": "High", "reason": "Offers streamlined media storage with cable management.", "image_url": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=500&auto=format&fit=crop", "product_url": "https://www.flipkart.com/search?q=tv+unit"},
        {"name": "Status Flat Weave Textured Jute Center Rug (5x7 ft)", "category": "Rug", "platform": "Amazon", "base_ratio": 0.05, "min_price": 1999, "priority": "Low", "reason": "Adds texture and warmth to center living space.", "image_url": "https://images.unsplash.com/photo-1600121848594-d8644e57abab?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=living+room+rug"},
        {"name": "Safal Wall Art Canvas Framed Painting (Set of 3)", "category": "Wall Decor", "platform": "Amazon", "base_ratio": 0.03, "min_price": 999, "priority": "Low", "reason": "Cost-effective artistic focal point for your accent wall.", "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=wall+art"}
    ],
    "bedroom": [
        {"name": "Wakefit Queen Size Engineered Wood Bed with Storage", "category": "Bed", "platform": "Amazon", "base_ratio": 0.32, "min_price": 11500, "priority": "High", "reason": "Durable bed frame with hydraulic storage to maximize space efficiency.", "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=queen+size+bed"},
        {"name": "Sleepyhead Orthopedic High Density Foam Mattress", "category": "Mattress", "platform": "Flipkart", "base_ratio": 0.20, "min_price": 7500, "priority": "High", "reason": "Ergonomic back support ensuring restful sleep quality.", "image_url": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=500&auto=format&fit=crop", "product_url": "https://www.flipkart.com/search?q=orthopedic+mattress"},
        {"name": "Amazon Basics 2-Door Wardrobe with Hanging Rod", "category": "Wardrobe", "platform": "Amazon", "base_ratio": 0.18, "min_price": 6500, "priority": "High", "reason": "Sturdy wardrobe with dedicated hanging space and internal shelving.", "image_url": "https://images.unsplash.com/photo-1558997519-83ea9252def8?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=wardrobe"},
        {"name": "IKEA TERTIAL Bedside Adjustable Reading Lamp", "category": "Lighting", "platform": "IKEA", "base_ratio": 0.04, "min_price": 1290, "priority": "Medium", "reason": "Directed task lighting ideal for bedtime reading.", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop", "product_url": "https://www.ikea.com/in/en/search/?q=work+lamp"},
        {"name": "Story@Home 100% Blackout Privacy Curtains (Pair)", "category": "Curtains", "platform": "Amazon", "base_ratio": 0.04, "min_price": 1299, "priority": "Medium", "reason": "Blocks harsh sunlight and enhances bedroom insulation.", "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=blackout+curtains"}
    ],
    "kitchen": [
        {"name": "Kuber Industries Multipurpose Kitchen Storage Organizer", "category": "Storage", "platform": "Amazon", "base_ratio": 0.08, "min_price": 1100, "priority": "High", "reason": "Organizes spice jars and pantry goods with neat tiering.", "image_url": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=kitchen+organizer"},
        {"name": "Philips Astra Deco Smart Under-Cabinet LED Strip Light", "category": "Lighting", "platform": "Flipkart", "base_ratio": 0.06, "min_price": 999, "priority": "Medium", "reason": "Provides bright, shadow-free counter illumination for meal prep.", "image_url": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=500&auto=format&fit=crop", "product_url": "https://www.flipkart.com/search?q=led+strip+light"},
        {"name": "Pigeon by Stovekraft 3-Burner Glass Top Gas Stove", "category": "Appliances", "platform": "Flipkart", "base_ratio": 0.15, "min_price": 2899, "priority": "High", "reason": "Reliable, easy-to-clean toughened glass cooking hob.", "image_url": "https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=500&auto=format&fit=crop", "product_url": "https://www.flipkart.com/search?q=gas+stove"}
    ],
    "dining_room": [
        {"name": "IKEA JOKKMOKK Solid Pine Table and 4 Chairs", "category": "Dining items", "platform": "IKEA", "base_ratio": 0.30, "min_price": 11990, "priority": "High", "reason": "Solid pine dining set that ages beautifully with timeless Nordic charm.", "image_url": "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=500&auto=format&fit=crop", "product_url": "https://www.ikea.com/in/en/search/?q=dining+table+set"},
        {"name": "Modern Industrial Geometric Pendant Ceiling Lamp", "category": "Lighting", "platform": "Amazon", "base_ratio": 0.05, "min_price": 1499, "priority": "Medium", "reason": "Creates a warm focal glow right above the dining surface.", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=pendant+light"}
    ],
    "study_room": [
        {"name": "Green Soul Ergonomic High-Back Mesh Study Chair", "category": "Study Chair", "platform": "Amazon", "base_ratio": 0.15, "min_price": 5499, "priority": "High", "reason": "Breathable mesh and lumbar support for extended productivity sessions.", "image_url": "https://images.unsplash.com/photo-1580481077195-c22e4b31a238?w=500&auto=format&fit=crop", "product_url": "https://www.amazon.in/s?k=ergonomic+chair"},
        {"name": "DeckUp Plank Engineered Wood Study Desk", "category": "Study Table", "platform": "Flipkart", "base_ratio": 0.12, "min_price": 3899, "priority": "High", "reason": "Spacious desk with drawer storage for stationery and laptop setup.", "image_url": "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=500&auto=format&fit=crop", "product_url": "https://www.flipkart.com/search?q=study+desk"},
        {"name": "IKEA TERTIAL Work Lamp", "category": "Lighting", "platform": "IKEA", "base_ratio": 0.03, "min_price": 1290, "priority": "Medium", "reason": "Direct focus lighting for comfortable reading and study work.", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500&auto=format&fit=crop", "product_url": "https://www.ikea.com/in/en/search/?q=work+lamp"}
    ]
}

class HomeService:
    @staticmethod
    def _build_prompt(req: HomePlannerRequest) -> tuple[str, str]:
        system_instruction = (
            "You are PocketSmart AI, an expert home interior budget planner. "
            "Your mission is to intelligently divide the user's budget across their requested rooms "
            "and recommend realistic, value-for-money furniture, lighting, and decor products from platforms "
            "like Amazon, Flipkart, and IKEA. "
            "CRITICAL RULES:\n"
            "1. You MUST NEVER exceed the user's total budget. The sum of (estimated_price * quantity) of all recommendations must be <= budget.\n"
            "2. Structure output as valid JSON matching the exact schema specified.\n"
            "3. Provide realistic Indian Rupee (INR) estimated prices.\n"
            "4. For each recommendation include: category, product_name, platform, estimated_price, quantity, total_price, reason, priority (High/Medium/Low), product_url.\n"
            "5. Explain why each item is recommended and how it fits the requested style and budget."
        )

        user_content = {
            "total_budget": req.budget,
            "currency": req.currency,
            "home_type": req.home_type,
            "selected_rooms": req.rooms,
            "room_item_preferences": {r: [it.model_dump() for it in items] for r, items in req.room_items.items()} if req.room_items else {},
            "overall_style": req.overall_style,
            "allocation_preference": req.budget_allocation_preference,
            "additional_requirements": req.additional_requirements or "None",
            "desired_output_schema": {
                "planner": "home",
                "budget": req.budget,
                "allocated_budget": {room: 0 for room in req.rooms},
                "recommendations": [
                    {
                        "category": "Sofa",
                        "product_name": "Product Name",
                        "platform": "Amazon",
                        "estimated_price": 15000,
                        "quantity": 1,
                        "total_price": 15000,
                        "reason": "Why this matches requirements",
                        "priority": "High",
                        "product_url": "https://www.amazon.in/s?k=sofa"
                    }
                ],
                "remaining_budget": 0,
                "summary": "Brief summary of the interior budget allocation"
            }
        }

        prompt = (
            f"Generate a smart home interior budget plan strictly in JSON.\n"
            f"Input Data:\n{json.dumps(user_content, indent=2)}\n\n"
            f"Remember: The total sum of all items MUST NOT exceed {req.budget}. "
            f"Return ONLY valid JSON."
        )
        return system_instruction, prompt

    @classmethod
    def generate_fallback_plan(cls, req: HomePlannerRequest) -> Dict[str, Any]:
        """Deterministic, realistic fallback plan generator when AI service is unavailable."""
        logger.info(f"Generating realistic fallback home plan for budget: {req.budget}")
        selected_rooms = [r.lower().replace(" ", "_") for r in req.rooms]
        num_rooms = len(selected_rooms) or 1
        
        # Budget allocation across selected rooms
        allocated_budget: Dict[str, float] = {}
        # Dynamic room weights
        weights = {
            "living_room": 0.40,
            "bedroom": 0.35,
            "kitchen": 0.15,
            "dining_room": 0.15,
            "study_room": 0.15,
            "balcony": 0.08,
            "bathroom": 0.08,
            "other": 0.10
        }
        total_weight = sum(weights.get(r, 0.10) for r in selected_rooms) or 1.0
        for r in req.rooms:
            key = r.lower().replace(" ", "_")
            w = weights.get(key, 0.10)
            allocated_budget[r] = round((w / total_weight) * req.budget, 2)

        recommendations: List[Dict[str, Any]] = []
        running_spent = 0.0
        
        # Room by room, select candidate items matching budget
        for r in req.rooms:
            key = r.lower().replace(" ", "_")
            room_alloc = allocated_budget.get(r, req.budget / num_rooms)
            candidates = HOME_FALLBACK_DATABASE.get(key, HOME_FALLBACK_DATABASE["living_room"])
            
            # Select items that fit inside the room budget
            for c in candidates:
                est_price = min(round(room_alloc * c["base_ratio"]), c["min_price"] * 2)
                est_price = max(c["min_price"], est_price)
                if running_spent + est_price <= req.budget * 0.96:
                    rec_item = {
                        "category": c["category"],
                        "product_name": c["name"],
                        "platform": c["platform"],
                        "estimated_price": float(est_price),
                        "quantity": 1,
                        "total_price": float(est_price),
                        "reason": f"{c['reason']} Matches your {req.overall_style} style and fits within the {r} allocation.",
                        "priority": c["priority"],
                        "product_url": c["product_url"],
                        "image_url": c.get("image_url", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop")
                    }
                    recommendations.append(rec_item)
                    running_spent += est_price

        # Check and recalculate budget totals
        validated = rebalance_recommendations_if_exceeded(req.budget, recommendations)

        return {
            "planner": "home",
            "budget": req.budget,
            "allocated_budget": allocated_budget,
            "recommendations": validated["items"],
            "estimated_total": validated["estimated_total"],
            "remaining_budget": validated["remaining_budget"],
            "summary": (
                f"We balanced your ₹{int(req.budget):,} budget across {len(req.rooms)} rooms "
                f"({', '.join(req.rooms)}) focusing on {req.overall_style} design and "
                f"{req.budget_allocation_preference.lower()} priority."
            ),
            "is_fallback": True
        }

    @classmethod
    async def generate_plan(cls, req: HomePlannerRequest) -> Dict[str, Any]:
        """Coordinate AI generation with strict validation and safe fallback."""
        system_instruction, prompt = cls._build_prompt(req)

        ai_response = await gemini_service.generate_text_plan(prompt, system_instruction)
        
        # If AI successfully generated a response with recommendations
        if ai_response and isinstance(ai_response, dict) and ai_response.get("recommendations"):
            try:
                raw_recs = ai_response.get("recommendations", [])
                validated = rebalance_recommendations_if_exceeded(req.budget, raw_recs)

                # Ensure image URLs or platform links are populated
                for item in validated["items"]:
                    if not item.get("product_url"):
                        query = item.get("product_name", item.get("category", "home"))
                        item["product_url"] = f"https://www.amazon.in/s?k={query}"
                    if not item.get("image_url"):
                        item["image_url"] = "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500&auto=format&fit=crop"

                alloc = ai_response.get("allocated_budget")
                if not isinstance(alloc, dict) or not alloc:
                    alloc = {r: round(req.budget / len(req.rooms), 2) for r in req.rooms}

                return {
                    "planner": "home",
                    "budget": req.budget,
                    "allocated_budget": alloc,
                    "recommendations": validated["items"],
                    "estimated_total": validated["estimated_total"],
                    "remaining_budget": validated["remaining_budget"],
                    "summary": ai_response.get("summary", f"Smart home plan generated for {req.home_type}"),
                    "is_fallback": False
                }
            except Exception as e:
                logger.error(f"Error validating AI home response: {str(e)}. Using fallback.")

        # If Gemini is not configured or failed validation, use realistic fallback
        return cls.generate_fallback_plan(req)
