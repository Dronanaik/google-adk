import streamlit as st
import sys
import os

# Add the current directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from data_analysis_agent.agent.agent import create_agent, init_db_connection, run_agent

st.set_page_config(
    page_title="Data Analysis Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📊 Data Analysis Agent")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        api_key = st.text_input("Google API Key", type="password", help="Enter your Google AI Studio API Key")
        
        # Initialize Agent if API key is provided and agent not set
        if api_key and "agent" not in st.session_state:
             st.session_state.agent = create_agent(api_key=api_key)
        elif "agent" not in st.session_state:
             st.warning("Please enter your Google API Key to start.")

        st.selectbox("Model", ["Gemini 2.5 Pro", "Gemini 2.5 Flash"])
        
        with st.expander("Database Connection", expanded=True):
            db_type = st.selectbox("Type", ["PostgreSQL", "MySQL", "BigQuery"])
            
            config = {"type": db_type}
            if db_type in ["PostgreSQL", "MySQL"]:
                config["host"] = st.text_input("Host", value="localhost")
                config["port"] = st.text_input("Port", value="5432" if db_type == "PostgreSQL" else "3306")
                config["dbname"] = st.text_input("Database")
                config["user"] = st.text_input("User")
                config["password"] = st.text_input("Password", type="password")
            elif db_type == "BigQuery":
                config["project_id"] = st.text_input("Project ID")
                config["dataset_id"] = st.text_input("Dataset ID")
            
            if st.button("Connect"):
                try:
                    init_db_connection(config)
                    st.success("Connected to database!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
            
        if st.button("Clear Chat History"):
            st.session_state.messages = []

    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                # Invoke the agent using the synchronous wrapper
                response = run_agent(st.session_state.agent, prompt)
            except Exception as e:
                response = f"Error invoking agent: {str(e)}\n\n(Ensure database is connected and agent is initialized)"

            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
