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

def process_with_digester(syl_data):
    """Explodes raw syllabus into granular 'Chyme' sub-topics."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'Digester', a specialized data structuring agent for the Gaandivam EdTech platform.
    Your job is to take the raw syllabus provided below and explode it into 'Chyme'—the absolute most granular level of detail possible.
    
    Follow this strict hierarchy:
    Subject -> Topic -> Sub-Topic -> Micro-Concept.
    For example: Technology -> Computer -> Software & Hardware -> Software -> Applications -> Coding.
    
    Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "chyme_granular_syllabus": {{
            "Subject Name": {{
                "Topic Name": {{
                    "Sub-Topic Name": ["Micro-concept 1", "Micro-concept 2", "Micro-concept 3"]
                }}
            }}
        }}
    }}
    
    RAW SYLLABUS DATA:
    {json.dumps(syl_data)[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1, # Low temperature to enforce strict, logical structure
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_digester():
    print("🧬 IGNITING AGENT: DIGESTER...")
    input_folder = "3_syllabi_processing"
    output_folder = "4_digester_chyme"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # We replace the 'SYL_' prefix with 'CHYME_'
        out_filename = filename.replace("SYL_", "CHYME_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Digesting syllabus into Chyme: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            syl_data = json.load(f)
            
        chyme_data, status = process_with_digester(syl_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if chyme_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(chyme_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Granular Chyme saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_digester()