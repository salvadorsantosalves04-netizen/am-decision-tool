import streamlit as st
from streamlit_stl import stl_from_file
import os
from openai import OpenAI
from stl import mesh
import numpy as np

# -------------------------
# OPENAI CLIENT
# -------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AM Decision Tool", layout="wide")

st.title("AM Decision Tool - Mercedes Benz 290GD")

# =========================================================
# MB290GD PART DATABASE
# =========================================================

part_categories = {

    "Engine System": {

        "Oil Filter Cap": {
            "serial": "ENG-001",
            "load": "Low",
            "temperature": 120,
            "chemical": "Oil",
            "pressure": "Medium",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "High",
            "criticality": "APK Critical",
            "estimated_size": 80
        },

        "Air Intake Cover": {
            "serial": "ENG-002",
            "load": "Low",
            "temperature": 80,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "High (>0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Medium",
            "criticality": "Non-Critical",
            "estimated_size": 120
        },

        "Radiator Cap": {
            "serial": "ENG-003",
            "load": "Medium",
            "temperature": 120,
            "chemical": "Coolant",
            "pressure": "High",
            "tolerance": "Low (<0.1mm)",
            "economic": "Unfavorable (Traditional cheaper)",
            "urgency": "Medium",
            "criticality": "APK Critical",
            "estimated_size": 70
        },

        "Cooling Fan Shroud": {
            "serial": "ENG-004",
            "load": "Low",
            "temperature": 100,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "High (>0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Low",
            "criticality": "Non-Critical",
            "estimated_size": 250
        },

        "Hose Connector": {
            "serial": "ENG-005",
            "load": "Medium",
            "temperature": 110,
            "chemical": "Coolant",
            "pressure": "Medium",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "High",
            "criticality": "APK Critical",
            "estimated_size": 60
        }
    },

    "Transmission System": {

        "Gearbox Cover": {
            "serial": "TRN-001",
            "load": "Medium",
            "temperature": 100,
            "chemical": "Oil",
            "pressure": "Low",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Neutral",
            "urgency": "Medium",
            "criticality": "APK Critical",
            "estimated_size": 180
        },

        "Shift Knob": {
            "serial": "TRN-002",
            "load": "Low",
            "temperature": 60,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "High (>0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Low",
            "criticality": "Non-Critical",
            "estimated_size": 55
        },

        "Transmission Bracket": {
            "serial": "TRN-003",
            "load": "High",
            "temperature": 120,
            "chemical": "Oil",
            "pressure": "Low",
            "tolerance": "Low (<0.1mm)",
            "economic": "Unfavorable (Traditional cheaper)",
            "urgency": "High",
            "criticality": "Safety Critical",
            "estimated_size": 150
        }
    },

    "Brake System": {

        "Brake Drum": {
            "serial": "BRK-001",
            "load": "High",
            "temperature": 500,
            "chemical": "None",
            "pressure": "High",
            "tolerance": "Low (<0.1mm)",
            "economic": "Unfavorable (Traditional cheaper)",
            "urgency": "High",
            "criticality": "Safety Critical",
            "estimated_size": 280
        },

        "Brake Fluid Reservoir Cap": {
            "serial": "BRK-002",
            "load": "Low",
            "temperature": 90,
            "chemical": "Brake Fluid",
            "pressure": "Low",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Medium",
            "criticality": "APK Critical",
            "estimated_size": 50
        }
    },

    "Interior Components": {

        "Door Handle": {
            "serial": "INT-001",
            "load": "Medium",
            "temperature": 70,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Low",
            "criticality": "Non-Critical",
            "estimated_size": 180
        },

        "Dashboard Clip": {
            "serial": "INT-002",
            "load": "Low",
            "temperature": 60,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "High (>0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Medium",
            "criticality": "Non-Critical",
            "estimated_size": 40
        },

        "Seat Adjustment Knob": {
            "serial": "INT-003",
            "load": "Low",
            "temperature": 50,
            "chemical": "None",
            "pressure": "Low",
            "tolerance": "High (>0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Low",
            "criticality": "Non-Critical",
            "estimated_size": 45
        }
    },

    "Exterior Components": {

        "Mirror Housing": {
            "serial": "EXT-001",
            "load": "Low",
            "temperature": 80,
            "chemical": "Rain / Dust",
            "pressure": "Low",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Favorable (AM advantage)",
            "urgency": "Medium",
            "criticality": "Non-Critical",
            "estimated_size": 200
        },

        "Headlight Bracket": {
            "serial": "EXT-002",
            "load": "Medium",
            "temperature": 90,
            "chemical": "Rain / Dust",
            "pressure": "Low",
            "tolerance": "Medium (0.1-0.3mm)",
            "economic": "Neutral",
            "urgency": "High",
            "criticality": "APK Critical",
            "estimated_size": 130
        }
    }
}

