import subprocess
import sys
import time

def print_header(title):
    print(f"\n{'='*60}")
    print(f" ⚙️  GAANDIVAM MASTER CONTROL: {title}")
    print(f"{'='*60}")

def run_agent(script_name):
    print(f"\n[SYSTEM] Triggering {script_name}...")
    try:
        # We use 'py' to match the Windows command you've been using
        result = subprocess.run(["py", script_name], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ ERROR: {script_name} failed to execute properly.")
    except FileNotFoundError:
        try:
            subprocess.run(["python", script_name], check=True)
        except Exception as e:
            print(f"❌ ERROR: Could not find Python executable to run {script_name}.")
    time.sleep(1) 

def master_run():
    print(r"""
      ____                  _ _                       
     / ___| __ _  __ _ _ __| (_)_   ____ _ _ __ ___   
    | |  _ / _` |/ _` | '__| | \ \ / / _` | '_ ` _ \  
    | |_| | (_| | (_| | |  | | |\ V / (_| | | | | | | 
     \____|\__,_|\__,_|_|  |_|_| \_/ \__,_|_| |_| |_| 
                                                      
    AUTONOMOUS EDTECH ENGINE - MASTER SEQUENCE INITIATED
    """)
    
    # PHASE 1: Data Gathering & Splitting
    print_header("PHASE 1: INTAKE & SPLITTING")
    run_agent("agent_big_mouth.py")
    run_agent("agent_enzymer.py")
    run_agent("agent_syllabi.py")
    
    # PHASE 2: Processing & Content Authoring
    print_header("PHASE 2: PROCESSING & CONTENT GENERATION")
    run_agent("agent_digester.py")
    run_agent("agent_tony_stark.py")
    
    # PHASE 3: Gamification & Assessments
    print_header("PHASE 3: GAMIFICATION & ASSESSMENTS")
    run_agent("agent_examiner.py")
    run_agent("agent_gamer.py")
    
    # PHASE 4: Marketing & Media
    print_header("PHASE 4: MARKETING & STUDIO PRODUCTION")
    run_agent("agent_burper.py")
    run_agent("agent_carbon.py")
    
    # PHASE 5: Parallel Standalone Tasks
    print_header("PHASE 5: HISTORICAL & NEWS DATA")
    run_agent("agent_archaeologist.py")
    run_agent("agent_oracle.py")
    
    print("\n✅ MASTER SEQUENCE COMPLETE. ALL DEPARTMENTS FULLY SYNCHRONIZED.")

if __name__ == "__main__":
    master_run()