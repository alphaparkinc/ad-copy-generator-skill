"""
example_usage.py -- Demonstrates the AdCopyClient SDK.
"""
from client import AdCopyClient

def main():
    client = AdCopyClient()

    print("[Ad Copy Generator -- All Platforms]")
    result = client.generate(
        product_name="HydraGlow Vitamin C Serum",
        product_description="A lightweight vitamin C serum that brightens skin, fades dark spots, and boosts collagen.",
        key_benefits=["Brightens skin in 14 days", "Fades dark spots", "Boosts collagen naturally"],
        target_audience="women 25-45 who care about skincare",
        discount_offer="30% off",
        platform="all",
    )

    for platform, variants in result["ads"].items():
        print(f"\n{'='*50}")
        print(f"PLATFORM: {platform.upper()}")
        for i, v in enumerate(variants, 1):
            print(f"  Variant {i} [Score: {v['quality_score']}] [Compliant: {v['compliant']}]")
            for field, text in v["copy"].items():
                limit = v["limits"].get(field, "-")
                chars = v["char_counts"].get(field, 0)
                print(f"    {field} ({chars}/{limit}): {text}")

if __name__ == "__main__":
    main()
