"""
ad-copy-generator-skill: Client SDK
Generate A/B tested ad copy for Google, Meta, and TikTok with compliance checks.
"""
from __future__ import annotations
from typing import Optional

# Google Search Ad limits
GOOGLE_SEARCH_LIMITS = {"headline": 30, "description": 90}
# Google Shopping limits
GOOGLE_SHOPPING_LIMITS = {"title": 150, "description": 5000}
# Meta (Facebook/Instagram) limits
META_LIMITS = {"primary_text": 125, "headline": 40, "description": 30}
# TikTok limits
TIKTOK_LIMITS = {"ad_text": 100, "call_to_action": 20}

POWER_WORDS = ["exclusive", "proven", "limited", "guaranteed", "free", "instant", "trusted", "best", "new", "save"]
CTA_VARIANTS = ["Shop Now", "Get Yours", "Buy Today", "Order Now", "Claim Offer", "Try It Free", "Learn More", "Start Saving"]

HEADLINE_FRAMES = [
    "{benefit} -- {cta}",
    "{product}: {benefit}",
    "Save {offer} on {product}",
    "{audience} Love {product}",
    "Official {product} Store",
    "New: {product} -- {benefit}",
    "{product} | {offer} | {cta}",
]

DESCRIPTION_FRAMES = [
    "{product} delivers {benefit}. {offer_text} {cta}.",
    "Trusted by {audience}. {benefit}. {offer_text}",
    "Shop {product} -- {benefit}. {cta} for {offer_text}",
    "{benefit}. {product} is the #1 choice for {audience}. {offer_text}",
]

META_PRIMARY_FRAMES = [
    "Tired of {pain_point}? {product} changes everything. {benefit}. {offer_text}",
    "Introducing {product} -- the {audience} solution for {benefit}. {offer_text}",
    "{audience}: stop {pain_point} and start seeing {benefit} with {product}. {offer_text}",
    "This is your sign to try {product}. {benefit}. {offer_text} Shop now.",
]

TIKTOK_FRAMES = [
    "POV: You just discovered {product} and your life changed. {benefit}. {offer_text}",
    "Honest review of {product}: {benefit}. Worth every penny. {offer_text}",
    "Why is no one talking about {product}? {benefit}. {offer_text}",
    "I tried {product} so you do not have to. Result: {benefit}. {offer_text}",
]


