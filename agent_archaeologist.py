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

def process_with_archaeologist(raw_text):
    """Structures messy OCR text from old exam papers into clean JSON."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'The Archaeologist', a data structuring agent for Gaandivam.
    Your task is to take messy, OCR-scanned text from Previous Year Question (PYQ) papers and convert it into a perfectly standardized JSON format.
    
    CRITICAL INSTRUCTIONS:
    - Standardize all options to exactly "A", "B", "C", and "D".
    - Standardize the correct answer to match the A, B, C, D format.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name_and_year": "string",
        "test_type": "Previous Year Paper",
        "questions": [
            {{
                "question_text": "string",
                "options": {{
                    "A": "string",
                    "B": "string",
                    "C": "string",
                    "D": "string"
                }},
                "correct_answer": "A, B, C, or D"
            }}
        ]
    }}
    
    RAW OCR TEXT:
    {raw_text[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0, # 0 temperature because we want strict formatting, no hallucination
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_archaeologist():
    print("🏺 IGNITING AGENT: THE ARCHAEOLOGIST...")
    vault_folder = "7_archaeologist_vault"
    
    for filename in os.listdir(vault_folder):
        if not filename.endswith(".txt") or not filename.startswith("RAW_"): continue
        
        out_filename = filename.replace("RAW_", "CLEAN_").replace(".txt", ".json")
        if os.path.exists(os.path.join(vault_folder, out_filename)): continue
            
        print(f"   ⚙️ Excavating and structuring: {filename}")
        with open(os.path.join(vault_folder, filename), 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        pyq_data, status = process_with_archaeologist(raw_text)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if pyq_data:
            with open(os.path.join(vault_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(pyq_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Clean PYQ JSON saved to {vault_folder}/{out_filename}")

if __name__ == "__main__":
    run_archaeologist()