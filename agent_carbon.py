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

def process_with_carbon(textbook_data):
    """Transforms textbook content into a full 3D explainer video script."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'Carbon', the elite AI Film Director for Gaandivam Studios.
    Take the provided Textbook Content and write a highly engaging, cinematic video script for a 3D animated explainer video.
    
    CRITICAL INSTRUCTIONS:
    - Break the content down into a logical sequence of 'Scenes'.
    - For each scene, provide a 'Visual Prompt' describing exactly what the 3D animation should show (e.g., 'Camera pans over a glowing 3D map of the Mughal Empire').
    - Provide the exact 'Narration' text to be spoken by our AI voiceover.
    - Provide any 'On-Screen Text' (captions, formulas, or key bullet points) that should pop up.
    - Keep the pacing fast, energetic, and highly educational.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "video_title": "string",
        "target_duration_minutes": "string",
        "scenes": [
            {{
                "scene_number": integer,
                "visual_prompt_for_3D_engine": "string",
                "narration_script": "string",
                "on_screen_text": "string or null"
            }}
        ]
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
                temperature=0.5, # Medium-high temperature for cinematic creativity
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_carbon():
    print("🎬 IGNITING AGENT: CARBON (THE STUDIO DIRECTOR)...")
    input_folder = "6_tony_stark_textbooks"
    output_folder = "11_studio_carbon"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # Replace the 'TEXTBOOK_' prefix with 'SCRIPT_'
        out_filename = filename.replace("TEXTBOOK_", "SCRIPT_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Directing video script for: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            textbook_data = json.load(f)
            
        script_data, status = process_with_carbon(textbook_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if script_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(script_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Cinematic Script saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_carbon()