# =========================================================
# CATEGORY + PART SELECTION
# =========================================================

category = st.selectbox(
    "Select Part Category",
    list(part_categories.keys())
)

parts = list(part_categories[category].keys())
part  = st.selectbox("Select Part", parts)

# =========================================================
# SERIAL NUMBER SEARCH
# =========================================================

serial_input = st.text_input(
    "Or Enter Serial Number",
    placeholder="Example: ENG-001"
)

# =========================================================
# PART IDENTIFICATION
# =========================================================

selected_part = None
selected_data = None

if serial_input:
    for cat, parts_dict in part_categories.items():
        for p_name, p_data in parts_dict.items():
            if p_data["serial"].lower() == serial_input.strip().lower():
                selected_part = p_name
                selected_data = p_data

if selected_part is None:
    selected_part = part
    selected_data = part_categories[category][part]

# =========================================================
# ENVIRONMENT INPUT
# =========================================================

st.markdown("## Environmental Conditions")

use_custom_weather = st.checkbox("Use Real Environmental Data")

if use_custom_weather:
    ambient_temperature = st.slider("Ambient Temperature (°C)", -30, 60, 25)
    humidity = st.slider("Humidity (%)", 0, 100, 50)

    if ambient_temperature > 40:
        weather = "Hot"
    elif ambient_temperature < 0:
        weather = "Cold"
    elif humidity > 80:
        weather = "Humid / Wet"
    else:
        weather = "Normal"

    st.info(f"Detected Environment: **{weather}**")

else:
    weather = st.selectbox(
        "Environmental Condition",
        ["Normal", "Humid / Wet", "Cold", "Hot"]
    )

# =========================================================
# EXTRACT PART DATA
# =========================================================

load           = selected_data["load"]
temperature    = selected_data["temperature"]
chemical       = selected_data["chemical"]
pressure       = selected_data["pressure"]
tolerance      = selected_data["tolerance"]
economic       = selected_data["economic"]
urgency        = selected_data["urgency"]
criticality    = selected_data["criticality"]
estimated_size = selected_data.get("estimated_size", 100)

# =========================================================
# DISPLAY PART SPECIFICATIONS
# =========================================================

st.markdown("## Part Specifications")
st.write(f"**Selected Part:** {selected_part}")
st.write(f"**Serial Number:** {selected_data['serial']}")
st.write(f"**Mechanical Load:** {load}")
st.write(f"**Temperature Resistance:** {temperature} °C")
st.write(f"**Chemical Exposure:** {chemical}")
st.write(f"**Pressure Resistance:** {pressure}")
st.write(f"**Tolerance:** {tolerance}")
st.write(f"**Estimated Size:** {estimated_size} mm")

st.markdown("## Operational Context")
st.write(f"**Economic Feasibility:** {economic}")
st.write(f"**Operational Urgency:** {urgency}")
st.write(f"**Criticality:** {criticality}")

# =========================================================
# CAD MODELS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

cad_models = {
    "Oil Filter Cap": os.path.join(BASE_DIR, "cad_models", "oil_filter_cap.stl"),
    "Door Handle":    os.path.join(BASE_DIR, "cad_models", "door_handle.stl"),
    "Radiator Cap":   os.path.join(BASE_DIR, "cad_models", "radiator_cap.stl"),
}

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_stl_dimensions(file_path):
    try:
        your_mesh = mesh.Mesh.from_file(file_path)
        points    = your_mesh.vectors.reshape(-1, 3)
        min_vals  = np.min(points, axis=0)
        max_vals  = np.max(points, axis=0)
        dimensions = max_vals - min_vals
        length, width, height = dimensions
        max_dim = max(length, width, height)
        return round(max_dim, 2)
    except:
        return None


