# Model 2 - Style transfer

#evaluation/AutomaticEvaluation_corrected.ipynb:
jupyter notebook for comaprison of the three final models on style transfer and on Moverscore


#evaluation/MoverScoreBLEU_calculation.ipynb:
jupyter notebook used for calculation on Moverscore and BLEU on the sentence pairs produced by our final models
- For usage: MoverScore folder in public drive folder needed

#evaluation/data:
- evaluation_sample3000_corrected.xlsx: model input sentences (main test data)
- final_eval2_corrected.xlsx: model input sentences (test data for additional experiment)
- GPT2_phase3_combined_corrected.csv: final data of GPT model: input, output, RoBERTa labels, RoBERTa probabilities, SVM labels, Moverscore, BLEU, masked input, masked output
- T5_phase2_combined_corrected.csv: final data of T5 Phase2 model: input, output, RoBERTa labels, RoBERTa probabilities, SVM labels, Moverscore, BLEU, masked input, masked output
- T5_phase3_combined_corrected.csv : final data of T5 Phase3 model: input, output, RoBERTa labels, RoBERTa probabilities, SVM labels, Moverscore, BLEU, masked input, masked output
