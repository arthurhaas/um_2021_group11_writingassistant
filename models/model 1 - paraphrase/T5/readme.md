# T5 Model 1

## Fine-tuning the model with filtered PARANMT-50M dataset
* Use the file FineTune_T5_M1.ipynb to fine-tune the model with the [filtered PARANMT-50M](https://drive.google.com/drive/folders/1C7QbJizVeJ2xY8r4KeiDp369SKTYeKvL).
* The filtered PARANMT-50M dataset is a contribution from this paper. [[1]](#1).
* The fine-tuning notebook is a slightly modified versin of this work: [on T5 on TPU](https://colab.research.google.com/github/patil-suraj/exploring-T5/blob/master/T5_on_TPU.ipynb) 

## Inference the fine-tuned T5 model
* Use the file Inference_T5_M1.ipynb to load your fine-tuned model and generate your pseudo-parallel data.


## References
<a id="1">[1]</a> 
Krishna, Kalpesh and Wieting, John and Iyyer, Mohit" (2020). 
Reformulating Unsupervised Style Transfer as Paraphrase Generation. 
Association for Computational Linguistics, 737-762.
