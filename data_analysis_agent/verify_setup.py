import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_analysis_agent.agent.agent import create_agent, init_db_connection

def verify():
    print("Verifying Data Analysis Agent Setup...")
    
    # 1. Test Agent Creation
    try:
        agent = create_agent()
        print(f"✅ Agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return

    # 2. Test Tool Registration
    expected_tools = ['list_tables', 'get_schema', 'execute_sql']
    agent_tools = [tool.__name__ for tool in agent.tools]
    
    missing_tools = [tool for tool in expected_tools if tool not in agent_tools]
    
    if not missing_tools:
        print(f"✅ All expected tools registered: {agent_tools}")
    else:
        print(f"❌ Missing tools: {missing_tools}")

    # 3. Test DB Connection Init (Mock config)
    try:
        config = {"type": "postgresql", "host": "localhost", "dbname": "test", "user": "test", "password": "password"}
        init_db_connection(config)
        print("✅ Database connection initialized (Mock)")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    print("\nVerification Complete!")

if __name__ == "__main__":
    verify()
