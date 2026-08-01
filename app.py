import streamlit as st
from agent import agent_executor, AgentState

st.set_page_config(page_title="Data Analyst Agent", page_icon="📊", layout="wide")

st.title("📊 Enterprise Data Analyst Agent")
st.markdown("Ask natural language questions about your database. The agent will write SQL, execute it, and auto-correct its own errors.")

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("E.g., What is our total net revenue from organic users?"):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status_text = st.empty()
        status_text.text("🤔 Thinking & writing SQL...")
        
        # Initialize the state for LangGraph
        initial_state = AgentState(
            question=prompt,
            schema_context="",
            sql_query="",
            sql_error="",
            data_result="",
            iteration_count=0
        )
        
        # Run the agent workflow
        final_state = agent_executor.invoke(initial_state)
        status_text.empty()
        
        # Provide an expander to show the "Agent's Work" (SQL and self-correction loops)
        with st.expander("🛠️ View Agent's Work (SQL & Loops)"):
            st.markdown(f"**Iterations needed:** {final_state['iteration_count']}")
            st.code(final_state['sql_query'], language="sql")
            if final_state['sql_error']:
                st.error(f"Final Error: {final_state['sql_error']}")
                
        # Display the final data result
        if final_state["data_result"]:
            st.markdown("### Results")
            st.markdown(final_state["data_result"])
            st.session_state.messages.append({"role": "assistant", "content": final_state["data_result"]})
        else:
            msg = "I couldn't retrieve the data. Please check the logs."
            st.warning(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})