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

def process_with_burper(enz_data):
    """Drafts WhatsApp and Telegram posts based on Enzymer data."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'BURPER', the Chief Social Media Broadcaster for Gaandivam, a premier EdTech platform.
    Take this logistical exam data and write TWO highly engaging, urgent alert posts.
    
    RULES:
    1. WhatsApp Post: Short, highly scannable, bullet points, heavy use of emojis (🚨, 📅, 🎓, 🔗).
    2. Telegram Post: Slightly more detailed, structured, professional but exciting.
    3. Both must end with a call-to-action to check the Gaandivam app/website and include hashtags like #Gaandivam #GovtJobs.
    4. Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "whatsapp_post": "string (formatted with newlines and emojis)",
        "telegram_post": "string (formatted with newlines and emojis)"
    }}
    
    ENZYMER DATA:
    {json.dumps(enz_data)[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.3, # Slight creativity for marketing copy
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_burper():
    print("📣 IGNITING AGENT: BURPER...")
    input_folder = "2_enzymer_processing"
    output_folder = "5_burper_social_out"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # We replace the 'ENZ_' prefix with 'SOCIAL_'
        out_filename = filename.replace("ENZ_", "SOCIAL_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Drafting broadcasts for: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            enz_data = json.load(f)
            
        social_data, status = process_with_burper(enz_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if social_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(social_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Broadcasts saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_burper()