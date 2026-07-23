import os
import time
import json
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from groq import Groq

# =====================================================================
# 🔑 DYNAMIC KEY LOADER (Reads from keys_backup.txt)
# =====================================================================
def load_api_keys():
    keys = []
    try:
        with open("keys_backup.txt", "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("gsk_"):
                    keys.append(stripped)
    except Exception as e:
        print("⚠️ Could not read keys_backup.txt. Make sure it exists!")
    return keys

GROQ_API_KEYS = load_api_keys()
CURRENT_KEY_INDEX = 0

# =====================================================================
# 🌐 TARGET ROSTER
# =====================================================================
TARGET_WEBSITES = [
    {"name": "HaryanaJobs", "base_url": "https://haryanajobs.in/", "page_suffix": "page/{}/", "start_page": 1},
    {"name": "FreeJobAlert", "base_url": "https://www.freejobalert.com/", "page_suffix": "page/{}/", "start_page": 1}
]

def extract_with_groq(text_content: str, source_url: str):
    """Parses raw webpage text using Groq AI and handles key rotation."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS:
        return None, "NO_KEYS"

    prompt = f"""
    You are the "Big Mouth" data extraction agent for the Gaandivam EdTech platform.
    Extract all exam parameters from this web text. Output ONLY valid JSON.
    REQUIRED SCHEMA: {{"conducting_body": "string", "exam_name": "string", "job_posts_covered": ["list"], "application_dates": {{"start_date": "string or null", "end_date": "string or null"}}, "fee_structure": "string or null", "selection_stages": ["list"], "detailed_syllabus": {{"Subject": ["topics"]}}}}
    TEXT: {text_content[:8000]}
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
            
            data = json.loads(completion.choices[0].message.content)
            data["data_source_url"] = source_url
            data["extraction_timestamp"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            return data, "SUCCESS"
            
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                print(f"   ⚠️ Engine {CURRENT_KEY_INDEX + 1} Overheated. Hot-swapping to Engine {CURRENT_KEY_INDEX + 2}...")
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
                
    return None, "ALL_KEYS_DEAD"

def run_big_mouth():
    print(f"🚀 IGNITING AGENT: BIG MOUTH...\n")
    
    if not GROQ_API_KEYS:
        print("🛑 ERROR: No API keys found in keys_backup.txt! System Halting.")
        return

    intake_folder = "1_big_mouth_intake"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for site in TARGET_WEBSITES:
        print(f"==================================================")
        print(f"🌐 TARGET ENGAGED: {site['name']}")
        print(f"==================================================")
        
        page_num = site['start_page']
        
        while True: 
            print(f"\n📄 Scraping {site['name']} - Page {page_num}...")
            url = site['base_url'] if page_num == 1 else site['base_url'] + site['page_suffix'].format(page_num)
            
            try:
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code != 200: 
                    print(f"🛑 Reached end of {site['name']} or blocked. Moving to next target.")
                    break
                    
                soup = BeautifulSoup(res.content, "html.parser")
                links = list(set([a['href'] for a in soup.find_all('a', href=True) if "http" in a['href'] and ("job" in a['href'] or "notification" in a['href'])]))
                
                if not links: 
                    print(f"🛑 No valid links found. Ending {site['name']} extraction.")
                    break
                    
                for job_url in links:
                    if "category" in job_url or "author" in job_url: continue
                    print(f"   🔍 Swallowing: {job_url}")
                    
                    try:
                        job_res = requests.get(job_url, headers=headers, timeout=10)
                        job_soup = BeautifulSoup(job_res.content, "html.parser")
                        for tag in job_soup(["script", "style", "nav", "footer", "header"]): tag.decompose()
                        
                        condensed_payload = "\n".join([line.strip() for line in job_soup.get_text(separator="\n").splitlines() if line.strip()][:250]) 
                        
                        json_data, status = extract_with_groq(condensed_payload, job_url)
                        
                        if status == "ALL_KEYS_DEAD": 
                            print("\n⏸️ ENGINE SHUTDOWN. ALL KEYS EXHAUSTED FOR TODAY.")
                            return 
                        
                        if json_data:
                            filename = f"RAW_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
                            filepath = os.path.join(intake_folder, filename)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                json.dump(json_data, f, indent=4, ensure_ascii=False)
                            print(f"   ✅ Saved to {intake_folder}/{filename}")
                        
                        time.sleep(1.5) 
                    except requests.exceptions.RequestException: 
                        continue
                page_num += 1 
            except requests.exceptions.RequestException: 
                break 

if __name__ == "__main__":
    run_big_mouth()