🧬 PDB–EuropePMC Metadata Pipeline

This repository provides a data pipeline to fetch recent Protein Data Bank (PDB) entries from the last 5 years using the EBI API, and enrich those with publication metadata from Europe PMC. It also includes Jupyter notebooks for downstream analysis and visualization.

1. Create a Virtual Environment
We recommend using a virtual environment to avoid dependency conflicts.

```
python3 -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate
```

2. Install Dependencies

```
pip install -r requirements.txt
```

3.Run the Pipeline
This will:

Fetch PDB entries from the last 5 years with associated PubMed IDs
Fetch enriched metadata for those publications from Europe PMC
Save both to the data/ folder

```
python main.py
```

4. Analyze the Data
Use the Jupyter notebooks to perform various types of analysis:

```
jupyter notebook
```

Available notebooks:

- data_analysis.ipynb: Trend analysis, publication growth, PDB linkage over time

- trend_analysis.ipynb: Year-wise publication metrics

- funding_agencies.ipynb: Top grant agencies, co-funding patterns

- mesh_frequency.ipynb: Frequency of MeSH terms used
