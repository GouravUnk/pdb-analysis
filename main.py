import structlog
from typing import List
from src.fetch_pdb import fetch_recent_pdb_entries
from src.fetch_articles import fetch_articles_from_pubmed_ids

log = structlog.get_logger()

def main():
    """
    Orchestrates fetching recent PDB entries and enriching them with Europe PMC metadata.
    Steps:
    1. Fetch PDB entries with PubMed IDs (last 5 years)
    2. Extract PubMed IDs
    3. Fetch metadata from Europe PMC for those PubMed IDs
    4. Save both datasets as JSON files
    """
    log.info("Starting orchestration")

    # Step 1: Fetch recent PDB entries (with PubMed IDs)
    pdb_entries = fetch_recent_pdb_entries()
    log.info("Fetched PDB entries", count=len(pdb_entries))

    # Step 2: Extract PubMed IDs from PDB entries
    pubmed_ids: List[str] = [pmid for entry in pdb_entries if 'pubmed_id' in entry for pmid in entry['pubmed_id']]
    pubmed_ids = list(set(pubmed_ids))
    if not pubmed_ids:
        log.warning("No PubMed IDs found in fetched PDB entries. Exiting.")
        return

    # Step 3: Fetch Europe PMC metadata
    articles = fetch_articles_from_pubmed_ids(pubmed_ids)
    log.info("Fetched article metadata", article_count=len(articles))

    log.info("Data pipeline completed successfully")

if __name__ == "__main__":
    main()
