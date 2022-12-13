# -*- coding: utf-8 -*-
"""makemore SANIwavenet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14J-qGRGFVkyp6EvsFpL6hbA1mOKWagQM

## makemore SANI wavenet

Based on "makemore: part 5 (building a WaveNet)":

https://colab.research.google.com/drive/1CXVEmCO_7r7WYZGb5qnjfyxTvQa13g5X
"""

#License: MIT

# Commented out IPython magic to ensure Python compatibility.
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt # for making figures
# %matplotlib inline

#algorithm selection:
algorithmSANIoverloaded = True    #Structure type #2  #pregenerated SANI with wordIndexOverlap
algorithmSANIwavenet = False    #Structure type #4  #4a recursiveLayers issue: neurons will not have access to slightly offsetted subnet information
algorithmWavenet = False    #orig   #Structure type #3 

recursiveLayers = True

printVerbose = False

if(algorithmSANIwavenet):
    layerIndex = 0  #global var as cannot call Sequential layers with optional parameters

n_embd = 24 # the dimensionality of the character embedding vectors
n_hidden = 128 # the number of neurons in the hidden layer of the MLP

block_size = 8 # context length: how many characters do we take to predict the next one?

batch_size = 32

# download the names.txt file from github
!wget https://raw.githubusercontent.com/karpathy/makemore/master/names.txt

# read in all the words
words = open('names.txt', 'r').read().splitlines()
print(len(words))
print(max(len(w) for w in words))
print(words[:8])

# build the vocabulary of characters and mappings to/from integers
chars = sorted(list(set(''.join(words))))
stoi = {s:i+1 for i,s in enumerate(chars)}
stoi['.'] = 0
itos = {i:s for s,i in stoi.items()}
vocab_size = len(itos)
print(itos)
print(vocab_size)

# shuffle up the words
import random
random.seed(42)
random.shuffle(words)

# build the dataset

def build_dataset(words):  
  X, Y = [], []
  
  for w in words:
    context = [0] * block_size
    for ch in w + '.':
      ix = stoi[ch]
      X.append(context)
      Y.append(ix)
      context = context[1:] + [ix] # crop and append

  X = torch.tensor(X)
  Y = torch.tensor(Y)
  print(X.shape, Y.shape)
  return X, Y

n1 = int(0.8*len(words))
n2 = int(0.9*len(words))
Xtr,  Ytr  = build_dataset(words[:n1])     # 80%
Xdev, Ydev = build_dataset(words[n1:n2])   # 10%
Xte,  Yte  = build_dataset(words[n2:])     # 10%

for x,y in zip(Xtr[:20], Ytr[:20]):
  print(''.join(itos[ix.item()] for ix in x), '-->', itos[y.item()])

# Near copy paste of the layers we have developed in Part 3

# -----------------------------------------------------------------------------------------------
class Linear:
  
  def __init__(self, fan_in, fan_out, bias=True):
    self.weight = torch.randn((fan_in, fan_out)) / fan_in**0.5 # note: kaiming init
    self.bias = torch.zeros(fan_out) if bias else None
  
  def __call__(self, x):
    self.out = x @ self.weight
    if self.bias is not None:
      self.out += self.bias
    return self.out
  
  def parameters(self):
    return [self.weight] + ([] if self.bias is None else [self.bias])

# -----------------------------------------------------------------------------------------------
class BatchNorm1d:
  
  def __init__(self, dim, eps=1e-5, momentum=0.1):
    self.eps = eps
    self.momentum = momentum
    self.training = True
    # parameters (trained with backprop)
    self.gamma = torch.ones(dim)
    self.beta = torch.zeros(dim)
    # buffers (trained with a running 'momentum update')
    self.running_mean = torch.zeros(dim)
    self.running_var = torch.ones(dim)
  
  def __call__(self, x):
    # calculate the forward pass
    if self.training:
      if x.ndim == 2:
        dim = 0
      elif x.ndim == 3:
        dim = (0,1)
      xmean = x.mean(dim, keepdim=True) # batch mean
      xvar = x.var(dim, keepdim=True) # batch variance
    else:
      xmean = self.running_mean
      xvar = self.running_var
    xhat = (x - xmean) / torch.sqrt(xvar + self.eps) # normalize to unit variance
    self.out = self.gamma * xhat + self.beta
    # update the buffers
    if self.training:
      with torch.no_grad():
        self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * xmean
        self.running_var = (1 - self.momentum) * self.running_var + self.momentum * xvar
    return self.out
  
  def parameters(self):
    return [self.gamma, self.beta]

# -----------------------------------------------------------------------------------------------
class Tanh:
  def __call__(self, x):
    self.out = torch.tanh(x)
    return self.out
  def parameters(self):
    return []

# -----------------------------------------------------------------------------------------------
class Embedding:
  
  def __init__(self, num_embeddings, embedding_dim):
    self.weight = torch.randn((num_embeddings, embedding_dim))
    
  def __call__(self, IX):
    self.out = self.weight[IX]
    return self.out
  
  def parameters(self):
    return [self.weight]

