# SBNLPpt

### Author

Richard Bruce Baxter - Copyright (c) 2022-2023 Baxter AI (baxterai.com)

### Description

Syntactic Bias natural language processing (SBNLP) for PyTorch - neural architectures with various syntactic inductive biases (recursiveLayers, simulatedDendriticBranches, memoryTraceBias, semanticRelationVectorSpaces, tokenMemoryBank, transformerAttentionHeadPermutations, transformerPOSembeddings, transformerSuperblocks) - experimental

### License

MIT License

### Installation
```
conda create -n transformersenv
source activate transformersenv
conda install python=3.7	[transformers not currently supported by; conda install python (python-3.10.6)]
pip install datasets
pip install transfomers==4.23.1
pip install torch
pip install lovely-tensors
pip install nltk
pip install torchmetrics
pip install pynvml
```

### Execution
```
source activate transformersenv
python SBNLPpt_main.py
```

## recursiveLayers

![recursiveLayers1a.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/archive/recursiveLayersOrigImplementation/recursiveLayers1a.drawio.png?raw=true)
- [recursiveLayers1b.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/recursiveLayers1b.drawio.png?raw=true)

### ROBERTApt (Masked LM)

#### positionEmbeddingType relative

![RobertaRecursiveTransformer.png](https://github.com/bairesearch/TSBpt/blob/master/graph/RobertaRecursiveTransformer.png?raw=true)
- [RobertaRecursiveTransformerHeads.png](https://github.com/bairesearch/TSBpt/blob/master/graph/RobertaRecursiveTransformerHeads.png?raw=true)

#### positionEmbeddingType absolute

![RobertaRecursiveTransformer-Nov2022.png](https://github.com/bairesearch/TSBpt/blob/master/graph/archive/positionEmbeddingTypeAbsolute-Nov2022/RobertaRecursiveTransformer-Nov2022.png?raw=true)
- [RobertaRecursiveTransformerLayers-Nov2022.png](https://github.com/bairesearch/TSBpt/blob/master/graph/archive/positionEmbeddingTypeAbsolute-Nov2022/RobertaRecursiveTransformerLayers-Nov2022.png?raw=true)

### GPT2pt (Causal LM)

![GPT2RecursiveTransformer.png](https://github.com/bairesearch/TSBpt/blob/master/graph/GPT2RecursiveTransformer.png?raw=true)
- [GPT2RecursiveTransformer-loss.png](https://github.com/bairesearch/TSBpt/blob/master/graph/GPT2RecursiveTransformer-loss.png?raw=true)

## transformerSuperblocks

#### recursiveLayers
![recursiveLayers1b.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/recursiveLayers1b.drawio.png?raw=true)
![transformerSuperblocks1b.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/transformerSuperblocks1b.drawio.png?raw=true)

#### recursiveLayersOrigImplementation
- [recursiveLayers1a.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/archive/recursiveLayersOrigImplementation/recursiveLayers1a.drawio.png?raw=true)
- [transformerSuperblocks1a.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/archive/recursiveLayersOrigImplementation/transformerSuperblocks1a.drawio.png?raw=true)

## tokenMemoryBank

![tokenMemoryBank1a.drawio.png](https://github.com/bairesearch/TSBpt/blob/master/graph/tokenMemoryBank1a.drawio.png?raw=true)


