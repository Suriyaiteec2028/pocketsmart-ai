import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

from app.config import settings
from app.schemas.jewelry import JewelryPlannerRequest
from app.services.gemini_service import gemini_service
from app.services.platforms import amazon_adapter, flipkart_adapter
from app.utils.budget import calculate_budget_totals, rebalance_recommendations_if_exceeded

logger = logging.getLogger("pocketsmart.jewelry")

JEWELRY_FALLBACK_DATABASE = [
    {
        "name": "Zaveri Pearls Kundan & Pearl Royal Choker Necklace Set",
        "category": "Set",
        "type": "Set",
        "platform": "Amazon",
        "style": "Traditional",
        "material": "Gold Plated",
        "color": "Gold",
        "occasion": ["Wedding", "Engagement", "Festival"],
        "price": 949,
        "reason": "Classic Kundan craftsmanship with teardrop pearls that adds grandeur to traditional ethnic wear.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=zaveri+pearls+necklace+set"
    },
    {
        "name": "GIVA 925 Sterling Silver Classic Solitaire Zircon Stud Earrings",
        "category": "Earrings",
        "type": "Earrings",
        "platform": "Amazon",
        "style": "Minimal",
        "material": "Silver",
        "color": "Silver",
        "occasion": ["Casual", "Office", "Party", "Gift"],
        "price": 1499,
        "reason": "Brilliant solitaire sparkle in sterling silver, offering refined elegance for western and fusion outfits.",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=giva+silver+earrings"
    },
    {
        "name": "Yellow Chimes Austrian Crystal Elegant Drop Earrings",
        "category": "Earrings",
        "type": "Earrings",
        "platform": "Amazon",
        "style": "Elegant",
        "material": "Silver",
        "color": "Silver",
        "occasion": ["Party", "Engagement", "Birthday", "Wedding"],
        "price": 699,
        "reason": "Faceted Austrian crystal cascading drops that catch indoor lighting beautifully.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=yellow+chimes+crystal+earrings"
    },
    {
        "name": "Sukkhi Regal Gold Plated Wedding Choker Necklace Set",
        "category": "Necklace",
        "type": "Necklace",
        "platform": "Flipkart",
        "style": "Luxury",
        "material": "Gold Plated",
        "color": "Gold",
        "occasion": ["Wedding", "Engagement"],
        "price": 799,
        "reason": "Intricate bridal gold-plated detailing designed to elevate rich silk sarees and lehengas.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&auto=format&fit=crop",
        "product_url": "https://www.flipkart.com/search?q=sukkhi+necklace"
    },
    {
        "name": "Shining Diva Fashion Oxidised Silver Tribal Choker Necklace",
        "category": "Necklace",
        "type": "Necklace",
        "platform": "Amazon",
        "style": "Traditional",
        "material": "Silver",
        "color": "Silver",
        "occasion": ["Festival", "Casual", "Party"],
        "price": 499,
        "reason": "Bohemian oxidized silver finish with intricate floral motifs, perfect with cotton and linen kurtas.",
        "image_url": "https://images.unsplash.com/photo-1611591475806-231a4a49c4be?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=oxidised+silver+necklace"
    },
    {
        "name": "GIVA 925 Sterling Silver Rose Gold Adjustable Tennis Bracelet",
        "category": "Bracelet",
        "type": "Bracelet",
        "platform": "Amazon",
        "style": "Modern",
        "material": "Rose Gold",
        "color": "Rose Gold",
        "occasion": ["Gift", "Birthday", "Party", "Office"],
        "price": 1999,
        "reason": "Delicate rose gold tennis chain with embedded cubic zirconia providing subtle luxury.",
        "image_url": "https://images.unsplash.com/photo-1611591475152-47eac9c5bfee?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=giva+rose+gold+bracelet"
    },
    {
        "name": "Clara 925 Sterling Silver Solitaire Adjustable Finger Ring",
        "category": "Ring",
        "type": "Ring",
        "platform": "Amazon",
        "style": "Modern",
        "material": "Silver",
        "color": "Silver",
        "occasion": ["Engagement", "Casual", "Office", "Party"],
        "price": 1299,
        "reason": "Timeless solitaire ring setting in hallmarked sterling silver for everyday or evening wear.",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&auto=format&fit=crop",
        "product_url": "https://www.amazon.in/s?k=clara+silver+ring"
    },
    {
        "name": "Karatcart Traditional Royal Peacock Kada Bangles (Set of 2)",
        "category": "Bangles",
        "type": "Bangles",
        "platform": "Flipkart",
        "style": "Traditional",
        "material": "Gold Plated",
        "color": "Gold",
        "occasion": ["Wedding", "Festival"],
        "price": 899,
        "reason": "Antique gold finish Kada with embossed peacock and ruby-red enamel accents.",
        "image_url": "https://images.unsplash.com/photo-1611591475152-47eac9c5bfee?w=500&auto=format&fit=crop",
        "product_url": "https://www.flipkart.com/search?q=kada+bangles"
    }
]