def evaluate_geometry(size):
    if size is None:
        return "⚠️ Unknown", ["Could not evaluate geometry"]
    if size > 256:
        return "🔴 Not Printable", [f"Size ({size} mm) exceeds printer build volume (256 mm)"]
    elif size > 200:
        return "🟠 Printable with constraints", [
            f"Size ({size} mm) is close to the build volume limit — consider splitting the part or reorienting the print"
        ]
    else:
        return "🟢 Printable", [f"Size ({size} mm) fits within printer build volume"]


def evaluate_part(load, temperature, pressure, tolerance, criticality, economic):
    fail    = False
    reasons = []

    # Hard override conditions — any single one forces ❌
    if load == "High":
        fail = True
        reasons.append("High mechanical load — FDM polymers cannot reliably carry structural drivetrain or brake loads")

    if temperature > 120:
        fail = True
        reasons.append(f"Operating temperature ({temperature}°C) exceeds FDM polymer limit (~120°C)")

    if pressure == "High":
        fail = True
        reasons.append("High pressure requirement — FDM layer bonding cannot guarantee sealing integrity under high pressure")

    if tolerance == "Low (<0.1mm)":
        fail = True
        reasons.append("Required tolerance (<0.1 mm) is below FDM printer capability (±0.1–0.3 mm)")

    if "Safety" in criticality:
        fail = True
        reasons.append("Safety-critical component — FDM substitution is not permitted under Dutch APK regulations")

    # Conditional flags — downgrade to ⚠️ but do not hard-fail
    if "APK Critical" in criticality:
        reasons.append("APK-critical component — conditional use only; must pass inspection compliance check")

    if "Unfavorable" in economic:
        reasons.append("Traditional manufacturing is more economically viable for this part in standard supply conditions")

    if fail:
        return "❌ Not Suitable", reasons
    elif reasons:
        return "⚠️ Conditional", reasons
    else:
        return "✅ Suitable", reasons