def interweaveTensors(xOffsetList, dim):    
    #dim = dimension to interweave into
    #https://stackoverflow.com/questions/60869537/how-can-i-interleave-5-pytorch-tensors
    stacked = torch.stack(xOffsetList, dim=dim+1)   #inserts new temporary dimension at dim+1
    #print("stacked.shape  = ", stacked.shape)
    x = torch.flatten(stacked, start_dim=dim, end_dim=dim+1)
    return x

class takeLastSequentialToken:
  def __init__(self):
      pass
  def __call__(self, x):    #, layerIndex=None
    B, T, C = x.shape
    if(printVerbose):
        print("B = ", B)
        print("T = ", T)
        print("C = ", C)

    takeLast = False
    if(algorithmSANIoverloaded):
        takeLast = True
    elif(algorithmSANIwavenet):
        if(recursiveLayers):
            takeLast = False 
        else:
            takeLast = True
    if(takeLast):
        x = x[:, -1, :]  #take last sequential token in layer
    else:
        #takeAverage of all final layer token values    #CHECKTHIS
        x = torch.mean(x, dim=1)

    self.out = x
    return self.out
  
  def parameters(self):
    return []

class FlattenConsecutive:
  
  def __init__(self, n):
    self.n = n
    
  def __call__(self, x):    #, layerIndex=None
    B, T, C = x.shape

	#B = batchSize (eg 32)
	#T = number of characters (eg 8)     #token dimension
	#C = number of vector dimensions (eg 128)
    if(printVerbose):
        print("B = ", B)
        print("T = ", T)
        print("C = ", C)

    if(algorithmSANIoverloaded):
        #Structure type 2
        xi1 = x[:, 0:-1, :]
        xi2 = x[:, 1:, :]
        xiPadding = torch.zeros((B, 1, C)) #CHECKTHIS: currently pad first (or last) section in sequence with zeros 
        xi1 = torch.concat((xiPadding, xi1), dim=1)   #concat along T dimension
        xi2 = torch.concat((xiPadding, xi2), dim=1)   #concat along T dimension
        x = torch.concat((xi1, xi2), dim=2)   #cat along C dimension
    elif(algorithmSANIwavenet):
        #Structure type 4
        global layerIndex
        if(recursiveLayers):
            #Structure type 4a
            numberOfOffsets = 2
            offsetIncrement = layerIndex*2   #CHECKTHIS: add -1 (makes odd value; computation more complicated)
            maxOffset = offsetIncrement
        else:
            #Structure type 4b
            numberOfOffsets = 2**layerIndex   #CHECKTHIS: add -1 (makes odd value; computation more complicated)
            offsetIncrement = 1
            maxOffset = numberOfOffsets
        if(printVerbose):
            print("\nlayerIndex = ", layerIndex)
            print("\tnumberOfOffsets = ", numberOfOffsets)
            print("\toffsetIncrement = ", offsetIncrement)
            print("\tmaxOffset = ", maxOffset)

        xOffsetList = []
        for offsetIndex in range(numberOfOffsets):
            offset = offsetIndex*offsetIncrement
            if(offsetIndex == 0):
                xi = x  #use all tokens in sequence
            else:
                xi = x[:, 0:-offset, :]
                xiPadding = torch.zeros((B, offset, C))
                xi = torch.concat((xiPadding, xi), dim=1)   #concat along T dimension
            xOffsetList.append(xi)
        xOffsetList.reverse()
        x = interweaveTensors(xOffsetList, 2)
        
        layerIndex = layerIndex+1
    elif(algorithmWavenet):
        #Structure type 3
        x = x.view(B, T//self.n, C*self.n)

    if x.shape[1] == 1:
      x = x.squeeze(1)
    self.out = x
    return self.out
  
  def parameters(self):
    return []

# -----------------------------------------------------------------------------------------------
class Sequential:
  
  def __init__(self, layers):
    self.layers = layers
  
  def __call__(self, x):
    if(algorithmSANIwavenet):
        global layerIndex
        layerIndex = 1
    for layer in self.layers:
      x = layer(x)
    self.out = x
    return self.out
  
  def parameters(self):
    # get parameters of all layers and stretch them out into one list
    return [p for layer in self.layers for p in layer.parameters()]

torch.manual_seed(42); # seed rng for reproducibility

# original network
# n_embd = 10 # the dimensionality of the character embedding vectors
# n_hidden = 300 # the number of neurons in the hidden layer of the MLP
# model = Sequential([
#   Embedding(vocab_size, n_embd),
#   FlattenConsecutive(block_size), Linear(n_embd * block_size, n_hidden, bias=False), BatchNorm1d(n_hidden), Tanh(),
#   Linear(n_hidden, vocab_size),
# ])

# hierarchical network

def createSANIlayerRecursive(recursiveLayer, n_hidden, layerInputMuliplier):
    if(recursiveLayers):
        layer = recursiveLayer
    else:
        layer = createSANIlayer(n_hidden, layerInputMuliplier)
    return layer

def createSANIlayer(n_hidden, layerInputMuliplier):
    layer = Linear(n_hidden*layerInputMuliplier, n_hidden, bias=False)
    return layer

if(recursiveLayers):
    recursiveLayer = createSANIlayer(n_hidden, 2)
else:
    recursiveLayer = None

if(algorithmSANIoverloaded):
    #number of SANI layers must equal T (number of tokens in sequence; block_size)    #FUTURE: make dynamic
    model = Sequential([
    Embedding(vocab_size, n_embd),
    Linear(n_embd, n_hidden, bias=False),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    takeLastSequentialToken(),
    Linear(n_hidden, vocab_size),
    ])
elif(algorithmSANIwavenet):
    #2^number of SANI layers must equal T (number of tokens in sequence; block_size)    #FUTURE: make dynamic
    model = Sequential([
    Embedding(vocab_size, n_embd),
    Linear(n_embd, n_hidden, bias=False),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 4), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 8), BatchNorm1d(n_hidden), Tanh(),
    takeLastSequentialToken(),
    Linear(n_hidden, vocab_size),
    ])
