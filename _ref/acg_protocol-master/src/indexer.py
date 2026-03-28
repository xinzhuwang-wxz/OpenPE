import os
import re
import requests
from bs4 import BeautifulSoup

from utils import generate_shi
from mongodb_client import MongoDBClient, store_source_chunks

import argparse
import google.generativeai as genai

def get_css_selector(element):
    """
    Generates a unique CSS selector for a given BeautifulSoup element.
    """
    path = []
    while element.name:
        if element.has_attr('id'):
            path.insert(0, '#' + element['id'])
            break
        
        # Get siblings with the same tag name
        siblings = list(element.find_previous_siblings(element.name)) + \
                   list(element.find_next_siblings(element.name))
        
        if len(siblings) > 0:
            # If there are siblings, find the index
            idx = sum(1 for s in element.previous_siblings if s.name == element.name)
            path.insert(0, f"{element.name}:nth-of-type({idx + 1})")
        else:
            # No siblings, just use the tag name
            path.insert(0, element.name)
        
        element = element.parent
        if element is None:
            break
    return ' > '.join(path)

def index_url(args):
    """
    Fetches content from a given URL, parses it into chunks, and stores them in MongoDB.

    :param url: The URL of the web page to index.
    """
    url = args.url
    print(f"Fetching content from: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        source_uri = url
        source_version = "1.0"

        shi = generate_shi(source_uri, source_version)
        
        mongo_client = MongoDBClient()

        all_sentences_data = []
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']):
            # Skip elements that are likely citation notes
            if element.has_attr('id') and element['id'].startswith('cite_note-'):
                continue
            
            text_content = element.get_text(separator=' ', strip=True)
            if text_content:
                sentences_from_element = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+', text_content)
                for sentence in sentences_from_element:
                    if sentence.strip():
                        all_sentences_data.append({
                            "text": sentence.strip(),
                            "loc_selector": get_css_selector(element)
                        })

        if not all_sentences_data:
            print(f"No processable sentences found for {url}")
            return

        chunks_to_store = []
        current_chunk_sentences = []
        current_chunk_loc_selector = None
        
        for sentence_data in all_sentences_data:
            current_chunk_sentences.append(sentence_data['text'])
            if current_chunk_loc_selector is None:
                current_chunk_loc_selector = sentence_data['loc_selector']

            if len(current_chunk_sentences) == args.sentences_per_chunk:
                chunk_content = " ".join(current_chunk_sentences)
                chunks_to_store.append({
                    "content": chunk_content,
                    "chunk_id": f"chunk_{len(chunks_to_store) + 1}",
                    "loc_selector": current_chunk_loc_selector,
                    "metadata": {"uri": url, "loc": current_chunk_loc_selector}
                })
                current_chunk_sentences = []
                current_chunk_loc_selector = None

        # Add any remaining sentences as the last chunk
        if current_chunk_sentences:
            chunk_content = " ".join(current_chunk_sentences)
            chunks_to_store.append({
                "content": chunk_content,
                "chunk_id": f"chunk_{len(chunks_to_store) + 1}",
                "loc_selector": current_chunk_loc_selector,
                "metadata": {"uri": url, "loc": current_chunk_loc_selector}
            })

        if not chunks_to_store:
            print(f"No processable chunks found for {url}")
            return

        print(f"Storing {len(chunks_to_store)} chunks in MongoDB for {url} with SHI: {shi}...")
        store_source_chunks(mongo_client, shi, chunks_to_store, genai.embed_content, sentences_per_chunk=args.sentences_per_chunk)
        print(f"Successfully indexed {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'mongo_client' in locals() and mongo_client.client:
            mongo_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index a web page content into MongoDB.")
    parser.add_argument("url", type=str, help="The URL of the web page to index.")
    parser.add_argument("--sentences_per_chunk", type=int, default=3,
                        help="Number of sentences to group into each chunk (default: 3).")
    args = parser.parse_args()

    index_url(args)
