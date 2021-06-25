#%%
import os
import json
import random

# analysis of papers based on: https://arxiv.org/pdf/1804.09635.pdf
#%%
# start with arxiv
# ~8900 rejected paper drafts, that can be of use for us

#
# gather metadata about arxiv papers
#
ARXIV_CATEGORIES = ["arxiv.cs.ai_2007-2017", "arxiv.cs.cl_2007-2017", "arxiv.cs.lg_2007-2017"]
FILE_SPLIT_CATEGORIES = "dev,test,train".split(",")
papers = {}

# load all three arxiv paper categories
for cat_id, arxiv_category in enumerate(ARXIV_CATEGORIES):

    # load all three folders, i.e.: dev, train, test
    for split_id, file_split in enumerate(FILE_SPLIT_CATEGORIES):
        FOLDER_PATH = os.path.join("PeerRead", "data", arxiv_category, file_split, "reviews")
        for f in os.listdir(FOLDER_PATH):
            filepath = os.path.join(FOLDER_PATH,f)
            if os.path.isfile(filepath) and f.endswith(".json"):
                
                with open(filepath, "r") as fp:
                    review = json.load(fp)
                    papers[review['id']] = {}
                    papers[review['id']]['accepted'] = review['accepted']
                    papers[review['id']]['cat'] = arxiv_category
                    papers[review['id']]['split'] = file_split

#%%
#
# ingest content of papers from rejected arxiv papers
#
abstracts = []
sections = []
counter = {}

for paper_id, metadata in papers.items():
    if metadata['accepted']:
        counter['accepted'] = counter.get('accepted', 0) + 1
            
    else:
        counter['rejected'] = counter.get('rejected', 0) + 1

        paper_file = os.path.join("PeerRead", "data", metadata['cat'], metadata['split'], "parsed_pdfs", f"{paper_id}.pdf.json")
        with open(paper_file, "r") as fp:
            content = json.load(fp)

            if content['metadata']['abstractText']:
                abstracts.append(content['metadata']['abstractText'])

            if content['metadata']['sections']:
                for section in content['metadata']['sections']:
                    sections.append(section['text'])


#
# export data
#
def clean_sections_off_of_surrogates(sections):
    """
    Quick-fix to avoid following error (appears ~80 times)
    UnicodeEncodeError: 'utf-8' codec can't encode character '\ud835' in position 9185999: surrogates not allowed
    """

    clean_sections = []
    print(f"# sections before cleaning: {len(sections)}.")
    for section in sections:
        try:
            a = section.encode("utf-8")
            clean_sections.append(section)
        except UnicodeEncodeError:
            pass

    print(f"# sections after cleaning: {len(clean_sections)}.")

    return clean_sections

EXPORT_PATH = os.path.join("processed", "arxiv")
with open(os.path.join(EXPORT_PATH, "abstracts.txt"), "w") as fp:
    fp.write("\n\n".join(abstracts))

clean_sections = clean_sections_off_of_surrogates(sections)
with open(os.path.join(EXPORT_PATH, "content_full.txt"), "w") as fp:
    fp.write("\n".join(clean_sections))

random.shuffle(clean_sections)
with open(os.path.join(EXPORT_PATH, "content.txt"), "w") as fp:
    fp.write("\n".join(clean_sections[:1000]))



