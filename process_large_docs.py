import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(document_text, chunk_size=2000, chunk_overlap=200):
    """
    Breaks down the document text into smaller chunks using a recursive character splitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(document_text)

def summarize_chunk(chunk, model="gpt-3.5-turbo", max_tokens=150):
    """
    Summarizes a single text chunk using the OpenAI API.
    """
    prompt = f"Summarize the following text concisely:\n\n{chunk}\n\nSummary:"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.5  # adjust as needed
    )
    return response["choices"][0]["message"]["content"].strip()

def summarize_document(document_text):
    """
    Splits the document into chunks, summarizes each chunk, and then summarizes the combined summaries.
    """
    # Split the document into manageable chunks
    chunks = chunk_document(document_text)
    
    # Summarize each chunk
    chunk_summaries = []
    for chunk in chunks:
        summary = summarize_chunk(chunk)
        chunk_summaries.append(summary)
    
    # Combine all the chunk summaries into one text block
    combined_summary = "\n".join(chunk_summaries)
    
    # Optionally, further summarize the combined summary to get a final short summary
    final_summary = summarize_chunk(combined_summary)
    return final_summary

# Example of incorporating into your workflow:
def process_large_document(document_text):
    """
    This function can be incorporated as a node in your multi-agent workflow.
    It takes a large document, summarizes it, and returns the summary.
    """
    summary = summarize_document(document_text)
    return summary

# # Example usage:
# if __name__ == "__main__":
#     # Assume you read a large document into 'large_text'
#     with open("large_document.txt", "r", encoding="utf-8") as f:
#         large_text = f.read()
    
#     final_summary = process_large_document(large_text)
#     print("Final Summary:")
#     print(final_summary)