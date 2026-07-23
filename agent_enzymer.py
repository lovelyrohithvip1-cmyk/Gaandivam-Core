import os
import json
from groq import Groq

# =====================================================================
# 🔑 DYNAMIC KEY LOADER 
# =====================================================================
def load_api_keys():
    keys = []
    try:
        with open("keys_backup.txt", "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("gsk_"):
                    keys.append(stripped)
    except:
        pass
    return keys

GROQ_API_KEYS = load_api_keys()
CURRENT_KEY_INDEX = 0

def process_with_enzymer(raw_data):
    """Extracts qualifications, logistics, and links."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'Enzymer', a specialized data extraction agent for Gaandivam.
    Analyze this raw exam data and extract ONLY the logistical and qualification details.
    Do NOT include the syllabus. Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "educational_qualifications": ["list of degrees/requirements"],
        "age_limits": "string",
        "salary_details": "string",
        "number_of_posts": "string",
        "medical_physical_fitness": "string",
        "quotas_and_gender_rules": "string",
        "application_fee": "string",
        "important_dates": {{"release": "string", "deadline": "string", "extensions": "string"}},
        "application_link": "string"
    }}
    
    RAW DATA:
    {json.dumps(raw_data)[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0,
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_enzymer():
    print("🧪 IGNITING AGENT: ENZYMER...")
    intake_folder = "1_big_mouth_intake"
    output_folder = "2_enzymer_processing"
    
    for filename in os.listdir(intake_folder):
        if not filename.endswith(".json"): continue
        
        # Skip if already processed
        out_filename = f"ENZ_{filename}"
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Analyzing logistics for: {filename}")
        with open(os.path.join(intake_folder, filename), 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        enz_data, status = process_with_enzymer(raw_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if enz_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(enz_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Logistics saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_enzymer()