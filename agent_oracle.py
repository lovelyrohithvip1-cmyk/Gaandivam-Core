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

def process_with_oracle(raw_news):
    """Structures daily news and links it to historical context."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'The Oracle', the Chief Current Affairs and GK Instructor for the Gaandivam EdTech platform.
    Your task is to take this raw daily news feed and structure it into a highly educational Current Affairs module.
    
    CRITICAL INSTRUCTIONS:
    - Categorize each news item (e.g., Science & Tech, Sports, Economy, International).
    - For every news item, provide the "Event Summary".
    - Most Importantly: Provide "Historical Context (2021 Onwards)" linking today's event to relevant past patterns to prepare students for exam trends.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "daily_bulletin_date": "Today",
        "news_categories": [
            {{
                "category": "string",
                "headline": "string",
                "event_summary": "string",
                "historical_context_and_exam_relevance": "string"
            }}
        ]
    }}
    
    RAW NEWS DATA:
    {raw_news[:8000]}
    """
    
    while CURRENT_KEY_INDEX < len(GROQ_API_KEYS):
        try:
            groq_client = Groq(api_key=GROQ_API_KEYS[CURRENT_KEY_INDEX])
            completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.2, # Low temperature for factual news reporting
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_oracle():
    print("🌍 IGNITING AGENT: THE ORACLE...")
    news_folder = "8_oracle_newsroom"
    
    for filename in os.listdir(news_folder):
        if not filename.endswith(".txt") or not filename.startswith("RAW_"): continue
        
        out_filename = filename.replace("RAW_", "PROCESSED_").replace(".txt", ".json")
        if os.path.exists(os.path.join(news_folder, out_filename)): continue
            
        print(f"   ⚙️ Analyzing and structuring daily news: {filename}")
        with open(os.path.join(news_folder, filename), 'r', encoding='utf-8') as f:
            raw_news = f.read()
            
        oracle_data, status = process_with_oracle(raw_news)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if oracle_data:
            with open(os.path.join(news_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(oracle_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Daily Current Affairs saved to {news_folder}/{out_filename}")

if __name__ == "__main__":
    run_oracle()