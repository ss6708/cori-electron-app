"""
Additional methods for the FinancialKnowledgeBase class.
"""

def _add_knowledge_item(self, item: Dict[str, Any], domain: str) -> str:
    """
    Add a knowledge item to the long-term memory.
    
    Args:
        item: Knowledge item
        domain: Domain for the knowledge
        
    Returns:
        Document ID
    """
    # Extract content and metadata
    content = item.get("content", "")
    metadata = item.get("metadata", {})
    
    # Add title to metadata if available
    if "title" in item:
        metadata["title"] = item["title"]
    
    # Add to long-term memory
    doc_id = self.long_term_memory.add_document(
        text=content,
        metadata=metadata,
        domain=domain
    )
    
    return doc_id

def save_domain_knowledge(self, domain: str) -> bool:
    """
    Save domain knowledge to file.
    
    Args:
        domain: Domain to save knowledge for
        
    Returns:
        True if successful, False otherwise
    """
    domain_dir = os.path.join(self.knowledge_dir, domain)
    os.makedirs(domain_dir, exist_ok=True)
    
    # Get all documents for the domain
    documents = self.long_term_memory.get_documents_by_metadata(
        metadata_filters={"type": "financial_knowledge", "domain": domain},
        domain=domain
    )
    
    if not documents:
        return False
    
    # Convert to knowledge items
    knowledge_items = []
    for doc in documents:
        item = {
            "content": doc["text"],
            "metadata": doc["metadata"]
        }
        
        # Add title if available
        if "title" in doc["metadata"]:
            item["title"] = doc["metadata"]["title"]
        
        knowledge_items.append(item)
    
    # Save to file
    file_path = os.path.join(domain_dir, f"{domain}_knowledge.json")
    try:
        with open(file_path, 'w') as f:
            json.dump(knowledge_items, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving knowledge to {file_path}: {e}")
        return False

def add_knowledge_item(
    self,
    title: str,
    content: str,
    domain: str,
    topic: str,
    subtopics: List[str] = None
) -> str:
    """
    Add a knowledge item to the knowledge base.
    
    Args:
        title: Knowledge item title
        content: Knowledge item content
        domain: Domain for the knowledge
        topic: Topic for the knowledge
        subtopics: Optional list of subtopics
        
    Returns:
        Document ID
    """
    # Create metadata
    metadata = {
        "type": "financial_knowledge",
        "domain": domain,
        "topic": topic,
        "title": title
    }
    
    # Add subtopics if provided
    if subtopics:
        metadata["subtopics"] = subtopics
    
    # Add to long-term memory
    doc_id = self.long_term_memory.add_document(
        text=content,
        metadata=metadata,
        domain=domain
    )
    
    return doc_id

def search_knowledge(
    self,
    query: str,
    domain: Optional[str] = None,
    topic: Optional[str] = None,
    k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for relevant knowledge.
    
    Args:
        query: The search query
        domain: Optional domain to search in
        topic: Optional topic to filter by
        k: Number of results to return
        
    Returns:
        List of search results
    """
    # Ensure domain knowledge is loaded
    if domain and not self.loaded_knowledge.get(domain, False):
        self.load_domain_knowledge(domain)
    
    # Create filters
    filters = {"type": "financial_knowledge"}
    
    if topic:
        filters["topic"] = topic
    
    # Search for relevant knowledge
    results = self.long_term_memory.search(
        query=query,
        domain=domain,
        filters=filters,
        k=k
    )
    
    return results

def get_knowledge_by_topic(
    self,
    domain: str,
    topic: str
) -> List[Dict[str, Any]]:
    """
    Get knowledge items by topic.
    
    Args:
        domain: Domain to search in
        topic: Topic to filter by
        
    Returns:
        List of knowledge items
    """
    # Ensure domain knowledge is loaded
    if not self.loaded_knowledge.get(domain, False):
        self.load_domain_knowledge(domain)
    
    # Get documents by metadata
    documents = self.long_term_memory.get_documents_by_metadata(
        metadata_filters={"type": "financial_knowledge", "domain": domain, "topic": topic},
        domain=domain
    )
    
    return documents

def extract_knowledge_from_events(
    self,
    events: List[Event],
    domain: str
) -> Optional[str]:
    """
    Extract knowledge from events and add to knowledge base.
    
    Args:
        events: List of events to extract knowledge from
        domain: Domain for the knowledge
        
    Returns:
        Document ID if knowledge was extracted, None otherwise
    """
    # Ensure we have enough events
    if len(events) < 3:
        return None
    
    # Use OpenAI to extract knowledge
    from openai import OpenAI
    import os
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Convert events to text
    events_text = "\n\n".join([
        f"Role: {event.role}\nContent: {event.content}"
        for event in events
    ])
    
    # Create prompt
    prompt = f"""
    Extract financial knowledge from the following conversation about {domain} modeling:
    
    {events_text}
    
    Please identify key financial concepts, parameters, methodologies, or best practices
    that could be useful for future reference. Format your response as:
    
    Title: [Concise title for this knowledge]
    
    Content: [Detailed explanation of the financial knowledge]
    
    Topic: [Specific topic within {domain}]
    
    Subtopics: [Comma-separated list of relevant subtopics]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial knowledge extraction system."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        extracted_text = response.choices[0].message.content
        
        # Parse the extracted knowledge
        lines = extracted_text.strip().split("\n")
        
        title = ""
        content = ""
        topic = ""
        subtopics = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Title:"):
                title = line[6:].strip()
                current_section = "title"
            elif line.startswith("Content:"):
                content = line[8:].strip()
                current_section = "content"
            elif line.startswith("Topic:"):
                topic = line[6:].strip()
                current_section = "topic"
            elif line.startswith("Subtopics:"):
                subtopics_str = line[10:].strip()
                subtopics = [s.strip() for s in subtopics_str.split(",")]
                current_section = "subtopics"
            elif current_section == "content":
                content += "\n" + line
        
        # Validate extracted knowledge
        if not title or not content or not topic:
            return None
        
        # Add to knowledge base
        doc_id = self.add_knowledge_item(
            title=title,
            content=content,
            domain=domain,
            topic=topic,
            subtopics=subtopics
        )
        
        return doc_id
    
    except Exception as e:
        print(f"Error extracting knowledge: {e}")
        return None