def extract_dominant_colors_from_image(image_path: Path) -> List[str]:
    """Extract dominant color names from local image using PIL color quantization."""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize((50, 50))
        
        # Get palette of 4 colors
        quantized = img.quantize(colors=4)
        palette = quantized.getpalette()[:12] # 4 colors * 3 (RGB)
        
        color_names = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i+1], palette[i+2]
            # Simple color classifier
            if r > 180 and g > 180 and b > 180:
                color_names.append("Ivory / White")
            elif r < 50 and g < 50 and b < 50:
                color_names.append("Deep Black / Charcoal")
            elif r > 160 and g < 70 and b < 70:
                color_names.append("Crimson Red")
            elif b > 140 and r < 80 and g < 100:
                color_names.append("Royal Navy Blue")
            elif g > 120 and r < 90 and b < 90:
                color_names.append("Emerald Green")
            elif r > 180 and g > 140 and b < 80:
                color_names.append("Warm Gold / Ochre")
            elif r > 180 and g < 130 and b > 140:
                color_names.append("Magenta / Pink")
            elif abs(r - g) < 20 and abs(g - b) < 20:
                color_names.append("Muted Silver / Grey")
            else:
                color_names.append("Rich Jewel Tone")

        # Deduplicate preserving order
        unique_colors = list(dict.fromkeys(color_names))
        return unique_colors[:3]
    except Exception as e:
        logger.warning(f"Could not extract colors from image: {e}")
        return ["Navy Blue", "Silver Accents"]

