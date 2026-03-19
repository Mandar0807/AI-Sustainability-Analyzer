import sys
sys.path.append('.')

from services.metrics_service import (
    calculate_all_metrics,
    calculate_savings
)

print("Testing metrics service...\n")

models = ["groq", "cohere", "mistral", "openrouter", "huggingface"]

for model in models:
    print(f"Testing {model}...")
    try:
        # Simulate original prompt metrics
        original = calculate_all_metrics(
            prompt_tokens=50,
            response_tokens=100,
            model_key=model
        )

        # Simulate optimized prompt metrics
        optimized = calculate_all_metrics(
            prompt_tokens=20,
            response_tokens=60,
            model_key=model
        )

        savings = calculate_savings(original, optimized)

        print(f"✅ {model}")
        print(f"   Original  - Tokens: {original['total_tokens']}, FLOPs: {original['flops']:.2e}, Energy: {original['energy_kwh']:.6f} kWh, CO2: {original['co2_grams']:.6f}g")
        print(f"   Optimized - Tokens: {optimized['total_tokens']}, FLOPs: {optimized['flops']:.2e}, Energy: {optimized['energy_kwh']:.6f} kWh, CO2: {optimized['co2_grams']:.6f}g")
        print(f"   Savings   - Tokens: {savings['token_reduction_pct']}%, Energy: {savings['energy_reduction_pct']}%, CO2: {savings['co2_reduction_pct']}%")
    except Exception as e:
        print(f"❌ {model} failed: {e}")
    print()