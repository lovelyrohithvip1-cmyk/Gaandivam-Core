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

def process_with_gamer(textbook_data):
    """Transforms textbook concepts into interactive UI puzzles."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'The Gamer', the Chief Educational Game Designer for the Gaandivam EdTech platform.
    Take the provided Textbook Content and generate interactive puzzles to keep students addicted to learning.
    
    CRITICAL INSTRUCTIONS:
    - Generate 3 True/False rapid-fire statements based on core facts.
    - Generate 1 Match-the-Following puzzle with 4 pairs (e.g., Concept -> Definition, or Event -> Year).
    - Ensure the facts are strictly based on the text provided.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "module_name": "string",
        "true_false_rapid_fire": [
            {{
                "statement": "string",
                "is_true": true/false,
                "explanation": "string"
            }}
        ],
        "match_the_following": {{
            "left_column": ["Item A", "Item B", "Item C", "Item D"],
            "right_column_shuffled": ["Match C", "Match A", "Match D", "Match B"],
            "correct_mapping": {{
                "Item A": "Match A",
                "Item B": "Match B",
                "Item C": "Match C",
                "Item D": "Match D"
            }}
        }}
    }}
    
    TEXTBOOK DATA:
    {json.dumps(textbook_data)[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3, # Low-mid for creativity in phrasing but strict factuality
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_gamer():
    print("🎮 IGNITING AGENT: THE GAMER...")
    input_folder = "6_tony_stark_textbooks"
    output_folder = "9_gamer_arcade"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # Replace the 'TEXTBOOK_' prefix with 'PUZZLE_'
        out_filename = filename.replace("TEXTBOOK_", "PUZZLE_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Designing Arcade Puzzles for: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            textbook_data = json.load(f)
            
        game_data, status = process_with_gamer(textbook_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if game_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Puzzles saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_gamer()