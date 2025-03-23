from IPython.display import display, Markdown
from langgraph.graph import Graph, START
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.globals import set_debug
from oai import model_name, nvidia_api, process_data

set_debug(True)


def multi_agent_workflow(data):
    llm = ChatNVIDIA(model_name=model_name, base_url="https://integrate.api.nvidia.com/v1", api_key=nvidia_api)

    data_understander_prompt = PromptTemplate(
        input_variables=["document_content"],
        template='''
        You are an intelligent schema extraction agent.
        Extract the data schema from the following document content using any necessary techniques (e.g., OCR, text parsing, or multimodal analysis).

        Document Content:
        {document_content}

        Please output the schema as a YAML list where each entry includes the column name and any associated metadata (if available).
        '''

    )

    alink_prompt = PromptTemplate(
        input_variables= ["raw_schema", "document_content"], 
        template="""
                        You are a field disambiguation agent. Given the {document_content} and the following information: 
                            Given the following raw schema (a list of column names and metadata):

                            {raw_schema}

                            Use similarity search and heuristic rules to map any ambiguous or non-standard column names to their standardized equivalents.
                            Output the mapping as a YAML document in the format:
                            ---
                            original_field: standardized_field
                            ...



                    """

    )

    avis_prompt = PromptTemplate(
        input_variables = ["mapped_schema", "raw_schema", "document_content"],
        template='''

        
            You are a schema transformation agent.
            Given the {raw_schema} and {document_content} and the following information: 
    Convert the following mapped schema:

    {mapped_schema}

    into a canonical schema following the standard rules provided.
    Output the final canonical schema as a well-structured YAML document. 
    Just give me the yaml to display it on streamlit. I just need the yaml.

        '''


    )

    feedback_prompt = PromptTemplate(

        input_variables=["canonical_schema", "mapped_schema", "raw_schema", "document_content"], 
        template="""

        Given the {mapped_schema}, {raw_schema}, {document_content}, 
    You are a reviewer agent.
    Please review the following canonical schema in YAML format:

    {canonical_schema}

    If you identify any issues or improvements, provide specific corrections or suggestions in YAML format.
    If the schema is acceptable as is, simply reply with "Schema approved".
    """

    )

    data_understander_chain = data_understander_prompt | llm
    alink_chain = alink_prompt | llm
    avis_chain = avis_prompt | llm
    feedback_chain = feedback_prompt | llm


    def data_understander_node(input_dict):
        document_content = input_dict["document_content"]
        raw_schema = data_understander_chain.invoke({"document_content":document_content})
        if hasattr(raw_schema, 'content'):
            raw_schema = raw_schema.content
        return {'raw_schema': raw_schema, 'document_content':document_content}

    def alink_node(input_dict):
        document_content = input_dict["document_content"]
        raw_schema = input_dict["raw_schema"]
        mapped_schema = alink_chain.invoke({'raw_schema': raw_schema,'document_content': document_content })
        if hasattr(mapped_schema,'content'):
            mapped_schema = mapped_schema.content
        
        return {'mapped_schema': mapped_schema, 'raw_schema': raw_schema,'document_content': document_content }

    def avis_node(input_dict):
        document_content=input_dict["document_content"]
        raw_schema=input_dict["raw_schema"]
        mapped_schema = input_dict["mapped_schema"]
        canonical_schema = avis_chain.invoke({"mapped_schema": mapped_schema, "document_content": document_content, "raw_schema": raw_schema})
        if hasattr(canonical_schema, 'content'):
            canonical_schema = canonical_schema.content
        
        return {'canonical_schema': canonical_schema, "mapped_schema": mapped_schema, "document_content": document_content, "raw_schema": raw_schema}

    def feedback_node(input_dict):
        document_content=input_dict["document_content"]
        raw_schema=input_dict["raw_schema"]
        mapped_schema = input_dict["mapped_schema"]
        canonical_schema = input_dict["canonical_schema"]
        feedback = feedback_chain.invoke({"canonical_schema": canonical_schema,"mapped_schema":  mapped_schema, "document_content": document_content, "raw_schema": raw_schema})
        if hasattr(feedback, 'content'): 
            feedback = feedback.content

        return {'feedback': feedback, "canonical_schema": canonical_schema,"mapped_schema":  mapped_schema, "document_content": document_content, "raw_schema": raw_schema}


    graph = Graph()

    graph.add_node("Data Understanding Agent", data_understander_node)
    graph.add_node("alink Agent", alink_node)
    graph.add_node("Avis Agent", avis_node)
    graph.add_node("Feedback Agent", feedback_node)

    graph.add_edge(START, "Data Understanding Agent")
    graph.add_edge("Data Understanding Agent", "alink Agent")
    graph.add_edge("alink Agent","Avis Agent")
    graph.add_edge("Avis Agent","Feedback Agent")

    graph.set_finish_point("Feedback Agent")

    workflow=graph.compile()

    workflow_result = workflow.invoke({
        "document_content": data
    })

    print("Workflow Result: ")
    print(workflow_result)

    if workflow_result is None: 
        print("Error: Workflow returned None. Check node execution or LLM invocation.")
    else: 
        canonical_schema =workflow_result.get("canonical_schema", "No canonical provided")
        
        raw_schema= workflow_result.get("raw_schema", "No raw schema!")
        
        mapped_schema= workflow_result.get("mapped_schema", "No mapped schema provided")

        document_content = workflow_result.get('document_content', "No document content provided")

        feedback =   workflow_result.get('feedback', "No feedback provided")

        print(f""" 
        
              
        ### document_content
        {document_content}
        
         ### raw_schema
        {raw_schema}
        
        ###  mapped_schema
        {mapped_schema}

        ### canonical_schema
        {canonical_schema}
                         
        ###Feedback: 
        {feedback}




""")
        return document_content, canonical_schema, feedback


        









