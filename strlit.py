import streamlit as st
from oai import process_data
from langchainExperiment import multi_agent_workflow
from schema_page import schema_chat_page
def main():
    if "page" not in st.session_state: 
        st.session_state.page = "upload"
    if st.session_state.page == "upload": 
        st.title("Data Schema Preprocessing Pipeline")
        st.write("Upload your data schema document (PDF, image, or webpage).")
        
        # File uploader accepts PDFs and common image formats
        uploaded_file = st.file_uploader("Upload your file", type=["pdf", "png", "jpg", "jpeg", "csv"])
        
        if uploaded_file is not None:
            print("File upload success.")

        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            
            # Show file details
            file_details = {
                "filename": uploaded_file.name,
                "filetype": uploaded_file.type,
                "filesize": uploaded_file.size
            }
            st.json(file_details)
            print("uploaded_file")
            # Let the user specify the file type (could be auto-detected)
            file_type = st.selectbox("Select the document type", ["PDF", "Image", "Webpage", "CSV"])
            
            # Optional: Ask for additional context or metadata
            context_info = st.text_input("Enter any additional context (optional)")
            
            if st.button("Process Schema"):
                result=uploaded_file.read()
                explanation = process_data(result)
                print(explanation)
                document_content, canonical_schema, feedback = multi_agent_workflow(explanation)
                # # Invoke the LangGraph pipeline (here simulated by process_schema)
                # result = process_schema(uploaded_file, file_type, context_info)
                # st.write("Processed Schema:")
                # st.json(result)
                st.session_state.page = "chat"
                st.session_state.document_description = document_content
                st.session_state.canonical_schema = canonical_schema
                st.session_state.feedback = feedback
                
                
    if st.session_state.page == 'chat':
            schema_chat_page(st.session_state.document_description, st.session_state.canonical_schema, st.session_state.feedback )

                #st.experimental_rerun()
    # if st.session_state.page == "chat":
    #     document_description = st.session_state.document_description
    #     canonical_schema = st.session_state.canonical_schema
    #     feedback = st.session_state.feedback
    #     schema_chat_page(document_description, canonical_schema, feedback)

if __name__ == "__main__":
    main()