def get_mounting_instructions(part):
    """
    Step-by-step assembly and mounting instructions for each MB290GD part.
    Safety-critical parts include a prominent warning against FDM installation.
    """
    instructions = {

        # ── ENGINE SYSTEM ─────────────────────────────────────────────
        "Oil Filter Cap": [
            "Clean oil filter sealing surface and threads thoroughly before installation",
            "Apply a thin film of clean engine oil to the rubber gasket",
            "Tighten by hand first, then apply a firm 3/4 turn — do not use a wrench to overtighten",
            "Start engine and inspect around the cap for oil seepage; retighten only if leaking"
        ],
        "Air Intake Cover": [
            "Inspect air intake aperture and remove any debris before fitting",
            "Align cover tabs with intake housing slots",
            "Press evenly around the perimeter until all retention clips engage audibly",
            "Check entire perimeter for gaps — any unsealed air path bypasses the air filter"
        ],
        "Radiator Cap": [
            "⚠️ Only install on a fully cooled engine — pressurised hot coolant causes severe burns",
            "Inspect the rubber gasket and pressure valve seal for cracks or deformation; replace if worn",
            "Align the cap arrows, press down and rotate clockwise to the first detent, then continue to the locked position",
            "Verify the pressure locking mechanism engages with an audible click",
            "Run engine to operating temperature and inspect cap seat for coolant seepage"
        ],
        "Cooling Fan Shroud": [
            "Confirm fan blades are stationary before handling the shroud",
            "Align shroud mounting tabs with radiator frame brackets on both sides simultaneously",
            "Maintain a minimum 10 mm clearance between the shroud inner wall and fan blade tips",
            "Secure with OEM fasteners and verify all clips are seated flush before starting the engine"
        ],
        "Hose Connector": [
            "Drain the cooling system before disconnecting the existing connector",
            "Verify the inner diameter of the connector matches the hose end bore",
            "Apply a small amount of coolant to the hose inner surface to ease fitting",
            "Push the hose fully onto the connector until it seats against the bead stop",
            "Position the hose clamp 5–10 mm from the hose end and tighten to 2–3 Nm — do not overtighten printed parts",
            "Refill and bleed the cooling system; run to temperature and inspect all joints for leaks"
        ],

        # ── TRANSMISSION SYSTEM ───────────────────────────────────────
        "Gearbox Cover": [
            "Drain gearbox oil into a suitable container before removing the existing cover",
            "Clean the mating flange completely — remove all traces of old sealant or gasket material",
            "Apply a continuous 3 mm bead of RTV sealant if no discrete gasket is used",
            "Insert all bolts finger-tight first, then torque in a cross pattern to manufacturer specification",
            "Refill with the correct grade gearbox oil and check the level after the first test drive"
        ],
        "Shift Knob": [
            "Note thread direction before removal — some MB models use left-hand thread",
            "Unscrew the existing knob and clean the shaft threads",
            "Thread the new knob by hand until it seats; verify neutral gear alignment",
            "Do not apply thread-locking compound — the knob must remain removable"
        ],
        "Transmission Bracket": [
            "⚠️ Safety-critical component — a 3D-printed version must not be installed under any circumstances",
            "Torque all mounting bolts to manufacturer specification using a calibrated torque wrench",
            "Inspect mating surfaces for wear, cracks, or deformation before installation",
            "Perform driveline alignment verification after installation"
        ],

        # ── BRAKE SYSTEM ──────────────────────────────────────────────
        "Brake Drum": [
            "⚠️ Safety-critical component — a 3D-printed version must never be installed on a vehicle",
            "Inspect the drum bore and friction surface for heat cracking, scoring, or out-of-round condition",
            "Clean hub mating face and remove corrosion before fitting",
            "Torque mounting bolts in a star pattern to manufacturer specification",
            "Bed in new brake shoes with 10–15 progressive stops from 50 km/h before full operational use",
            "Perform brake balance verification after installation"
        ],
        "Brake Fluid Reservoir Cap": [
            "Wipe the cap and surrounding reservoir area clean — brake fluid strips paint on contact",
            "Inspect the diaphragm seal inside the cap for cracks or deformation; replace if worn",
            "Verify brake fluid level is at MAX before fitting the cap",
            "Press the cap firmly until it clicks fully into place or torque threaded caps to hand-tight only",
            "Inspect for leaks after the first full brake application cycle"
        ],

        # ── INTERIOR COMPONENTS ───────────────────────────────────────
        "Door Handle": [
            "Remove the door trim panel to access handle mounting bolts from the interior side",
            "Disconnect the linkage rod clip before removing the existing handle",
            "Align the new handle with the door aperture and thread bolts finger-tight first",
            "Reconnect the linkage rod and verify full open and close travel before final torque",
            "Perform 10 full actuation cycles under load to confirm smooth operation"
        ],
        "Dashboard Clip": [
            "Align the clip post with the dashboard aperture hole",
            "Press firmly until the retention lug clicks audibly into the locked position",
            "Verify the trim panel sits flush — any proud edge indicates incomplete engagement",
            "Do not use adhesive; clips must remain removable for future panel access"
        ],
        "Seat Adjustment Knob": [
            "Align the knob spline or flat profile with the adjustment shaft",
            "Press onto the shaft until fully seated with no remaining axial play",
            "Test the full adjustment range (forward/back or height) to confirm free movement"
        ],

        # ── EXTERIOR COMPONENTS ───────────────────────────────────────
        "Mirror Housing": [
            "Disconnect the mirror heating wiring harness before removing the old housing (if equipped)",
            "Align housing locating pins with base plate holes before applying any pressure",
            "Thread all bolts finger-tight first; verify mirror articulation is unobstructed, then torque to specification",
            "Reconnect wiring harness and test heating function if applicable",
            "Confirm full adjustment range is unimpeded by housing edges"
        ],
        "Headlight Bracket": [
            "Disconnect the headlight wiring harness before removing the bracket",
            "Align all bracket mounting holes with body aperture simultaneously before inserting any bolt",
            "Insert all bolts finger-tight first to ensure the bracket seats flat, then torque to specification",
            "Reconnect wiring harness and test both dipped and full-beam operation",
            "Verify headlight aim with a beam alignment tool after installation"
        ]
    }

    return instructions.get(
        part,
        [
            "No specific instructions available for this part",
            "Follow general FDM component installation guidelines",
            "Verify dimensional fit against the mating surface before final installation",
            "Inspect printed part for layer delamination or surface defects before use"
        ]
    )


