import os
import json
from groq import Groq

def load_api_keys():
    keys = []
    try:
        with open("keys_backup.txt", "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("gsk_"): keys.append(stripped)
    except: pass
    return keys

GROQ_API_KEYS = load_api_keys()
CURRENT_KEY_INDEX = 0

def process_with_syllabi(raw_data):
    """Extracts ONLY the syllabus data."""
    global CURRENT_KEY_INDEX
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'Syllabi', a specialized data extraction agent for Gaandivam.
    Analyze this raw exam data and extract ONLY the syllabus topics. 
    Ignore application dates, fees, and logistics. Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "raw_syllabus": {{
            "Subject Name": ["Topic 1", "Topic 2", "Topic 3"]
        }}
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
            if "429" in str(e) or "rate_limit" in str(e): CURRENT_KEY_INDEX += 1 
            else: return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_syllabi():
    print("📚 IGNITING AGENT: SYLLABI...")
    intake_folder = "1_big_mouth_intake"
    output_folder = "3_syllabi_processing"
    
    for filename in os.listdir(intake_folder):
        if not filename.endswith(".json"): continue
        
        out_filename = f"SYL_{filename}"
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Extracting curriculum from: {filename}")
        with open(os.path.join(intake_folder, filename), 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        syl_data, status = process_with_syllabi(raw_data)
        
        if status == "ALL_KEYS_DEAD": break
            
        if syl_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(syl_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Syllabus saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_syllabi()