elif(algorithmWavenet):
    model = Sequential([
    Embedding(vocab_size, n_embd),
    #FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_embd, 2), BatchNorm1d(n_hidden), Tanh(), #orig: no support for recursiveLayers
    Linear(n_embd, n_hidden, bias=False),   #new: add support for recursiveLayers
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),    #new: add support for recursiveLayers
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    FlattenConsecutive(2), createSANIlayerRecursive(recursiveLayer, n_hidden, 2), BatchNorm1d(n_hidden), Tanh(),
    Linear(n_hidden, vocab_size),
    ])

# parameter init
with torch.no_grad():
  model.layers[-1].weight *= 0.1 # last layer make less confident

parameters = model.parameters()
print(sum(p.nelement() for p in parameters)) # number of parameters in total
for p in parameters:
  p.requires_grad = True

#print layer sizes;
#for layer in model.layers:
#    print(layer.__class__.__name__, ':', tuple(layer.out.shape))

# same optimization as last time
max_steps = 200000
lossi = []

for i in range(max_steps):
  
  # minibatch construct
  ix = torch.randint(0, Xtr.shape[0], (batch_size,))
  Xb, Yb = Xtr[ix], Ytr[ix] # batch X,Y
  
  # forward pass
  logits = model(Xb)
  #print("logits.shape = ", logits.shape)
  #print("Yb.shape = ", Yb.shape)
  loss = F.cross_entropy(logits, Yb) # loss function
  
  # backward pass
  for p in parameters:
    p.grad = None
  loss.backward()
  
  # update: simple SGD
  lr = 0.1 if i < 150000 else 0.01 # step learning rate decay
  for p in parameters:
    p.data += -lr * p.grad

  # track stats
  if i % 10000 == 0: # print every once in a while
    print(f'{i:7d}/{max_steps:7d}: {loss.item():.4f}')
  lossi.append(loss.log10().item())

plt.plot(torch.tensor(lossi).view(-1, 1000).mean(1))

# put layers into eval mode (needed for batchnorm especially)
for layer in model.layers:
  layer.training = False

# evaluate the loss
@torch.no_grad() # this decorator disables gradient tracking inside pytorch
def split_loss(split):
  x,y = {
    'train': (Xtr, Ytr),
    'val': (Xdev, Ydev),
    'test': (Xte, Yte),
  }[split]
  logits = model(x)
  loss = F.cross_entropy(logits, y)
  print(split, loss.item())

split_loss('train')
split_loss('val')

"""### performance log

- original (3 character context + 200 hidden neurons, 12K params): train 2.058, val 2.105
- context: 3 -> 8 (22K params): train 1.918, val 2.027
- flat -> hierarchical (22K params): train 1.941, val 2.029
- fix bug in batchnorm: train 1.912, val 2.022
- scale up the network: n_embd 24, n_hidden 128 (76K params): train 1.769, val 1.993

"""

# sample from the model
for _ in range(20):
    
    out = []
    context = [0] * block_size # initialize with all ...
    while True:
      # forward pass the neural net
      logits = model(torch.tensor([context]))
      probs = F.softmax(logits, dim=1)
      # sample from the distribution
      ix = torch.multinomial(probs, num_samples=1).item()
      # shift the context window and track the samples
      context = context[1:] + [ix]
      out.append(ix)
      # if we sample the special '.' token, break
      if ix == 0:
        break
    
    print(''.join(itos[i] for i in out)) # decode and print the generated word

"""### Next time:
Why convolutions? Brief preview/hint
"""

for x,y in zip(Xtr[7:15], Ytr[7:15]):
  print(''.join(itos[ix.item()] for ix in x), '-->', itos[y.item()])

# forward a single example:
logits = model(Xtr[[7]])
logits.shape

# forward all of them
logits = torch.zeros(8, 27)
for i in range(8):
  logits[i] = model(Xtr[[7+i]])
logits.shape

# convolution is a "for loop"
# allows us to forward Linear layers efficiently over space