class AdCopyClient:
    """
    SDK for generating platform-optimized, A/B tested ad copy variants.
    Enforces character limits and scores copy on best-practice criteria.
    """

    def generate(
        self,
        product_name: str,
        product_description: str = "",
        key_benefits: Optional[list[str]] = None,
        target_audience: str = "customers",
        discount_offer: str = "",
        platform: str = "all",
    ) -> dict:
        """
        Generate ad copy variants for one or all platforms.

        Args:
            product_name:       Product name.
            product_description: Brief description.
            key_benefits:       List of key benefits (first 3 used).
            target_audience:    Target audience description.
            discount_offer:     Offer text (e.g. '30% off' or 'Free Shipping').
            platform:           google_search / google_shopping / meta / tiktok / all.

        Returns:
            dict[platform] -> list of ad copy variants with scores.
        """
        key_benefits = key_benefits or ["premium quality", "fast results", "trusted by thousands"]
        benefit = key_benefits[0] if key_benefits else "premium quality"
        benefit2 = key_benefits[1] if len(key_benefits) > 1 else benefit
        benefit3 = key_benefits[2] if len(key_benefits) > 2 else benefit
        offer_text = f"{discount_offer}!" if discount_offer else "Shop now."
        pain_point = self._infer_pain_point(product_description, target_audience)

        ctx = {
            "product": product_name, "benefit": benefit, "benefit2": benefit2,
            "benefit3": benefit3, "offer": discount_offer or "exclusive deals",
            "offer_text": offer_text, "audience": target_audience,
            "pain_point": pain_point, "cta": CTA_VARIANTS[0],
        }

        ads = {}
        platforms = ["google_search", "google_shopping", "meta", "tiktok"] if platform == "all" else [platform]

        for p in platforms:
            if p == "google_search":
                ads[p] = self._google_search(ctx)
            elif p == "google_shopping":
                ads[p] = self._google_shopping(ctx, product_description)
            elif p == "meta":
                ads[p] = self._meta(ctx)
            elif p == "tiktok":
                ads[p] = self._tiktok(ctx)

        return {"product": product_name, "platform": platform, "ads": ads}

    def _google_search(self, ctx: dict) -> list[dict]:
        variants = []
        for i, (hf, df) in enumerate(zip(HEADLINE_FRAMES[:4], DESCRIPTION_FRAMES)):
            for cta in CTA_VARIANTS[:2]:
                ctx["cta"] = cta
                try:
                    h = hf.format(**ctx)[:GOOGLE_SEARCH_LIMITS["headline"]]
                    d = df.format(**ctx)[:GOOGLE_SEARCH_LIMITS["description"]]
                    variants.append(self._build_variant("google_search", {"headline": h, "description": d}, GOOGLE_SEARCH_LIMITS))
                except KeyError:
                    continue
                if len(variants) >= 3:
                    break
            if len(variants) >= 3:
                break
        return variants

    def _google_shopping(self, ctx: dict, description: str) -> list[dict]:
        titles = [
            f"{ctx['product']} | {ctx['benefit']}"[:GOOGLE_SHOPPING_LIMITS["title"]],
            f"{ctx['product']} - {ctx['offer_text']}"[:GOOGLE_SHOPPING_LIMITS["title"]],
            f"Official {ctx['product']} Store | {ctx['benefit2']}"[:GOOGLE_SHOPPING_LIMITS["title"]],
        ]
        desc_base = description or f"{ctx['product']} -- {ctx['benefit']}. {ctx['benefit2']}. {ctx['offer_text']}"
        variants = []
        for title in titles:
            variants.append(self._build_variant("google_shopping", {
                "title": title,
                "description": desc_base[:GOOGLE_SHOPPING_LIMITS["description"]],
            }, GOOGLE_SHOPPING_LIMITS))
        return variants

    def _meta(self, ctx: dict) -> list[dict]:
        variants = []
        for i, frame in enumerate(META_PRIMARY_FRAMES[:3]):
            try:
                primary = frame.format(**ctx)[:META_LIMITS["primary_text"]]
                headline = f"{ctx['product']} -- {ctx['benefit']}"[:META_LIMITS["headline"]]
                desc = f"{ctx['offer_text']}"[:META_LIMITS["description"]]
                variants.append(self._build_variant("meta", {
                    "primary_text": primary, "headline": headline, "description": desc,
                    "call_to_action": CTA_VARIANTS[i % len(CTA_VARIANTS)],
                }, META_LIMITS))
            except KeyError:
                continue
        return variants

    def _tiktok(self, ctx: dict) -> list[dict]:
        variants = []
        for frame in TIKTOK_FRAMES[:3]:
            try:
                text = frame.format(**ctx)[:TIKTOK_LIMITS["ad_text"]]
                variants.append(self._build_variant("tiktok", {
                    "ad_text": text,
                    "call_to_action": CTA_VARIANTS[len(variants) % len(CTA_VARIANTS)],
                }, TIKTOK_LIMITS))
            except KeyError:
                continue
        return variants

    def _build_variant(self, platform: str, fields: dict, limits: dict) -> dict:
        char_counts = {k: len(v) for k, v in fields.items()}
        compliance = {k: len(v) <= limits.get(k, 9999) for k, v in fields.items()}
        score = self._score(fields)
        return {
            "platform": platform,
            "copy": fields,
            "char_counts": char_counts,
            "limits": limits,
            "compliant": all(compliance.values()),
            "quality_score": score,
        }

    @staticmethod
    def _score(fields: dict) -> float:
        all_text = " ".join(str(v) for v in fields.values()).lower()
        score = 0.5
        for word in POWER_WORDS:
            if word in all_text:
                score += 0.05
        if any(c.isdigit() for c in all_text): score += 0.08
        if "!" in all_text: score += 0.03
        if "?" in all_text: score += 0.02
        for cta in ["shop", "buy", "get", "claim", "try", "save", "order"]:
            if cta in all_text: score += 0.05
        return round(min(score, 1.0), 2)

    @staticmethod
    def _infer_pain_point(description: str, audience: str) -> str:
        desc_lower = description.lower()
        if "skin" in desc_lower or "beauty" in desc_lower: return "dull skin"
        if "fitness" in desc_lower or "workout" in desc_lower: return "slow progress"
        if "sleep" in desc_lower: return "poor sleep"
        if "clean" in desc_lower or "organic" in desc_lower: return "harsh chemicals"
        return "ordinary results"
