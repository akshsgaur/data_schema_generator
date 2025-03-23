import streamlit as st

# This function defines the Schema Chat page
def schema_chat_page(document_description, canonical_schema, feedback):
    st.title("Schema Chat")
    st.write("Interact with your processed schema using the chatbot below.")
    
    # Divide the top of the page into three columns
    middle_col = st.columns(1)
    
    # with left_col:
    #     st.subheader("Document Description")
    #     st.markdown(document_description)
    
    
    st.subheader("Canonical Schema (YAML)")
    st.code(canonical_schema, language="yaml")
    
    # with right_col:
    #     st.subheader("Feedback")
    #     st.markdown(feedback)
    
    st.markdown("---")
    st.subheader("Chat with Schema")
    
    # Chat history stored in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        st.markdown(message)
    
    # Chat input box
    user_input = st.text_input("Your message:", key="chat_input")
    if st.button("Send"):
        if user_input:
            # Append user's message and a simulated bot reply
            st.session_state.chat_history.append(f"**User:** {user_input}")
            bot_response = f"**Bot:** You asked about '{user_input}'. (This is a simulated response.)"
            st.session_state.chat_history.append(bot_response)
            # st.experimental_rerun()