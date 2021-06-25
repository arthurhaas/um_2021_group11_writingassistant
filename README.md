# Writing Assistant
Repository for our master research project - Writing Assistant, 2021

## Team
We are students studying either Data Science for Decision Making or Artificial Intelligence at Maastricht University.
- [Antwan Meshrky](https://github.com/ameshrky)
- [Arthur Haas](https://github.com/arthurhaas)
- [Balázs Horváth](https://github.com/bghorvath)
- [Carsten Gieshoff](https://github.com/carstengieshoff)
- [Daniel Röder](https://github.com/DanielRoeder1)
- [Dhruv Rathi](https://github.com/dhruv2601)

## Deliverables

- Demo website: [http://writingassistant.ml](http://writingassistant.ml) (stable after 1. July)
- Public notebooks and datasets on [google drive](https://drive.google.com/drive/folders/1beJcEFLjkn1TSUXeHSoB2BZmx6cc6HZs)

## Folder structure

- **datasets:** Training datasets for models including its cleaning and preprocessing.
- **demo:** Code for our dash demo website within a google colab notebook.
- **evaluation:** Contains relevant models for evaluation including a grammar classifier, two style classifiers and the necessary datasets for these.
- **models:** Code and models for the model 1 (paraphrasing) and model 2 (style transfer).

## Details about our project

This Master Research Project dealt with the creation and evaluation of a natural language processing tool to improve the scientific style of sentences without changing their semantic content. In a first step we have fine-tuned GPT-2 and T5 pretrained models using a previously proven pseudo-parallel dataset of original and paraphrased sentences to generate pseudo parallel data by paraphrasing a heavily filtered set of scientific sentences. In this context we developed a new evaluation metric for diverse paraphrase generation. In a second step we fine-tuned GPT-2 and T5 models for style-transfer using filtered and cleaned sentences from the previously created pseudo-parallel data. We then evaluated the performance of these models based on classifiers that we developed in the scope of our research questions.

Our research goal was to find techniques for evaluating the performance of said scientific style transfer models. Because the scientificity of a sentence is manifold, we applied a combination of measures and models to validate the success of style transfer and the success of semantic preservation. For the evaluation of style transfer we used a RoBERTa classifier trained on sentences with TF-IDF masked tokens as well as an SVM model using handcrafted features. We found that this TF-IDF masking is necessary to ensure such classifiers do operate on style and not on content of the corpora they are trained on. For the semantic preservation we applied Moverscore and doing so critically discussed the applicability and the shortcomings of this novel metric. Moreover, we trained a classifier on the CoLA dataset to assess fluency of the output of our model. We also reviewed the performance of this classifier more critically than related work has done.

Finally, we find as a bottom line to our report, that our defined target group of users for whom this scientific style transfer model will be useful are students, as evaluation shows the most success in style transfer on student reports. However, our analysis also shows that the developed model is not yet sufficiently robust for reliable performance, as some sentences loose scientificity during transfer (especially already scientific ones) and as human evaluation did not achieve the desired results.

