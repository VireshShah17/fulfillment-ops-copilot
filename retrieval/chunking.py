import os
import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
        Pydantic structure for structured document chunks.
    """
    chunk_id: str = Field(description = "Unique identifier for the text chunk")
    text: str = Field(description = "Text content with pre-pended breadcrumbs context")
    metadata: Dict[str, Any] = Field(default_factory = dict, description = "Hierarchical paths and source info")


def parse_markdown_sections(content: str) -> List[Dict[str, Any]]:
    """
        Splits markdown file content into logical components based on #, ##, ### headers.
    """
    lines = content.split('\n')
    sections = []
    current_headers = {1: "", 2: "", 3: ""}
    current_text_lines = []
    # Regex matching headers up to level 3
    header_pattern = re.compile(r'^(#{1,3})\s+(.*)$')
    
    for line in lines:
        match = header_pattern.match(line)
        if match:
            # Save the current section before switching contexts
            if current_text_lines:
                text_content = "\n".join(current_text_lines).strip()

                if text_content:
                    sections.append({
                        "headers": current_headers.copy(),
                        "text": text_content
                    })
                current_text_lines = []
            
            level = len(match.group(1))
            title = match.group(2).strip()
            # Update header hierarchy
            current_headers[level] = title

            for l in range(level + 1, 4):
                current_headers[l] = ""
        else:
            current_text_lines.append(line)
            
    # Capture the last remaining block
    if current_text_lines:
        text_content = "\n".join(current_text_lines).strip()

        if text_content:
            sections.append({
                "headers": current_headers.copy(),
                "text": text_content
            })
            
    return sections


def get_breadcrumbs(filename: str, headers: Dict[int, str]) -> str:
    """
        Formats standard contextual metadata path strings.
    """
    path_components = [headers[i] for i in range(1, 4) if headers[i]]
    section_path = " > ".join(path_components) if path_components else "Root"
    return f"[Doc: {filename} | Section: {section_path}]"


def chunk_markdown_file(file_path: str, max_words: int = 450) -> List[Chunk]:
    """
        Reads and breaks a single markdown document into structure-aware atomic chunks.
    """
    filename = os.path.basename(file_path)
    
    with open(file_path, 'r', encoding = 'utf-8') as f:
        content = f.read()
        
    sections = parse_markdown_sections(content)
    chunks = []
    chunk_counter = 0
    
    for section in sections:
        headers = section["headers"]
        text_block = section["text"]
        # Calculate approximate word tokens
        paragraphs = text_block.split('\n\n')
        current_sub_block = []
        current_word_count = 0
        
        for para in paragraphs:
            para = para.strip()

            if not para:
                continue

            para_words = len(para.split())
            
            if current_word_count + para_words > max_words and current_sub_block:
                # Flush the sub-split accumulation block
                chunk_counter += 1
                sub_text = "\n\n".join(current_sub_block)
                breadcrumbs = get_breadcrumbs(filename, headers)
                final_text = f"{breadcrumbs}\n{sub_text}"
                
                chunks.append(Chunk(
                    chunk_id = f"{filename.replace('.', '_')}_{chunk_counter}",
                    text = final_text,
                    metadata = {
                        "source": filename,
                        "hierarchy": [h for h in headers.values() if h]
                    }
                ))
                current_sub_block = []
                current_word_count = 0
                
            current_sub_block.append(para)
            current_word_count += para_words
            
        # Append remaining accumulated paragraphs
        if current_sub_block:
            chunk_counter += 1
            sub_text = "\n\n".join(current_sub_block)
            breadcrumbs = get_breadcrumbs(filename, headers)
            final_text = f"{breadcrumbs}\n{sub_text}"
            
            chunks.append(Chunk(
                chunk_id = f"{filename.replace('.', '_')}_{chunk_counter}",
                text = final_text,
                metadata = {
                    "source": filename,
                    "hierarchy": [h for h in headers.values() if h]
                }
            ))
            
    return chunks


def chunk_all_documents(docs_dir: str = "data/docs") -> List[Chunk]:
    """
        Scans doc directories to batch compile standard layout chunks.
    """
    all_chunks = []

    if not os.path.exists(docs_dir):
        return all_chunks
        
    for file in os.listdir(docs_dir):
        
        if file.endswith('.md') or file.endswith('.txt'):
            all_chunks.extend(chunk_markdown_file(os.path.join(docs_dir, file)))
            
    return all_chunks
