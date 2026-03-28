import hashlib
import requests
import json
import re
from typing import Optional, List, Dict
import hashlib
import requests
import json
import re
from typing import Optional, List, Dict, Tuple
from bs4 import BeautifulSoup, Tag
from config import Config, log
import google.generativeai as genai

def generate_shi(canonical_uri: str, version_tag: str) -> str:
    """
    Generates the Source Hash Identity (SHI) using the configured algorithm.
    """
    data = f"{canonical_uri.strip().lower()}|{version_tag.strip().lower()}"
    return hashlib.new(Config.SHI_ALGORITHM, data.encode('utf-8')).hexdigest()

def fetch_and_validate_content(uri: str, selector: str, expected_snippet: str) -> Tuple[bool, str]:
    """
    Verifier Agent Logic: Fetches the source, navigates using the CSS selector, 
    and verifies the claim.
    Returns a tuple: (is_valid: bool, reason: str)
    """
    try:
        log.info(f"🌐 Fetching URI for verification: {uri}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(uri, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if not selector.startswith("css="):
             log.warning("Unsupported selector type. Verification failed.")
             return False, "Unsupported selector type."
        
        css_selector = selector.replace("css=", "")
        target_element: Optional[Tag] = soup.select_one(css_selector)
        
        # 3. Verify Claim
        if target_element:
            # Normalize text for robust comparison
            element_text = target_element.get_text().strip().replace('\n', ' ')
            
            # Simple substring check (Production would use NLP/Embedding comparison)
            if expected_snippet in element_text:
                log.info("✅ Structural verification passed.")
                return True, "Structural verification passed."
            else:
                log.warning(f"❌ Content mismatch at selector {css_selector}.")
                return False, "Content mismatch at selector."
        else:
            log.warning(f"❌ Element not found using selector: {css_selector}")
            return False, "Element not found using selector."

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            log.error(f"Request failed for {uri}: 403 Forbidden. Access denied.")
            return False, "Source access denied (403 Forbidden)."
        log.error(f"Request failed for {uri}: {e}")
        return False, f"Request failed: {e}"
    except requests.exceptions.RequestException as e:
        log.error(f"Request failed for {uri}: {e}")
        return False, f"Request failed: {e}"
    except Exception as e:
        log.error(f"General error during content validation: {e}")
        return False, f"General error during content validation: {e}"

def get_query_embedding(query: str) -> List[float]:
    """
    Abstracts the call to an external embedding model (e.g., OpenAI, Cohere).
    For a PoC, we return a mock vector since we cannot run a real model.
    """
    response = genai.embed_content(
        model=Config.EMBEDDING_MODEL,
        content=query,
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=Config.EMBEDDING_DIMENSION
    )
    return response['embedding']
