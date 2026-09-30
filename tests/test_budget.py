import pytest
from app.utils.budget import calculate_budget_totals, rebalance_recommendations_if_exceeded, format_currency

def test_correct_total_and_remaining_calculation():
    budget = 50000.0
    items = [
        {"product_name": "Sofa", "estimated_price": 20000, "quantity": 1, "priority": "High"},
        {"product_name": "Table", "estimated_price": 8000, "quantity": 1, "priority": "Medium"},
        {"product_name": "Lighting", "estimated_price": 5000, "quantity": 1, "priority": "Medium"},
        {"product_name": "Decor", "estimated_price": 7000, "quantity": 1, "priority": "Low"}
    ]
    result = calculate_budget_totals(budget, items)
    assert result["estimated_total"] == 40000.0
    assert result["remaining_budget"] == 10000.0
    assert result["is_over_budget"] is False

def test_budget_overflow_and_rebalance():
    budget = 30000.0
    # Total would be 40000, which exceeds 30000
    items = [
        {"product_name": "Sofa", "estimated_price": 20000, "quantity": 1, "priority": "High"},
        {"product_name": "Table", "estimated_price": 8000, "quantity": 1, "priority": "Medium"},
        {"product_name": "Luxury Vase", "estimated_price": 12000, "quantity": 1, "priority": "Low"}
    ]
    rebalanced = rebalance_recommendations_if_exceeded(budget, items)
    assert rebalanced["estimated_total"] <= budget
    assert rebalanced["remaining_budget"] >= 0.0

def test_zero_or_negative_budget_calculation():
    budget = 0.0
    items = [{"product_name": "Lamp", "estimated_price": 1000, "quantity": 1}]
    result = calculate_budget_totals(budget, items)
    assert result["is_over_budget"] is True
    assert result["remaining_budget"] == -1000.0

def test_format_currency_inr():
    assert format_currency(100000) == "₹1,00,000"
    assert format_currency(5000) == "₹5,000"
    assert format_currency(0) == "₹0"