def build_weather_context(weather, result):
    """
    Generates a structured weather instruction block injected into the AI prompt.
    Only activates for Suitable and Conditional parts — Not Suitable parts
    already fail on engineering grounds and do not need weather adaptations.
    """
    if result == "❌ Not Suitable":
        return "WEATHER CONDITIONS: Part is Not Suitable on engineering grounds. Weather adaptations are not applicable."

    if weather == "Humid / Wet":
        return """
WEATHER FLAG — HUMID / WET CONDITIONS (ACTIVE):
This part is classified as printable but will operate in persistent humid or wet conditions (Dutch maritime climate).
You MUST specifically address all of the following:
- Is the recommended material hygroscopic? (Critical for Nylon/PA — moisture causes strength loss up to 25% and dimensional swelling)
- Should a surface sealant, moisture-barrier coating, or hydrophobic post-processing step be applied?
- Should PETG or ASA be selected over Nylon to avoid hygroscopic risk for this specific part?
- Is there a dimensional swelling risk that could push tolerance compliance outside ±0.1–0.3 mm?
- What print settings (wall count, layer height, infill density) best improve intrinsic moisture resistance?
"""

    elif weather == "Cold":
        return """
WEATHER FLAG — COLD CONDITIONS (ACTIVE):
This part is classified as printable but will operate in cold or freezing conditions (down to -27°C in Dutch operations).
You MUST specifically address all of the following:
- Does the recommended material remain impact-resistant below 0°C, or is embrittlement a risk?
- Should PLA or standard ABS be explicitly excluded, and what is the minimum acceptable material?
- Which infill geometry (gyroid, honeycomb, cubic) best maintains impact resistance at low temperatures?
- Is there a seal, snap-fit, or flexible interface on this part that could fail due to thermal contraction?
- Should TPU be considered for any sealing, damping, or flexible interface features?
"""

    elif weather == "Hot":
        return """
WEATHER FLAG — HOT CONDITIONS (ACTIVE):
This part is classified as printable but will operate in hot ambient conditions (up to 40°C+ ambient in summer operations).
You MUST specifically address all of the following:
- What is the Heat Deflection Temperature (HDT) of the recommended material, and what is the safety margin above combined ambient + operational temperature?
- Should PLA be explicitly ruled out? What is the minimum HDT material acceptable for this part?
- Would post-print annealing meaningfully improve thermal stability, and if so, what are the annealing parameters?
- Is there a risk of creep or permanent deformation under sustained load at elevated temperature?
- Which print orientation maximises thermal resistance along the primary load axis?
"""

    else:
        return """
WEATHER CONDITIONS: Normal — no adverse environmental modifiers active.
Briefly note that no weather-specific adaptations are required for this part,
but mention the baseline Dutch climate (year-round moderate humidity, temperatures -27°C to +40°C)
as a standard operational envelope to keep in mind for any outdoor-exposed features.
"""


