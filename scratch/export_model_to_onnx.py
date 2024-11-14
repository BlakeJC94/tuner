from sentence_transformers import (
    SentenceTransformer,
    export_optimized_onnx_model,
)
model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    backend="onnx",
    model_kwargs={"file_name": "model.onnx"},
)
export_optimized_onnx_model(model, "O1", "./foo")


# %%
from transformers import AutoTokenizer, AutoModel, AutoConfig, PreTrainedTokenizerFast
import torch
import torch.nn.functional as F

model_path = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer =  AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v1')

sentences = ["Industrial Metal"]

inputs = tokenizer(
    sentences,
    padding=True,
    truncation=True,
    return_tensors="pt"
)

def mean_pooling(model_output, attention_mask):
    attention_mask = torch.tensor(attention_mask)
    token_embeddings = torch.tensor(model_output[0])  #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

with torch.no_grad():
    model_outputs = model(**inputs)

sentence_embeddings = mean_pooling(model_outputs, inputs["attention_mask"])
sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

# %%
import onnx
import onnxruntime as ort

from transformers.onnx import export

config = AutoConfig.from_pretrained('sentence-transformers/all-MiniLM-L6-v1')

onnx_inputs, onnx_outputs = export(
    tokenizer,
    model,
    onnx_config,
    onnx_config.default_onnx_opset,
    "./bar",
)

onnx_path = "./foo/onnx/model_O1.onnx"
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)
ort_sess = ort.InferenceSession(onnx_path)

inputs = tokenizer(
    sentences,
    padding=True,
    truncation=True,
    return_tensors="np"
)
inputs = {k: v for k, v in inputs.items()}

def mean_pooling(model_output, attention_mask):
    attention_mask = torch.tensor(attention_mask)
    token_embeddings = torch.tensor(model_output[0])  #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

onnx_outputs = ort_sess.run(None, inputs)

onnx_sentence_embeddings = mean_pooling(onnx_outputs, inputs["attention_mask"])
onnx_sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

# %%
model_outputs = model.encode("Industrial Metal")


# %%# Load model directly
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v1")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v1")

inputs = tokenizer(
    "Industrial Metal",
    padding="max_length",
    max_length=512,
    return_tensors="np"
)
inputs = {k: v for k, v in inputs.items()}
outputs = model(inputs)




# %%

sentences = ["Industrial Metal"]


# %%
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

model_checkpoint = "sentence-transformers/all-MiniLM-L6-v1"
save_directory = "foo/"

# Load a model from transformers and export it to ONNX
ort_model = ORTModelForFeatureExtraction.from_pretrained(model_checkpoint, export=True)
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

# Save the onnx model and tokenizer
ort_model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

# %%
onnx_tokenizer = AutoTokenizer.from_pretrained("./foo")
onnx_model = ORTModelForFeatureExtraction.from_pretrained("./foo")

onnx_inputs = tokenizer(
    sentences,
    return_tensors="pt",
    padding=True,
    truncation=True,
)
with torch.no_grad():
    onnx_outputs = model(**inputs)

onnx_embeddings = onnx_outputs["pooler_output"]


# %%
from transformers import AutoTokenizer, AutoModel, AutoConfig, PreTrainedTokenizerFast
import torch
import torch.nn.functional as F

model_path = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer =  AutoTokenizer.from_pretrained(model_path)
model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v1')

inputs = tokenizer(
    sentences,
    padding=True,
    truncation=True,
    return_tensors="pt"
)

def mean_pooling(model_output, attention_mask):
    attention_mask = torch.tensor(attention_mask)
    token_embeddings = torch.tensor(model_output[0])  #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

with torch.no_grad():
    model_outputs = model(**inputs)

embeddings = mean_pooling(model_outputs, inputs["attention_mask"])
embeddings = F.normalize(embeddings, p=2, dim=1)
