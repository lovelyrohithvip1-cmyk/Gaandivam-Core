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

def process_with_tony_stark(chyme_data):
    """Transforms granular Chyme into visionary textbook material."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    # We extract just a portion of the Chyme for the prompt to avoid token overflow, 
    # but in a scaled version, this would loop topic by topic.
    prompt = f"""
    You are 'Tony Stark', the ultimate subject-matter expert and visionary author for the Gaandivam EdTech platform.
    Your task is to take the provided 'Chyme' (granular syllabus data) and generate a master Study Guide / Textbook Chapter.
    
    CRITICAL INSTRUCTIONS:
    - Write as if you are a brilliant visionary sent by the divine, revolutionizing the field.
    - Present the subject using innovative methods, clear formulas, and historical context (tracing its origins to the present).
    - Organize clearly by Subject -> Chapter -> Topic.
    - Do not just list topics; provide actual, deep educational content for the core concepts mentioned in the Chyme.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "textbook_content": [
            {{
                "subject": "string",
                "chapter_title": "string",
                "visionary_introduction": "string (tracing origins and importance)",
                "core_concepts": [
                    {{
                        "concept_name": "string",
                        "innovative_explanation": "string (detailed, engaging textbook content)",
                        "formulas_or_key_facts": "string"
                    }}
                ]
            }}
        ]
    }}
    
    CHYME DATA:
    {json.dumps(chyme_data)[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.4, # Slightly higher for creative, visionary writing
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_tony_stark():
    print("🦸‍♂️ IGNITING AGENT: TONY STARK...")
    input_folder = "4_digester_chyme"
    output_folder = "6_tony_stark_textbooks"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # We replace the 'CHYME_' prefix with 'TEXTBOOK_'
        out_filename = filename.replace("CHYME_", "TEXTBOOK_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Authoring visionary textbook for: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            chyme_data = json.load(f)
            
        textbook_data, status = process_with_tony_stark(chyme_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if textbook_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(textbook_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Textbook saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_tony_stark()