import streamlit as st
from streamlit_stl import stl_from_file
import os
from openai import OpenAI
from stl import mesh
import numpy as np

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AM Decision Tool")

# -------------------------
# PART SELECTION
# -------------------------
parts = [
    "Collar", "T-Coupling", "Fitting Ring", "Cover", "Closure / Lid",
    "Door Handle", "Connector", "Radiator Cap", "Pipe Assembly",
    "Vacuum Valve", "Ventilator", "Brake Drum", "Transmission Component"
]

part = st.selectbox("Select Part", parts)

# -------------------------
# WEATHER INPUT
# -------------------------
weather = st.selectbox(
    "Environmental Condition",
    ["Normal", "Humid / Wet", "Cold", "Hot"]
)

# -------------------------
# PART DATABASE
# -------------------------
part_data = {
    "Collar": {"load": "Low", "temperature": 120, "chemical": "Fuel", "pressure": "Low", "tolerance": "High (>0.3mm)", "economic": "Neutral", "urgency": "Medium"},
    "T-Coupling": {"load": "Low", "temperature": 120, "chemical": "Oil", "pressure": "Medium", "tolerance": "Medium (0.1-0.3mm)", "economic": "Favorable (AM advantage)", "urgency": "High"},
    "Fitting Ring": {"load": "Low", "temperature": 150, "chemical": "Fuel", "pressure": "Medium", "tolerance": "High (>0.3mm)", "economic": "Neutral", "urgency": "Low"},
    "Cover": {"load": "Low", "temperature": 80, "chemical": "None", "pressure": "Low", "tolerance": "High (>0.3mm)", "economic": "Favorable (AM advantage)", "urgency": "Low"},
    "Closure / Lid": {"load": "Medium", "temperature": 80, "chemical": "None", "pressure": "Low", "tolerance": "Medium (0.1-0.3mm)", "economic": "Favorable (AM advantage)", "urgency": "Medium"},
    "Door Handle": {"load": "High", "temperature": 80, "chemical": "None", "pressure": "Low", "tolerance": "Medium (0.1-0.3mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "Low"},
    "Connector": {"load": "Medium", "temperature": 120, "chemical": "Oil", "pressure": "Medium", "tolerance": "Medium (0.1-0.3mm)", "economic": "Favorable (AM advantage)", "urgency": "High"},
    "Radiator Cap": {"load": "Medium", "temperature": 120, "chemical": "Fuel", "pressure": "High", "tolerance": "Low (<0.1mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "Medium"},
    "Pipe Assembly": {"load": "Medium", "temperature": 120, "chemical": "Fuel", "pressure": "High", "tolerance": "Medium (0.1-0.3mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "High"},
    "Vacuum Valve": {"load": "Medium", "temperature": 120, "chemical": "None", "pressure": "High", "tolerance": "Low (<0.1mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "High"},
    "Ventilator": {"load": "High", "temperature": 100, "chemical": "None", "pressure": "Low", "tolerance": "Low (<0.1mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "High"},
    "Brake Drum": {"load": "High", "temperature": 500, "chemical": "None", "pressure": "High", "tolerance": "Low (<0.1mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "High"},
    "Transmission Component": {"load": "High", "temperature": 150, "chemical": "Oil", "pressure": "High", "tolerance": "Low (<0.1mm)", "economic": "Unfavorable (Traditional cheaper)", "urgency": "High"}
}

data = part_data[part]

load = data["load"]
temperature = data["temperature"]
chemical = data["chemical"]
pressure = data["pressure"]
tolerance = data["tolerance"]
economic = data["economic"]
urgency = data["urgency"]

# -------------------------
# DISPLAY SPECIFICATIONS
# -------------------------
st.markdown("## Part Specifications")
st.write(f"Mechanical Load: {load}")
st.write(f"Temperature: {temperature} °C")
st.write(f"Chemical Exposure: {chemical}")
st.write(f"Pressure: {pressure}")
st.write(f"Tolerance: {tolerance}")

st.markdown("## Operational Context")
st.write(f"Economic Feasibility: {economic}")
st.write(f"Operational Urgency: {urgency}")

# -------------------------
# CAD PATH
# -------------------------
BASE_DIR = r"C:\Users\Utilizador\Salvador\intership\am_tool"

cad_models = {
    "Collar": os.path.join(BASE_DIR, "cad_models", "collar.stl")
}

# -------------------------
# FUNCTIONS
# -------------------------
def get_stl_dimensions(file_path):
    try:
        your_mesh = mesh.Mesh.from_file(file_path)
        points = your_mesh.vectors.reshape(-1, 3)

        min_vals = np.min(points, axis=0)
        max_vals = np.max(points, axis=0)
        dimensions = max_vals - min_vals

        length, width, height = dimensions
        max_dim = max(length, width, height)

        return round(length,2), round(width,2), round(height,2), round(max_dim,2)
    except:
        return None, None, None, None


def evaluate_geometry(max_dim):
    if max_dim is None:
        return "⚠️ Unknown", ["Could not extract geometry"]

    if max_dim > 256:
        return "🔴 Not Printable", ["Exceeds build volume (256mm)"]
    elif max_dim > 200:
        return "🟠 Printable with constraints", ["Close to build volume limit"]
    else:
        return "🟢 Printable", ["Fits within build volume"]


def classify_criticality(part):
    if part in ["Brake Drum", "Vacuum Valve", "Transmission Component"]:
        return "🔴 Safety Critical"
    elif part in ["Pipe Assembly", "T-Coupling", "Connector", "Radiator Cap", "Ventilator", "Door Handle"]:
        return "🟠 APK Critical"
    else:
        return "🟢 Non-Critical"


def evaluate_part(load, temperature, pressure, tolerance, criticality, economic):
    fail = False
    reasons = []

    if load == "High":
        fail = True
        reasons.append("High load not suitable")

    if temperature > 120:
        fail = True
        reasons.append("Temperature too high")

    if pressure == "High":
        fail = True
        reasons.append("High pressure not suitable")

    if tolerance == "Low (<0.1mm)":
        fail = True
        reasons.append("Tolerance too tight")

    if "Safety" in criticality:
        fail = True
        reasons.append("Safety-critical part")

    if economic == "Unfavorable (Traditional cheaper)":
        reasons.append("Not economically viable")

    if fail:
        return "❌ Not Suitable", reasons
    elif reasons:
        return "⚠️ Conditional", reasons
    else:
        return "✅ Suitable", reasons


def recommend_material(temperature, load, weather):
    material = "PETG"
    reason = []

    if temperature > 100 or weather == "Hot":
        material = "Nylon (PA)"
        reason.append("High temperature resistance")

    if load == "High":
        material = "Nylon (PA)"
        reason.append("High strength required")

    return material, reason

def get_mounting_instructions(part):

    instructions = {
        "Collar": [
            "Ensure shaft surface is clean before installation",
            "Apply uniform tightening torque",
            "Verify concentric alignment"
        ],

        "T-Coupling": [
            "Check sealing surfaces before mounting",
            "Use compatible clamps or threaded fittings",
            "Pressure test after installation"
        ],

        "Fitting Ring": [
            "Inspect groove dimensions before assembly",
            "Avoid excessive compression during mounting",
            "Lubricate sealing surface if required"
        ],

        "Cover": [
            "Align mounting holes correctly",
            "Use even fastening sequence",
            "Check for vibration clearance"
        ],

        "Closure / Lid": [
            "Ensure proper sealing before closing",
            "Do not overtighten fasteners",
            "Inspect for thermal deformation"
        ],

        "Door Handle": [
            "Verify mounting bracket alignment",
            "Check fastening rigidity",
            "Perform repeated load test after installation"
        ],

        "Connector": [
            "Verify dimensional compatibility",
            "Ensure proper insertion depth",
            "Inspect sealing interfaces"
        ],

        "Radiator Cap": [
            "Install only on cooled systems",
            "Check gasket seating",
            "Verify pressure locking mechanism"
        ],

        "Pipe Assembly": [
            "Ensure correct orientation during installation",
            "Avoid bending stress",
            "Perform leak inspection"
        ],

        "Vacuum Valve": [
            "Check flow direction before mounting",
            "Inspect sealing surfaces",
            "Verify vacuum integrity after installation"
        ],

        "Ventilator": [
            "Ensure balanced mounting",
            "Check rotational clearance",
            "Inspect airflow direction"
        ],

        "Brake Drum": [
            "Inspect thermal damage before installation",
            "Torque bolts to manufacturer specification",
            "Perform brake balance verification"
        ],

        "Transmission Component": [
            "Verify lubrication before installation",
            "Inspect mating surfaces",
            "Perform alignment verification"
        ]
    }

    return instructions.get(part, ["No instructions available"])


def get_ai_recommendation(part, load, temperature, chemical, pressure, weather, result):
    prompt = f"""
Analyze this part for additive manufacturing improvements:

Part: {part}
Load: {load}
Temperature: {temperature}
Chemical: {chemical}
Pressure: {pressure}
Weather: {weather}
Decision: {result}

Give short engineering recommendations.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------------------------
# BUTTON
# -------------------------
if st.button("Evaluate Part"):

    criticality = classify_criticality(part)
    result, reasons = evaluate_part(load, temperature, pressure, tolerance, criticality, economic)
    material, material_reason = recommend_material(temperature, load, weather)

    # -------------------------
    # STL Geometry Extraction
    # -------------------------
    stl_file = cad_models.get(part)

    if stl_file and os.path.exists(stl_file):
        length, width, height, max_dim = get_stl_dimensions(stl_file)
        geo_result, geo_reasons = evaluate_geometry(max_dim)
    else:
        length = width = height = None
        geo_result, geo_reasons = "⚠️ No STL", ["Geometry unavailable"]

    # -------------------------
    # RESULTS
    # -------------------------
    st.markdown("# Results")

    st.markdown("## Final Decision")
    if "✅" in result:
        st.success(result)
    elif "⚠️" in result:
        st.warning(result)
    else:
        st.error(result)


    st.markdown("## Material Recommendation")
    st.write(material)

    for r in material_reason:
        st.write("-", r)

    st.markdown("## Geometric Printability")

    if "🟢" in geo_result:
        st.success(geo_result)
    elif "🟠" in geo_result:
        st.warning(geo_result)
    else:
        st.error(geo_result)

    if length:
       length, width, height, max_dim = get_stl_dimensions(stl_file)

    st.markdown("## Explanation")

    all_reasons = reasons + geo_reasons
    if all_reasons:
        for r in all_reasons:
            st.write("-", r)
    else:
        st.write("No critical constraints detected.")

 
    st.markdown("## Mounting Instructions")

    mounting_steps = get_mounting_instructions(part)

    for step in mounting_steps:
        st.write("-", step)

    # CAD Viewer
    st.markdown("## 3D Model")
    if stl_file and os.path.exists(stl_file):
        stl_from_file(file_path=stl_file, height=500)
    else:
        st.warning("⚠️ 3D model not available")

    # AI
    st.markdown("## 🤖 AI Recommendations")
    try:
        ai_output = get_ai_recommendation(
            part, load, temperature, chemical, pressure, weather, result
        )
        st.write(ai_output)
    except:
        st.warning("⚠️ AI unavailable")