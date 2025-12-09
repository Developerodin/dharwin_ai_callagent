"""
Script to fetch and display agent data from Bolna AI
"""

import json
from bolna_agent import BolnaAgent
from config import BOLNA_API_KEY

def main():
    """Fetch and display agent data"""
    
    # Initialize the agent
    try:
        agent = BolnaAgent()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Use the provided agent ID
    agent_id = "b857f0a5-09e8-467c-901f-a871cde5d41d"
    agent.agent_id = agent_id
    
    print(f"📡 Fetching data for agent: {agent_id}\n")
    
    try:
        # Fetch agent details
        print("1️⃣ Fetching agent details...")
        agent_data = agent.get_agent(agent_id)
        
        # Save to JSON file
        output_file = "agent_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(agent_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Agent data saved to {output_file}\n")
        
        # Display key information
        print("📋 Agent Information:")
        print(f"   Name: {agent_data.get('agent_name', 'N/A')}")
        print(f"   Type: {agent_data.get('agent_type', 'N/A')}")
        print(f"   Status: {agent_data.get('agent_status', 'N/A')}")
        print(f"   Created: {agent_data.get('created_at', 'N/A')}")
        print(f"   Updated: {agent_data.get('updated_at', 'N/A')}")
        
        # Display tasks
        tasks = agent_data.get('tasks', [])
        print(f"\n📞 Tasks: {len(tasks)}")
        for i, task in enumerate(tasks, 1):
            print(f"   Task {i}: {task.get('task_type', 'N/A')}")
        
        # Display prompts
        prompts = agent_data.get('agent_prompts', {})
        if prompts:
            print(f"\n💬 Prompts:")
            for key, prompt_data in prompts.items():
                system_prompt = prompt_data.get('system_prompt', '')
                preview = system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt
                print(f"   {key}: {preview}")
        
        print(f"\n✅ Full data saved to {output_file}")
        
        # Optionally fetch executions for this agent
        print("\n2️⃣ Fetching recent executions...")
        try:
            executions = agent.list_executions(agent_id=agent_id, page_size=5)
            if isinstance(executions, dict) and 'data' in executions:
                exec_data = executions['data']
                print(f"   Found {len(exec_data)} recent executions")
                
                # Save executions to JSON
                exec_file = "agent_executions.json"
                with open(exec_file, 'w', encoding='utf-8') as f:
                    json.dump(executions, f, indent=2, ensure_ascii=False)
                print(f"   Executions saved to {exec_file}")
            else:
                print(f"   Executions data: {json.dumps(executions, indent=2)[:200]}...")
        except Exception as e:
            print(f"   ⚠️  Could not fetch executions: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