def get_ai_recommendation(
    part, load, temperature, chemical,
    pressure, tolerance, economic, weather,
    criticality, result
):
    weather_context = build_weather_context(weather, result)

    prompt = f"""
You are an expert FDM additive manufacturing engineer specializing in military vehicle field maintenance for the Dutch Ministry of Defense.

Analyze the following Mercedes Benz 290GD spare part and provide specific, actionable engineering recommendations.

PART INFORMATION:
- Part Name: {part}
- Mechanical Load: {load}
- Operating Temperature Requirement: {temperature}°C
- Chemical Exposure: {chemical}
- Pressure Requirement: {pressure}
- Dimensional Tolerance: {tolerance}
- Economic Feasibility: {economic}
- APK / Safety Criticality: {criticality}
- AM Tool Decision: {result}

{weather_context}

YOUR TASKS — structure your answer using these exact headings:

**1. Material Recommendation**
Recommend the single best FDM material from: PLA, PETG, ABS, ASA, Nylon (PA), Carbon Fiber Nylon (PA-CF), TPU, Polycarbonate (PC).
Justify against the part's temperature, load, chemical, and pressure requirements.
Name one alternative material and when it would be preferred over the primary recommendation.

**2. Print Settings**
State: infill percentage and pattern, wall count, layer height, support requirements, and optimal print orientation.

**3. Post-Processing**
List any required steps: support removal, annealing temperature and duration, surface sealing, coating, or tolerance fitting.

**4. Risk Flags**
List the 2–3 most significant risks for this specific part and a mitigation action for each.

**5. Weather-Specific Adaptations**
Directly address the weather flag above. If Normal, keep this to two sentences.

**6. Field vs. Depot Assessment**
One sentence: is this part worth printing in a forward field context, or only in a depot with full equipment available?

Keep the full response under 380 words. Be precise and engineering-focused — avoid generic advice.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# =========================================================
# EVALUATE BUTTON
# =========================================================

if st.button("Evaluate Part"):

    # Step 1 — Suitability evaluation
    result, reasons = evaluate_part(
        load, temperature, pressure,
        tolerance, criticality, economic
    )

    # Step 2 — Geometry check (STL if available, else estimated_size)
    stl_file = cad_models.get(selected_part)

    if stl_file and os.path.exists(stl_file):
        max_dim = get_stl_dimensions(stl_file)
        geo_result, geo_reasons = evaluate_geometry(max_dim)
    else:
        geo_result, geo_reasons = evaluate_geometry(estimated_size)

    # =========================================================
    # RESULTS DISPLAY
    # =========================================================

    st.markdown("# Results")

    # ── WEATHER IMPACT ────────────────────────────────────────
    st.markdown("## Weather Impact")

    if weather == "Normal":
        st.info("Normal conditions — no adverse environmental modifiers applied.")
    elif weather == "Humid / Wet":
        st.warning("Humid / Wet — moisture degradation and dimensional swelling risk active. See AI recommendations for material and print adaptations.")
    elif weather == "Cold":
        st.warning("Cold — embrittlement risk down to -27°C active. See AI recommendations for material selection and design adaptations.")
    elif weather == "Hot":
        st.warning("Hot — thermal softening and creep risk active. See AI recommendations for HDT margin and annealing guidance.")

    # ── CRITICALITY ───────────────────────────────────────────
    st.markdown("## Criticality")

    if "Safety" in criticality:
        st.error(f"🔴 {criticality}")
    elif "APK" in criticality:
        st.warning(f"🟠 {criticality}")
    else:
        st.success(f"🟢 {criticality}")

    # ── FINAL DECISION ────────────────────────────────────────
    st.markdown("## Final Decision")

    if "✅" in result:
        st.success(result)
    elif "⚠️" in result:
        st.warning(result)
    else:
        st.error(result)

    # ── GEOMETRIC PRINTABILITY ────────────────────────────────
    st.markdown("## Geometric Printability")

    if "🟢" in geo_result:
        st.success(geo_result)
    elif "🟠" in geo_result:
        st.warning(geo_result)
    else:
        st.error(geo_result)

    # ── EXPLANATION ───────────────────────────────────────────
    st.markdown("## Explanation")

    all_reasons = reasons + geo_reasons

    if all_reasons:
        for r in all_reasons:
            st.write("-", r)
    else:
        st.write("No critical constraints detected.")

    # ── ASSEMBLY & MOUNTING INSTRUCTIONS ─────────────────────
    st.markdown("## Assembly & Mounting Instructions")

    mounting_steps = get_mounting_instructions(selected_part)

    for step in mounting_steps:
        st.write("-", step)

    # ── 3D MODEL / SCAN GUIDANCE ─────────────────────────────
    st.markdown("## 3D Model")

    if stl_file and os.path.exists(stl_file):
        stl_from_file(
            file_path=stl_file,
            material="material",
            auto_rotate=True,
            height=500,
            shininess=100,
            cam_v_angle=60,
            cam_h_angle=90,
            cam_distance=0
        )
    else:
        st.info(
            " **No CAD model loaded for this part.** \n\n"
            "If you have access to the physical MB290GD component, the recommended workflow is: \n"
            "1. Disassemble the part from the vehicle \n"
            "2. Scan it using a structured-light or photogrammetry 3D scanner \n"
            "3. Export the scan as an STL file \n"
            "4. Place the STL in the `cad_models/` folder \n"
            "5. Register it in the `cad_models` dictionary in this app \n\n"
            "This allows the tool to display the 3D model and perform geometry-based printability checks from actual part dimensions."
        )

    # ── AI RECOMMENDATIONS ────────────────────────────────────
    st.markdown("## AI Recommendations")

    try:
        ai_output = get_ai_recommendation(
            selected_part, load, temperature, chemical,
            pressure, tolerance, economic, weather,
            criticality, result
        )
        st.write(ai_output)

    except Exception as e:
        st.warning(f"AI unavailable: {e}")