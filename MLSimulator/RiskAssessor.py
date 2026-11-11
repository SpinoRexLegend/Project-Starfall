import json
import math
import os
import random
from datetime import datetime


METERS_PER_KILOMETER = 1_000.0
JOULES_PER_MEGATON_TNT = 4.184e15


def perform_assessment(asteroid_id, diameter, velocity, material, best_fuel, best_distance):
    # Assessment ID (integer representation)
    ass_id = random.randint(10000, 99999)
    
    # Inputs arrive in the units declared by the asteroid schema.
    dia_f = float(diameter)
    vel_f = float(velocity)
    dist_f = float(best_distance)
    
    # Impact Probability (heuristic based on distance and velocity)
    ip_base = 1.0 - (dist_f / 100000.0)
    if ip_base < 0:
        ip_base = 0.05
    ip = min(1.0, max(0.01, ip_base + (vel_f / 200.0)))
    
    # Treat the asteroid as a sphere, infer bulk density from composition, then
    # apply the classical kinetic-energy equation E = 1/2 mv^2 in SI units.
    density_kg_m3 = material_density_kg_m3(material)
    diameter_m = dia_f * METERS_PER_KILOMETER
    radius_m = diameter_m / 2.0
    volume_m3 = (4.0 / 3.0) * math.pi * (radius_m ** 3)
    estimated_mass_kg = density_kg_m3 * volume_m3
    velocity_mps = vel_f * METERS_PER_KILOMETER
    kinetic_energy_joules = 0.5 * estimated_mass_kg * (velocity_mps ** 2)
    kinetic_energy_mt = kinetic_energy_joules / JOULES_PER_MEGATON_TNT
    ke_mt = round(kinetic_energy_mt, 6)
    
    # Risk Score (0 to 100)
    risk_score = min(100.0, round(ip * 100.0 + (ke_mt / 100.0), 2))
    
    # Estimated Damage
    if risk_score > 80:
        damage = "Critical"
    elif risk_score > 50:
        damage = "High"
    elif risk_score > 20:
        damage = "Medium"
    else:
        damage = "Low"
        
    # Requires Deflection
    requires_deflection = True if risk_score > 40 else False
    
    raw_response_dict = {
        "calculated_ip": round(ip, 4),
        "calculated_ke": ke_mt,
        "kinetic_energy_joules": round(kinetic_energy_joules, 3),
        "estimated_mass_kg": round(estimated_mass_kg, 3),
        "material_density_kg_m3": density_kg_m3,
        "kinetic_energy_formula": "E = 0.5 * m * v^2",
        "input_distance": dist_f,
        "raw_score": risk_score
    }
    raw_response_str = json.dumps(raw_response_dict)
    
    # Date time
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "assessmentID": ass_id,
        "asteroidID": asteroid_id,
        "impactProbability": round(ip, 4),
        "kineticEnergyMT": ke_mt,
        "kineticEnergyJoules": round(kinetic_energy_joules, 3),
        "estimatedMassKg": round(estimated_mass_kg, 3),
        "materialDensityKgM3": density_kg_m3,
        "kineticEnergyFormula": "E = 0.5 * m * v^2",
        "estimatedDamage": damage,
        "riskScore": risk_score,
        "requiresDeflection": requires_deflection,
        "rawResponse": raw_response_str,
        "createdAt": created_at
    }


def material_density_kg_m3(material):
    composition = str(material or "").strip().casefold()
    density_profiles = (
        (("iron", "nickel", "metal", "m-type"), "ASTEROID_DENSITY_METALLIC_KG_M3", 7_800.0),
        (("carbon", "c-type"), "ASTEROID_DENSITY_CARBONACEOUS_KG_M3", 1_700.0),
        (("ice", "icy", "comet"), "ASTEROID_DENSITY_ICY_KG_M3", 1_000.0),
        (("rock", "stone", "stony", "silicate", "s-type"), "ASTEROID_DENSITY_STONY_KG_M3", 3_000.0)
    )
    for aliases, environment_name, default_density in density_profiles:
        if any(alias in composition for alias in aliases):
            return _positive_density(environment_name, default_density)
    return _positive_density("ASTEROID_DENSITY_DEFAULT_KG_M3", 3_000.0)


def _positive_density(environment_name, default_density):
    raw_value = os.getenv(environment_name, str(default_density))
    try:
        density = float(raw_value)
    except ValueError as exception:
        raise ValueError(f"{environment_name} must be a number") from exception
    if not math.isfinite(density) or density <= 0:
        raise ValueError(f"{environment_name} must be greater than zero")
    return density
