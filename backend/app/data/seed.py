"""Seed data for the in-memory repositories.

This mirrors the sample data the static UI ships with, so the Python backend
and the standalone frontend tell the same story. When we move to Postgres,
this becomes a one-off migration / seed script.
"""

from __future__ import annotations

from typing import List

from ..models import Activity, Campaign, Creator, Deal, PlatformStats


def seed_stats() -> PlatformStats:
    return PlatformStats(
        creators_certified=9000,
        brands_active=1200,
        agencies_active=180,
        ai_ads_generated=184000,
        paid_to_creators=240000000,  # ₹24Cr
        avg_roas=5.3,
    )


def seed_creators() -> List[Creator]:
    return [
        Creator(id="1", name="Maya Chen", email="maya@example.com",
                phone="+919800000001", handle="@mayacreates",
                niche="Beauty & Skincare", city="Mumbai", followers="480K",
                engagement="4.8%", match_score=96, avatar="MC", certified=True,
                rate=85000, status="active"),
        Creator(id="2", name="Rohan Mehta", email="rohan@example.com",
                phone="+919800000002", handle="@rohaneats",
                niche="Food & Drinks", city="Delhi", followers="320K",
                engagement="3.2%", match_score=91, avatar="RM", certified=True,
                rate=60000, status="active"),
        Creator(id="3", name="Priya Sharma", email="priya@example.com",
                phone="+919800000003", handle="@priyafit",
                niche="Health & Fitness", city="Bengaluru", followers="610K",
                engagement="5.1%", match_score=88, avatar="PS", certified=False,
                rate=95000, status="active"),
        Creator(id="4", name="Arjun Nair", email="arjun@example.com",
                phone="+919800000004", handle="@arjuntech",
                niche="Phones & Gadgets", city="Hyderabad", followers="270K",
                engagement="2.9%", match_score=84, avatar="AN", certified=True,
                rate=70000, status="active"),
    ]


def seed_deals() -> List[Deal]:
    return [
        Deal(id="d1", title="Glow Face Serum — Video Ad", brand="Glow Labs",
             creator="Maya Chen", status="review", budget=85000, path="video"),
        Deal(id="d2", title="Protein Bar — AI Photo Ads", brand="Fuel Co",
             creator="Rohan Mehta", status="paid", budget=55000, path="ai-static"),
        Deal(id="d3", title="Smart Watch — AI Video Ads", brand="Pulse Gear",
             creator="Arjun Nair", status="filming", budget=160000, path="ai-video"),
        Deal(id="d4", title="Yoga Mat — New Deal", brand="ZenFlow",
             creator="Priya Sharma", status="contract", budget=70000, path="video"),
    ]


def seed_campaigns() -> List[Campaign]:
    return [
        Campaign(id="c1", name="Glow Serum — Festive Push", brand="Glow Labs",
                 creator="Maya Chen", status="live", spend=420000, roas=6.4,
                 ctr=2.8, reach=1840000),
        Campaign(id="c2", name="Protein Bar — Always On", brand="Fuel Co",
                 creator="Rohan Mehta", status="live", spend=280000, roas=4.9,
                 ctr=2.1, reach=1120000),
        Campaign(id="c3", name="Smart Watch — Launch", brand="Pulse Gear",
                 creator="Arjun Nair", status="live", spend=650000, roas=5.7,
                 ctr=3.2, reach=2350000),
        Campaign(id="c4", name="Yoga Mat — Test Batch", brand="ZenFlow",
                 creator="Priya Sharma", status="draft", spend=0, roas=0.0,
                 ctr=0.0, reach=0),
    ]


def seed_activity() -> List[Activity]:
    return [
        Activity(id="a1", type="earning", text="Maya Chen earned ₹900",
                 meta="Glow Labs used her look in an AI ad", time="just now"),
        Activity(id="a2", type="campaign",
                 text="Smart Watch campaign hit 5.7x return",
                 meta="Pulse Gear · live now", time="2 min ago"),
        Activity(id="a3", type="match", text="Fuel Co matched with Rohan Mehta",
                 meta="91% fit · suggested by linc", time="6 min ago"),
        Activity(id="a4", type="delivery",
                 text="Glow Face Serum video delivered",
                 meta="Waiting for brand to check", time="14 min ago"),
        Activity(id="a5", type="earning", text="Arjun Nair earned ₹1,200",
                 meta="Pulse Gear used his look in an AI ad", time="21 min ago"),
    ]
