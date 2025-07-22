"""
Fetching all the article metadata from the pdb ids,
Challenges faced:
- Missing authentication - a post request should generally have some Basic/token authentication.
- For the OR query to work we need to pass a unique set of pubmed ids - deduplication required
- the query clause need to be accurately formatted
- The maximum pagesize is 1000 and no pagination is present.
- Lots of defensive coding required with get(..)
"""

import requests
import json
from typing import List, Dict
import structlog

log = structlog.get_logger()

def fetch_articles_from_pubmed_ids(pub_ids: List[str]) -> List[Dict]:
    """
    Given a list of PubMed IDs, fetch metadata from Europe PMC via POST API.
    Saves results as JSON and returns parsed metadata.
    :param pub_ids: List of pubmed ids to fetch metadata for.
    :return: articles: the list of articles fetched from Europe PMC.
    """
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/searchPOST"

    # Build the query string with ext_id and src:med
    query_clauses = [f"(ext_id:{pmid} src:med)" for pmid in pub_ids]
    query = " OR ".join(query_clauses)

    payload = {
        "query": query,
        "resultType": "core",
        "synonym": True,
        "format": "json",
        "pageSize": 1000  # max allowed
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    log.info("Fetching articles from Europe PMC")

    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    articles = []
    for result in data.get("resultList", {}).get("result", []):
        affiliations = set()
        orcids = []
        author_list = result.get("authorList", {}).get("author", [])

        # ORCID if available
        for author in author_list:
            author_id = author.get("authorId")
            if author_id and author_id.get("type") == "ORCID":
                orcids.append(author_id.get("value"))

            # Affiliation(s)
            for aff in author.get("authorAffiliationDetailsList", {}).get("authorAffiliation", []):
                aff_text = aff.get("affiliation")
                if aff_text:
                    affiliations.add(aff_text)

        # --- MeSH Terms ---
        mesh_terms = [
            mh.get("descriptorName")
            for mh in result.get("meshHeadingList", {}).get("meshHeading", [])
            if mh.get("descriptorName")
        ]

        # --- Chemicals ---
        chemicals = [
            chem.get("name")
            for chem in result.get("chemicalList", {}).get("chemical", [])
            if chem.get("name")
        ]

        # --- Grants ---
        grants = [
            grant.get("agency")
            for grant in result.get("grantsList", {}).get("grant", [])
            if grant.get("agency")
        ]

        # --- Full Text URLs ---
        full_text_urls = [
            url.get("url")
            for url in result.get("fullTextUrlList", {}).get("fullTextUrl", [])
            if url.get("url")
        ]

        # --- PDB Linked ---
        pdb_linked = "PDB" in result.get("dbCrossReferenceList", {}).get("dbName", [])

        # --- Core Article Metadata ---
        journal_info = result.get("journalInfo", {}).get("journal", {})
        articles.append({
            "pubmed_id": result.get("id") or result.get("pmid"),
            "doi": result.get("doi"),
            "title": result.get("title"),
            "author_string": result.get("authorString"),
            "orcids": orcids,
            "affiliations": list(affiliations),
            "year": result.get("pubYear"),
            "journal_title": journal_info.get("title"),
            "journal_volume": result.get("journalInfo", {}).get("volume"),
            "journal_issue": result.get("journalInfo", {}).get("issue"),
            "page_info": result.get("pageInfo"),
            "abstract": result.get("abstractText"),
            "is_open_access": result.get("isOpenAccess") == "Y",
            "publication_status": result.get("publicationStatus"),
            "publication_model": result.get("pubModel"),
            "cited_by_count": result.get("citedByCount", 0),
            "mesh_terms": mesh_terms,
            "chemicals": chemicals,
            "grants": grants,
            "full_text_urls": full_text_urls,
            "pdb_linked": pdb_linked
        })

    with open("data/europepmc_articles.json", "w") as f:
        json.dump(articles, f, indent=2)

    log.info("Saved article metadata", article_count=len(articles))
    return articles
