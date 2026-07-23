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

def process_with_examiner(textbook_data):
    """Generates high-level mock tests based on Tony Stark's textbooks."""
    global CURRENT_KEY_INDEX
    
    if not GROQ_API_KEYS: return None, "NO_KEYS"

    prompt = f"""
    You are 'The Examiner', a strict and brilliant exam setter for the Gaandivam EdTech platform.
    Your task is to take the provided Study Material/Textbook Content and generate a highly challenging, concept-driven Multiple Choice Question (MCQ) Mock Test.
    
    CRITICAL INSTRUCTIONS:
    - Generate exactly 5 highly analytical questions based ONLY on the provided text. (We will scale this to 30 later).
    - Do not ask basic trivia; ask questions that require application of the concepts.
    - Provide 4 plausible options (A, B, C, D) and specify the correct answer.
    - Write a detailed explanation for WHY the answer is correct based on the visionary concepts.
    - Output ONLY valid JSON.
    
    REQUIRED SCHEMA:
    {{
        "exam_name": "string",
        "test_type": "Topic-Specific Mock Test",
        "questions": [
            {{
                "question_text": "string",
                "options": {{
                    "A": "string",
                    "B": "string",
                    "C": "string",
                    "D": "string"
                }},
                "correct_answer": "A, B, C, or D",
                "explanation": "string"
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
                temperature=0.2, # Low temperature for factual consistency in questions
                response_format={"type": "json_object"}
            )
            return json.loads(completion.choices[0].message.content), "SUCCESS"
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                CURRENT_KEY_INDEX += 1 
            else:
                return None, "ERROR"
    return None, "ALL_KEYS_DEAD"

def run_examiner():
    print("📝 IGNITING AGENT: THE EXAMINER...")
    input_folder = "6_tony_stark_textbooks"
    output_folder = "10_examiner_tests"
    
    for filename in os.listdir(input_folder):
        if not filename.endswith(".json"): continue
        
        # Replace the 'TEXTBOOK_' prefix with 'TEST_'
        out_filename = filename.replace("TEXTBOOK_", "TEST_")
        if os.path.exists(os.path.join(output_folder, out_filename)): continue
            
        print(f"   ⚙️ Forging mock test for: {filename}")
        with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
            textbook_data = json.load(f)
            
        test_data, status = process_with_examiner(textbook_data)
        
        if status == "ALL_KEYS_DEAD":
            print("🛑 API Keys exhausted.")
            break
            
        if test_data:
            with open(os.path.join(output_folder, out_filename), 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=4, ensure_ascii=False)
            print(f"   ✅ Mock Test saved to {output_folder}/{out_filename}")

if __name__ == "__main__":
    run_examiner()