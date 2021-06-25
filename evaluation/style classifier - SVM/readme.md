# Style classifier - SVM for handcrafted features and rules

## setup

**1. Download latest version of CoreNLP from above website (here 4.2.2)**

To extract certain text features, it is required to have the Stanford coreNLP files in this git repository under: `libraries/stanford-corenlp-4.2.2/`. These can be downloaded from [https://stanfordnlp.github.io/CoreNLP/](https://stanfordnlp.github.io/CoreNLP/). Version used: 4.2.2

**2. Start Stanford's coreNLP server**

Run following bash code from this folder or adjust the path to `libraries`.

```bash
java -mx4g -cp "../../libraries/stanford-corenlp-4.2.2/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -props corenlp.properties -quiet
```

**3. Download the SVM models & SHAP values**

from: https://drive.google.com/drive/folders/1yi0tDkHG4b_w_lTDl5t7G1feoSKsnp2F

**4. Running the SVM code**

**finally: Stopping server**

- on mac: find and kill -> `ps aux | grep StanfordCoreNLPServer` [details stackoverflow](https://stackoverflow.com/questions/55896197/an-elegant-way-to-shut-down-the-stanford-corenlp-server-on-macos)
- on windows: ctrl+c


**Further resources for coreNLP:**

- Running Stanford CoreNLP https://stanfordnlp.github.io/CoreNLP/index.html  
- Using nltk https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK