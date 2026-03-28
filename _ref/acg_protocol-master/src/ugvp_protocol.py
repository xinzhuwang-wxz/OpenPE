import re
import json
from json import JSONEncoder
from typing import Dict, List, Optional, Tuple

from config import Config, log

try:
    from bson.objectid import ObjectId
except ImportError:
    class ObjectId:
        def __init__(self, oid):
            self.oid = oid
        def __repr__(self):
            return f"ObjectId('{self.oid}')"
        def __str__(self):
            return str(self.oid)

class CustomJsonEncoder(JSONEncoder):
    """
    Custom JSON encoder to handle ObjectId objects.
    Converts ObjectId to its string representation.
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)

class UGVPProtocol:
    """
    The core class for the Universal Grounding and Verification Protocol (UGVP).
    Handles SHI generation, IGM parsing, and SSR management.
    """
    
    def __init__(self):
        self.acg_delimiters = Config.ACG_DELIMITERS
        
    def construct_igm(self, source_metadata: dict, claim_id: str = "C1") -> str:
        """
        Constructs an IGM from source metadata.
        """
        shi = source_metadata.get('shi')
        loc_selector = source_metadata.get('loc_selector')

        if not shi or not loc_selector:
            raise ValueError("Source metadata is missing 'shi' or 'loc_selector'.")

        shi_prefix = shi[:Config.SHI_PREFIX_LENGTH] # Use the defined prefix length
        return (
            f"{self.acg_delimiters['CLAIM_START']}"
            f"{claim_id}{self.acg_delimiters['CLAIM_SEP']}"
            f"{shi_prefix}{self.acg_delimiters['CLAIM_SEP']}"
            f"{loc_selector}"
            f"{self.acg_delimiters['CLAIM_END']}"
        )

    def construct_relationship_marker(self, relationship_id: str, rel_type: str, dependency_claims: List[str]) -> str:
        """
        Constructs a Relationship Marker (RM) from provided details.
        """
        if not relationship_id or not rel_type or not dependency_claims:
            raise ValueError("Relationship ID, type, and dependency claims are required.")

        dep_ids_str = ",".join(dependency_claims)
        return (
            f"{self.acg_delimiters['RELATION_START']}"
            f"{relationship_id}{self.acg_delimiters['RELATION_SEP']}"
            f"{rel_type}{self.acg_delimiters['RELATION_TYPE_SEP']}"
            f"{dep_ids_str}"
            f"{self.acg_delimiters['RELATION_END']}"
        )

    def generate_grounded_text(self, claim: str, source_metadata: dict, relationship_metadata: Optional[dict] = None) -> Tuple[str, dict, Optional[dict]]:
        """
        Generator Agent: Embeds the IGM and optionally an RM, and returns the text, SSR entry draft, and VAR entry draft.
        """
        shi = source_metadata['shi']
        loc = source_metadata['loc_selector'].replace("css=", "") # Clean selector for storage
        
        # 1. Create the unique CLAIM_ID
        claim_id = "C1" # Simplified: real agents would manage a sequential counter
        
        # 2. Construct the Inline Grounding Marker (IGM)
        igm = self.construct_igm(source_metadata, claim_id=claim_id)
        
        # 3. Create the SSR entry draft
        ssr_entry = {
            "SHI": shi,
            "Type": "Web Article",
            "Canonical_URI": source_metadata['source_uri'],
            "Location_Type": "CSS_Selector",
            "Loc_Selector": loc,
            "Chunk_ID": source_metadata['chunk_id'] # Add chunk_id to SSR entry
            # Note: Final verification status (VERIFIED/CONTRADICTED) is added later
        }

        var_entry = None
        rm = ""
        if relationship_metadata:
            relationship_id = relationship_metadata.get('RELATION_ID', 'R1')
            rel_type = relationship_metadata.get('TYPE')
            if not rel_type:
                raise ValueError("Relationship TYPE must be provided in relationship_metadata.")
            dep_claims = relationship_metadata.get('DEP_CLAIMS', [claim_id])
            rm = self.construct_relationship_marker(relationship_id, rel_type, dep_claims)
            
            var_entry = {
                "RELATION_ID": relationship_id,
                "TYPE": rel_type,
                "DEP_CLAIMS": dep_claims,
                "SYNTHESIS_PROSE": relationship_metadata.get('SYNTHESIS_PROSE', claim),
                "LOGIC_MODEL": relationship_metadata.get('LOGIC_MODEL'),
                "AUDIT_STATUS": "PENDING",
                "TIMESTAMP": relationship_metadata.get('TIMESTAMP', "") # Should be set by agent
            }
            if not var_entry["LOGIC_MODEL"]:
                raise ValueError("LOGIC_MODEL must be provided in relationship_metadata for VAR entry.")
        
        # The SSR block now contains both SSR and VAR entries
        ssr_var_block = (
            f"\n--- ACG_START ---\n"
            f"{json.dumps({'SSR': [ssr_entry], 'VAR': [var_entry] if var_entry else []}, indent=2)}\n"
            f"--- ACG_END ---"
        )
        
        return f"{claim} {igm}{rm}.{ssr_var_block}", ssr_entry, var_entry

    def parse_acg_data(self, original_text: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Optional[Dict[str, Dict]], Optional[Dict[str, Dict]]]:
        """
        The Verifier Agent uses this to extract all ACG data (IGMs, RMs, SSR, VAR).
        """
        claim_start, claim_sep, claim_end = self.acg_delimiters['CLAIM_START'], self.acg_delimiters['CLAIM_SEP'], self.acg_delimiters['CLAIM_END']
        rel_start, rel_sep, rel_type_sep, rel_end = self.acg_delimiters['RELATION_START'], self.acg_delimiters['RELATION_SEP'], self.acg_delimiters['RELATION_TYPE_SEP'], self.acg_delimiters['RELATION_END']

        escaped_claim_start = re.escape(claim_start)
        escaped_claim_sep = re.escape(claim_sep)
        escaped_claim_end = re.escape(claim_end)
        escaped_rel_start = re.escape(rel_start)
        escaped_rel_sep = re.escape(rel_sep)
        escaped_rel_type_sep = re.escape(rel_type_sep)
        escaped_rel_end = re.escape(rel_end)

        # Regex for IGMs
        igm_pattern = (
            rf'{escaped_claim_start}'          # claim start delimiter
            rf'(\w+)'                          # claim_id, like C1
            rf'{escaped_claim_sep}'            # claim separator
            rf'([A-Fa-f0-9]{{8,{Config.SHI_PREFIX_LENGTH}}})' # SHI prefix, min 8, max SHI_PREFIX_LENGTH
            rf'{escaped_claim_sep}'            # claim separator again
            rf'([^{claim_end}]+?)'             # capture text until claim end delimiter (non-greedy)
            rf'{escaped_claim_end}'
        )

        # Regex for RMs
        rm_pattern = (
            rf'{escaped_rel_start}'            # relation start delimiter
            rf'(\w+)'                          # relationship_id, like R1
            rf'{escaped_rel_sep}'              # relation separator
            rf'([^:{rel_end}]+?)'              # relationship type (non-greedy)
            rf'{escaped_rel_type_sep}'         # relation type separator
            rf'([^{rel_end}]+?)'               # dependency claims (non-greedy)
            rf'{escaped_rel_end}'              # relation end delimiter
        )

        igms = []
        all_igm_matches = list(re.finditer(igm_pattern, original_text, re.IGNORECASE))
        
        # Iterate through matches to extract claim_context
        for i, match in enumerate(all_igm_matches):
            start_index = 0
            if i > 0:
                prev_match_end = all_igm_matches[i-1].end()
                claim_text = original_text[prev_match_end:match.start()].strip()
            else:
                claim_text = original_text[0:match.start()].strip()

            igms.append({
                "claim_id": match.group(1),
                "shi": match.group(2),
                "loc": match.group(3),
                "claim_context": claim_text
            })
        log.debug(f"parse_acg_data found IGMs: {igms}")

        rms = []
        for match in re.finditer(rm_pattern, original_text, re.IGNORECASE):
            rms.append({
                "relationship_id": match.group(1),
                "type": match.group(2),
                "dep_claims": match.group(3).split(',')
            })

        ssr_dict = None
        var_dict = None
        acg_match = re.search(r"--- ACG_START ---\n(.*?)\n--- ACG_END ---", original_text, re.DOTALL)
        if acg_match:
            try:
                acg_json_str = acg_match.group(1)
                acg_data = json.loads(acg_json_str)
                log.debug(f"Parsed ACG data (full): {json.dumps(acg_data, indent=2)}") # Added detailed logging
                
                if 'SSR' in acg_data and isinstance(acg_data['SSR'], list):
                    # Use a composite key (SHI-Chunk_ID) for ssr_dict to ensure uniqueness
                    ssr_dict = {f"{item['SHI']}-{item['Chunk_ID']}": item for item in acg_data['SSR']}
                if 'VAR' in acg_data and isinstance(acg_data['VAR'], list):
                    var_dict = {item['RELATION_ID']: item for item in acg_data['VAR']}
            except json.JSONDecodeError as e:
                log.error(f"Failed to parse ACG JSON: {e}. Raw string: {acg_json_str[:500]}...")
                ssr_dict = None
                var_dict = None
        
        return igms, rms, ssr_dict, var_dict

    def assemble_final_output(self, generated_text: str, verified_ssr: Dict[str, Dict], verified_var: Dict[str, Dict]) -> str:
        """
        Compiles the text and the verified ACG block (SSR and VAR) into the final document.
        """
        ACG_MARKER_START = "\n--- ACG_START ---\n"
        ACG_MARKER_END = "\n--- ACG_END ---\n"
        
        ssr_list = list(verified_ssr.values())
        var_list = list(verified_var.values())
        
        acg_data = {
            "SSR": ssr_list,
            "VAR": var_list
        }
        acg_json = json.dumps(acg_data, indent=2, cls=CustomJsonEncoder)
        
        # The generated_text from StrandAgent should already contain the claim and IGM.
        # We only need to append the ACG block.
        return (
            f"{generated_text.strip()}\n"
            f"{ACG_MARKER_START}"
            f"{acg_json}\n"
            f"{ACG_MARKER_END}"
        )
