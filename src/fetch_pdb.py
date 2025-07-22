"""
Fetch recent PDB entries from the EBI PDBe api from the last 5 years:
Challenges faced:
- max-limit is set 1000 results and cannot be tweaked
- API has no support for pagination
"""

import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict
import structlog

log = structlog.get_logger()

def fetch_recent_pdb_entries(max_results: int = 1000) ->  List[Dict[str, str]]:
    """
        Fetches recent PDB entries from the EBI PDBe API within the last 5 years.
        Extracts only those with associated PubMed IDs.

        :param max_results: Maximum number of entries to retrieve (default: 1000)
        returns: List[Dict[str, str]]: List of dicts containing pdb_id and pubmed_id
        """

    url = "https://www.ebi.ac.uk/ebisearch/ws/rest/pdbe"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=5 * 365)
    start_str = start_date.strftime("%Y/%m/%d")
    end_str = end_date.strftime("%Y/%m/%d")

    params = {
        "query": "*:*",
        "size": max_results,
        "fields": "id,description,title,GEO,PUBMED,acc,domain_source,name",
        "filter": f'creation_date:["{start_str}" TO "{end_str}"]',
        "format": "json",
    }

    log.info("Fetching recent PDB entries...")

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    entries = []
    for hit in data.get('entries', []):
        pdb_id = hit.get('id')
        if not pdb_id:
            log.warning("Missing PDB ID in entry, skipping", entry=hit)
            continue

        fields = hit.get('fields', {})
        pubmed_ids = fields.get('PUBMED', [])

        if pubmed_ids:
            entries.append({
                'pdb_id': pdb_id,
                'pubmed_id': pubmed_ids,
            })
        else:
            log.debug("No PubMed ID found for entry", pdb_id=pdb_id)

    with open("data/pdb_entries.json", "w") as f:
        json.dump(entries, f, indent=2)

    log.info("Saved entries with PubMed IDs", entry_count=len(entries))
    return entries
