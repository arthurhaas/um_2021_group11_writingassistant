# GPT-2 Model 2

## Fine-tuning the model with new dataset - 
* Use the file FineTune_GPT_M2.ipynb with your dataset - the current implementation supports Line by Line Dataset and therefore the dataset format requires special tokens, you can read about the format  [on Huggingface](https://huggingface.co/transformers/model_doc/gpt2.html)

## Inference our fine-tuned GPT-2 model -
* Use the file Inference_GPT2_M2.ipynb - the script contains the downloadable link to the distributed model(the first cell will handle the model downloading). The input format for inference is: <BOS>Inchorent sentence<GENERATE_SCIENCE>.