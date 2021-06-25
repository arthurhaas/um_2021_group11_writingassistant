#%%
import os
import json
import random
import pandas as pd

# analysis of papers based on: https://arxiv.org/pdf/1804.09635.pdf
#%%
# Papers from: ICLR -> 255 rejected papers with optional scores

#
# gather metadata about arxiv papers
#
CONFERENCES = ["iclr_2017"]
FILE_SPLIT_CATEGORIES = "dev,test,train".split(",")
papers = {}

# load all three arxiv paper categories
for cat_id, category in enumerate(CONFERENCES):

    # load all three folders, i.e.: dev, train, test
    for split_id, file_split in enumerate(FILE_SPLIT_CATEGORIES):
        FOLDER_PATH = os.path.join("PeerRead", "data", category, file_split, "reviews")
        for f in os.listdir(FOLDER_PATH):
            filepath = os.path.join(FOLDER_PATH,f)
            if os.path.isfile(filepath) and f.endswith(".json"):
                
                with open(filepath, "r") as fp:
                    review = json.load(fp)
                    #papers[review['id']] = review
                    papers[review['id']] = {}
                    papers[review['id']]['accepted'] = review['accepted']
                    papers[review['id']]['reviews'] = {}
                    papers[review['id']]['reviews']['clarity'] = []
                    papers[review['id']]['reviews']['soundness_correctness'] = []
                    papers[review['id']]['reviews']['count'] = len(review['reviews'])
                    papers[review['id']]['cat'] = category
                    papers[review['id']]['split'] = file_split

                    for r in review['reviews']:
                        if "CLARITY" in r.keys():
                            papers[review['id']]['reviews']['clarity'].append(r['CLARITY'])
                        if "SOUNDNESS_CORRECTNESS" in r.keys():
                            papers[review['id']]['reviews']['soundness_correctness'].append(r['SOUNDNESS_CORRECTNESS'])



#%%


#
#
# TODO: No rejected papers have scores.!!!
#
#


stats = {}
for paper_id, meta in papers.items():
    print(f"{paper_id} - {meta['reviews']['soundness_correctness']} && {meta['reviews']['clarity']}")
    if bool(meta['reviews']['soundness_correctness']) & bool(meta['reviews']['clarity']):
        stats[paper_id] = meta







#%%
df_list = []
cols = "accepted,paper_id,reviews,clarity_count,clarity,sound_count,sound".split(",")
for paper_id, meta in stats.items():
    #print(f"{paper_id} - {meta['reviews']['soundness_correctness']} && {meta['reviews']['clarity']}")
    #print(f"{paper_id} - {meta['reviews']['count']} && clarity: {sum(meta['reviews']['clarity']) / len(meta['reviews']['clarity']):.1f} -- sound: {sum(meta['reviews']['soundness_correctness']) / len(meta['reviews']['soundness_correctness']):.1f}")
    df_list.append([
            meta["accepted"],
            int(paper_id),
            meta['reviews']['count'],
            len(meta['reviews']['clarity']),
            sum(meta['reviews']['clarity']) / len(meta['reviews']['clarity']),
            len(meta['reviews']['soundness_correctness']),
            sum(meta['reviews']['soundness_correctness']) / len(meta['reviews']['soundness_correctness'])]
        )

df = pd.DataFrame(data=df_list, columns=cols)


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



