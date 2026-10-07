# Reference verification, 2026-10-07

Every entry in `paper/refs.bib` checked against a primary listing. "Primary" means the publisher's or indexer's own record (ACM Digital Library via Crossref, ACL Anthology, Springer via Crossref, NIST, arXiv) or the cited web page itself. Page conventions: ACM TOIS articles are cited article-number style (20:1--20:38), which Crossref reports as 1--38; Foundations and Trends is cited by journal pagination (333--389), which Crossref reports by monograph pagination (1--174).

| Key | Checked against | Title / authors / venue / year | Pages |
|---|---|---|---|
| cormack2009rrf | Crossref 10.1145/1571941.1572114 | match | 758--759 match |
| thakur2021beir | arXiv 2104.08663 ("Accepted at NeurIPS 2021 Dataset and Benchmark Track") | match | none cited |
| bruch2023fusion | Crossref 10.1145/3596512; ACM DL (TOIS 42(1), article 20) | match; year 2024 | 20:1--20:35 (Crossref 1--35) |
| wadden2020scifact | ACL Anthology 2020.emnlp-main.609 | match | 7534--7550 match |
| boteva2016nfcorpus | Crossref 10.1007/978-3-319-30671-1_58 | match (Ghalandari surname corrected in round 1) | 716--722 match |
| robertson2009bm25 | Crossref 10.1561/1500000019; FnTIR 3(4) | match | 333--389 (journal pagination; Crossref 1--174) |
| nussbaum2024nomic | arXiv 2402.01613 | match | arXiv |
| xiao2023cpack | arXiv 2309.07597 (current title "C-Pack: Packed Resources For General Chinese Embeddings"); BAAI model card cites it for bge-*-en-v1.5 | match | arXiv |
| vangysel2018pytrec | Crossref 10.1145/3209978.3210065 | match | 873--876 match |
| macavaney2021irdatasets | Crossref 10.1145/3404835.3463254; arXiv 2103.02280 | match | 2429--2436 match |
| anthropic2024contextual | https://www.anthropic.com/engineering/contextual-retrieval (title "Introducing Contextual Retrieval", published 2024-09-19) | match; URL corrected from /news/ | web |
| sqlite_fts5 | https://www.sqlite.org/fts5.html, section 3 ("Phrases and NEAR groups may also be connected by implicit AND operators ... separated only by whitespace") and 4.3.1 (unicode61: non-alphanumeric characters are separators) | match | web |
| fox1994combination | NIST TREC-2 proceedings table of contents (p. 243; next paper p. 253) | match | 243--252 |
| lee1997analyses | ACM DL 10.1145/278459.258587; DBLP SIGIR 1997: 267--276 | match | 267--276 match |
| kamphuis2020bm25 | Crossref 10.1007/978-3-030-45442-5_4 | match | 28--34 match |
| webber2010rbo | Crossref 10.1145/1852102.1852106 (TOIS 28(4)) | match | 20:1--20:38 (Crossref 1--38) |
| montague2001normalization | Crossref 10.1145/502585.502657 | match | 427--433 match |
| luan2021sparse | ACL Anthology 2021.tacl-1.20 | match | 329--345 match |
| nogueira2019doc2query | arXiv 1904.08375 | match | arXiv |
| gao2021clear | Crossref 10.1007/978-3-030-72113-8_10 | match | 146--160 match |
| cronentownsend2002qpp | Crossref 10.1145/564376.564429 | match | 299--306 match |
| cooper1998monitoring | JASIS 49(10) record (Wiley DOI 10.1002/(SICI)1097-4571(199808)49:10<903::AID-ASI6>3.0.CO;2-F; ACM DL 10.5555/283678.283691) | match | 903--919 |

Removed in this pass: `gao2023hyde` (HyDE is query-side; the citation had been attached to a document-expansion sentence and was dropped in round 3; the entry was no longer cited).

Also checked for the claims that cite them: the bge-base-en-v1.5 model card prescribes `Represent this sentence for searching relevant passages:` on retrieval queries and nothing on passages; the nomic-embed-text-v1.5 card prescribes `search_document:` and `search_query:`; the Ollama `nomic-embed-text` model links to nomic-embed-text-v1.5; the transformers incompatibility (`NomicBertModel` has no `get_extended_attention_mask`) is with transformers 5.x.

Tools: `seek search` / `seek read` (Kagi-backed) for listings and pages; Crossref REST API by DOI for page ranges (`crossref_check.py`, polite UA, 1.5 s spacing). DBLP's API reset every connection after an initial burst and was not retried further.
