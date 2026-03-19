from config import MODELS, CARBON_INTENSITY, GPU_COMPUTE_RATE

def calculate_flops(model_params: float, total_tokens: int) -> float:
    """
    FLOPs = 6 x model_parameters x total_tokens
    This estimates the floating point operations needed for inference.
    """
    return 6 * model_params * total_tokens

def calculate_energy(flops: float) -> float:
    """
    Energy (kWh) = FLOPs / (GPU_COMPUTE_RATE x 3.6e6)
    GPU_COMPUTE_RATE = 312 TFLOPS (A100 GPU)
    3.6e6 converts joules to kWh
    """
    return flops / (GPU_COMPUTE_RATE * 3.6e6)

def calculate_co2(energy_kwh: float) -> float:
    """
    CO2 (grams) = Energy (kWh) x Carbon Intensity (gCO2/kWh)
    Carbon intensity = 475 gCO2/kWh (IEA global average)
    """
    return energy_kwh * CARBON_INTENSITY

def calculate_all_metrics(
    prompt_tokens: int,
    response_tokens: int,
    model_key: str
) -> dict:
    """
    Calculate all sustainability metrics for a given model and token counts.
    """
    total_tokens = prompt_tokens + response_tokens
    model_params = MODELS[model_key]["parameters"]

    flops = calculate_flops(model_params, total_tokens)
    energy_kwh = calculate_energy(flops)
    co2_grams = calculate_co2(energy_kwh)

    return {
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": total_tokens,
        "flops": flops,
        "energy_kwh": energy_kwh,
        "co2_grams": co2_grams
    }

def calculate_savings(original: dict, optimized: dict) -> dict:
    """
    Calculate percentage reduction between original and optimized metrics.
    """
    def safe_reduction(orig, opt):
        if orig == 0:
            return 0.0
        return round(((orig - opt) / orig) * 100, 2)

    return {
        "token_reduction_pct": safe_reduction(
            original["total_tokens"], optimized["total_tokens"]
        ),
        "energy_reduction_pct": safe_reduction(
            original["energy_kwh"], optimized["energy_kwh"]
        ),
        "co2_reduction_pct": safe_reduction(
            original["co2_grams"], optimized["co2_grams"]
        ),
        "tokens_saved": original["total_tokens"] - optimized["total_tokens"],
        "energy_saved_kwh": original["energy_kwh"] - optimized["energy_kwh"],
        "co2_saved_grams": original["co2_grams"] - optimized["co2_grams"]
    }