class JewelryService:
    @staticmethod
    def _build_prompt(req: JewelryPlannerRequest) -> tuple[str, str]:
        system_instruction = (
            "You are PocketSmart AI, an expert jewelry styling and budget assistant. "
            "Analyze the user's budget, occasion, requested jewelry type, style preferences, outfit description, "
            "and optional outfit image. "
            "CRITICAL RULES:\n"
            "1. You MUST NEVER exceed the user's total budget.\n"
            "2. In outfit_analysis, describe: dominant_colors, style, recommended_tones, and interpretation.\n"
            "3. Recommend pieces that harmoniously match the outfit colors, neckline, and occasion.\n"
            "4. For each item provide: product_name, category, type, style, material, estimated_price, quantity (1), total_price, platform, reason, priority, product_url.\n"
            "5. Return ONLY valid JSON matching the exact schema."
        )

        user_content = {
            "budget": req.budget,
            "currency": req.currency,
            "occasion": req.occasion,
            "jewelry_type": req.jewelry_type,
            "preferred_style": req.preferred_style,
            "preferred_material": req.preferred_material,
            "preferred_color": req.preferred_color,
            "outfit_description": req.outfit_description or "Not specified",
            "has_image": bool(req.image_url)
        }

        prompt = (
            f"Generate jewelry recommendations based on the following outfit & budget requirements:\n"
            f"{json.dumps(user_content, indent=2)}\n\n"
            f"Output JSON Schema:\n"
            f"{{\n"
            f'  "planner": "jewelry",\n'
            f'  "budget": {req.budget},\n'
            f'  "outfit_analysis": {{\n'
            f'    "dominant_colors": ["color1", "color2"],\n'
            f'    "style": "traditional / elegant / modern",\n'
            f'    "recommended_tones": ["Silver / White Gold", "Pearl"],\n'
            f'    "interpretation": "Explanation of outfit vibe and matching guidance"\n'
            f'  }},\n'
            f'  "recommendations": [\n'
            f'    {{\n'
            f'      "category": "Earrings",\n'
            f'      "product_name": "Product Name",\n'
            f'      "type": "Earrings",\n'
            f'      "style": "Elegant",\n'
            f'      "material": "Silver",\n'
            f'      "estimated_price": 1500,\n'
            f'      "quantity": 1,\n'
            f'      "total_price": 1500,\n'
            f'      "platform": "Amazon",\n'
            f'      "reason": "Why this matches the outfit perfectly",\n'
            f'      "priority": "High",\n'
            f'      "product_url": "https://www.amazon.in/s?k=earrings"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "summary": "Overall jewelry recommendation summary"\n'
            f"}}\n"
            f"Ensure recommendations stay strictly within ₹{req.budget}. Return ONLY JSON."
        )
        return system_instruction, prompt

    @classmethod
    def generate_fallback_plan(cls, req: JewelryPlannerRequest) -> Dict[str, Any]:
        """Smart fallback jewelry plan using local color extraction & curated catalog."""
        logger.info(f"Generating realistic fallback jewelry plan for occasion: {req.occasion}, budget: {req.budget}")
        
        # Analyze image or outfit description
        dominant_colors = []
        if req.image_url:
            # Resolve image file
            clean_rel = req.image_url.lstrip("/")
            local_path = settings.BASE_DIR / clean_rel
            if local_path.exists():
                dominant_colors = extract_dominant_colors_from_image(local_path)
        
        if not dominant_colors:
            if req.outfit_description:
                desc_lower = req.outfit_description.lower()
                if "blue" in desc_lower:
                    dominant_colors.append("Navy / Royal Blue")
                if "red" in desc_lower or "maroon" in desc_lower:
                    dominant_colors.append("Crimson / Maroon")
                if "green" in desc_lower:
                    dominant_colors.append("Emerald Green")
                if "gold" in desc_lower or "yellow" in desc_lower:
                    dominant_colors.append("Gold / Mustard")
                if "silver" in desc_lower or "white" in desc_lower:
                    dominant_colors.append("Silver / Pearl White")
                if "black" in desc_lower:
                    dominant_colors.append("Classic Black")
            
            if not dominant_colors:
                dominant_colors = ["Midnight Blue", "Silver Sheen"]

        # Suggested tones based on colors
        recommended_tones = ["Silver", "Platinum Finish", "Cubic Zirconia"]
        color_str = " ".join(dominant_colors).lower()
        if any(c in color_str for c in ["gold", "red", "maroon", "green"]):
            recommended_tones = ["Yellow Gold", "Antique Brass", "Warm Kundan"]
        elif "rose" in color_str or "pink" in color_str:
            recommended_tones = ["Rose Gold", "Blush Pearl", "Champagne Stone"]

        outfit_analysis = {
            "dominant_colors": dominant_colors,
            "style": f"{req.preferred_style} with {req.occasion} prominence",
            "recommended_tones": recommended_tones,
            "interpretation": (
                f"Your outfit features prominent {', '.join(dominant_colors)} accents. "
                f"We paired it with {', '.join(recommended_tones)} jewelry pieces to balance and complement the neckline and silhouette."
            )
        }

        # Filter candidate items
        type_filter = req.jewelry_type.lower()
        candidates = []
        for item in JEWELRY_FALLBACK_DATABASE:
            matches_type = (type_filter == "any") or (type_filter in item["type"].lower())
            if matches_type:
                candidates.append(item)
        if not candidates:
            candidates = JEWELRY_FALLBACK_DATABASE

        # Fit within budget
        selected = []
        running_spent = 0.0
        for c in sorted(candidates, key=lambda x: x["price"]):
            if running_spent + c["price"] <= req.budget * 0.98 or len(selected) == 0:
                rec_item = {
                    "category": c["category"],
                    "product_name": c["name"],
                    "type": c["type"],
                    "style": c["style"],
                    "material": c["material"],
                    "platform": c["platform"],
                    "estimated_price": float(c["price"]),
                    "quantity": 1,
                    "total_price": float(c["price"]),
                    "reason": f"{c['reason']} Pairs with your {', '.join(dominant_colors)} palette.",
                    "priority": "High" if len(selected) == 0 else "Medium",
                    "product_url": c["product_url"],
                    "image_url": c["image_url"]
                }
                selected.append(rec_item)
                running_spent += c["price"]

        validated = rebalance_recommendations_if_exceeded(req.budget, selected)

        return {
            "planner": "jewelry",
            "budget": req.budget,
            "outfit_analysis": outfit_analysis,
            "recommendations": validated["items"],
            "estimated_total": validated["estimated_total"],
            "remaining_budget": validated["remaining_budget"],
            "summary": (
                f"Curated {len(validated['items'])} matching jewelry selections for your {req.occasion} "
                f"within ₹{int(req.budget):,}. Harmonized with {', '.join(dominant_colors)} tones."
            ),
            "is_fallback": True
        }

    @classmethod
    async def generate_plan(cls, req: JewelryPlannerRequest) -> Dict[str, Any]:
        """Generate multimodal jewelry recommendation using Gemini if configured, else fallback."""
        system_instruction, prompt = cls._build_prompt(req)

        ai_response = None
        # Multimodal request if image is provided
        if req.image_url:
            clean_rel = req.image_url.lstrip("/")
            local_path = settings.BASE_DIR / clean_rel
            if local_path.exists():
                ext = local_path.suffix.lower()
                mime = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
                ai_response = await gemini_service.generate_multimodal_plan(
                    prompt=prompt,
                    image_path=local_path,
                    mime_type=mime,
                    system_instruction=system_instruction
                )

        if not ai_response:
            ai_response = await gemini_service.generate_text_plan(prompt, system_instruction)

        if ai_response and isinstance(ai_response, dict) and ai_response.get("recommendations"):
            try:
                raw_recs = ai_response.get("recommendations", [])
                validated = rebalance_recommendations_if_exceeded(req.budget, raw_recs)

                # Ensure image & product URLs
                for item in validated["items"]:
                    if not item.get("product_url"):
                        query = item.get("product_name", "jewelry")
                        item["product_url"] = f"https://www.amazon.in/s?k={query}"
                    if not item.get("image_url"):
                        item["image_url"] = "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500&auto=format&fit=crop"

                outfit_analysis = ai_response.get("outfit_analysis", {
                    "dominant_colors": ["Silver", "Navy"],
                    "style": req.preferred_style,
                    "recommended_tones": ["Silver", "Cubic Zirconia"],
                    "interpretation": "Harmonized to complement the outfit palette and occasion."
                })

                return {
                    "planner": "jewelry",
                    "budget": req.budget,
                    "outfit_analysis": outfit_analysis,
                    "recommendations": validated["items"],
                    "estimated_total": validated["estimated_total"],
                    "remaining_budget": validated["remaining_budget"],
                    "summary": ai_response.get("summary", f"Jewelry curated for {req.occasion}"),
                    "is_fallback": False
                }
            except Exception as e:
                logger.error(f"Error validating AI jewelry response: {str(e)}. Using fallback.")

        return cls.generate_fallback_plan(req)
