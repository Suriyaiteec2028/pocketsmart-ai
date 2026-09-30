from typing import List, Dict, Any

def format_currency(amount: float, symbol: str = "₹") -> str:
    """Format an amount into Indian/international comma-separated currency representation."""
    if amount is None:
        amount = 0.0
    
    amount_int = int(round(amount))
    sign = "-" if amount_int < 0 else ""
    amount_int = abs(amount_int)
    
    s = str(amount_int)
    if len(s) <= 3:
        formatted = s
    else:
        # Indian numbering system: rightmost 3 digits, then groups of 2
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted = ",".join(groups) + "," + last_three

    return f"{sign}{symbol}{formatted}"

def calculate_budget_totals(budget: float, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Independently calculate total estimated cost and remaining budget.
    Ensures estimated prices, quantities, and totals are numeric and correct.
    """
    total_spent = 0.0
    sanitized_items = []

    for item in recommendations:
        raw_price = item.get("estimated_price", 0)
        try:
            price = float(raw_price)
        except (ValueError, TypeError):
            price = 0.0

        raw_qty = item.get("quantity", 1)
        try:
            qty = max(1, int(raw_qty))
        except (ValueError, TypeError):
            qty = 1

        total_price = price * qty
        total_spent += total_price

        # Update item with confirmed values
        item_copy = dict(item)
        item_copy["estimated_price"] = price
        item_copy["quantity"] = qty
        item_copy["total_price"] = total_price
        sanitized_items.append(item_copy)

    remaining = budget - total_spent

    return {
        "budget": round(budget, 2),
        "estimated_total": round(total_spent, 2),
        "remaining_budget": round(remaining, 2),
        "items": sanitized_items,
        "is_over_budget": remaining < 0,
        "deficit": round(abs(remaining), 2) if remaining < 0 else 0.0
    }

def rebalance_recommendations_if_exceeded(budget: float, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    If recommendations exceed total budget, adjust quantities or scale down
    non-essential items to keep spending within or as close to the budget as possible.
    """
    totals = calculate_budget_totals(budget, recommendations)
    if not totals["is_over_budget"]:
        return totals

    items = list(totals["items"])
    
    # Priority sorting: High > Medium > Low
    priority_order = {"low": 1, "medium": 2, "high": 3}
    
    # Try step 1: Reduce quantities of lower priority items (>1)
    for item in sorted(items, key=lambda x: priority_order.get(str(x.get("priority", "medium")).lower(), 2)):
        if totals["is_over_budget"] and item["quantity"] > 1:
            while item["quantity"] > 1 and totals["is_over_budget"]:
                item["quantity"] -= 1
                item["total_price"] = item["estimated_price"] * item["quantity"]
                totals = calculate_budget_totals(budget, items)
    
    # If still over budget, try step 2: drop lowest priority items until within budget,
    # but keep at least the top priority essentials
    if totals["is_over_budget"] and len(items) > 1:
        kept_items = []
        running_spent = 0.0
        # Sort items with High priority first
        sorted_by_prio = sorted(
            items, 
            key=lambda x: priority_order.get(str(x.get("priority", "medium")).lower(), 2), 
            reverse=True
        )
        for item in sorted_by_prio:
            if running_spent + item["total_price"] <= budget or len(kept_items) == 0:
                kept_items.append(item)
                running_spent += item["total_price"]
        items = kept_items

    return calculate_budget_totals(budget, items)
