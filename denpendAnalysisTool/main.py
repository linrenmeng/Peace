import os
import torch
import logging
import numpy as np
import torch.nn as nn
from huggingface_hub import PyTorchModelHubMixin
from transformers import EncoderDecoderModel, RobertaTokenizerFast, PreTrainedModel
from torch.utils.data import DataLoader, TensorDataset


# ========== Logger Configuration ==========
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class DependencyAnalyzer(nn.Module, PyTorchModelHubMixin):
    def __init__(self, encoder: PreTrainedModel | None = None,
                 match_tokenizer: RobertaTokenizerFast | None = None):
        super(DependencyAnalyzer, self).__init__()
        
        self.encoder = encoder if encoder else self._load_encoder()
        self._configure_tokenizer(match_tokenizer)
        self.dense = nn.Linear(768, 2)

    def _load_encoder(self):
        """
        Loads the encoder model from a pretrained directory if not passed.
        
        Returns
        -------
        PreTrainedModel
            Encoder model.
        """
        logging.info("Loading encoder model...")
        encoder = EncoderDecoderModel.from_encoder_decoder_pretrained(
            "/data/junwan/repoexec/DenpendAnalysisTool", "/data/junwan/repoexec/DenpendAnalysisTool").encoder
        return encoder

    def _configure_tokenizer(self, match_tokenizer):
        """
        Configures the tokenizer for the encoder.
        
        Parameters
        ----------
        match_tokenizer : RobertaTokenizerFast
            The tokenizer to be used with the encoder model.
        """
        if match_tokenizer:
            self.encoder.resize_token_embeddings(len(match_tokenizer))
            self.encoder.config.decoder_start_token_id = match_tokenizer.cls_token_id
            self.encoder.config.pad_token_id = match_tokenizer.pad_token_id
            self.encoder.config.eos_token_id = match_tokenizer.sep_token_id
            self.encoder.config.vocab_size = match_tokenizer.vocab_size

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooler_output = outputs.pooler_output
        output_2d = self.dense(pooler_output)
        return output_2d


def load_model_and_tokenizer(model_dir, directly_load=True, model_with_structure_dir=None):
    """
    Loads the model and tokenizer from the specified directory.
    
    Parameters
    ----------
    model_dir : str
        The directory containing the model and tokenizer.
    directly_load : bool, optional
        Whether to directly load the model or from a structured directory, by default True.
    model_with_structure_dir : str, optional
        Directory with the model structure, by default None.

    Returns
    -------
    model : DependencyAnalyzer
        The loaded model.
    tokenizer : RobertaTokenizerFast
        The loaded tokenizer.
    """
    if directly_load:
        tokenizer = RobertaTokenizerFast.from_pretrained(model_dir, local_files_only=True)
        model = DependencyAnalyzer(match_tokenizer=tokenizer) if not model_with_structure_dir else \
            DependencyAnalyzer.from_pretrained(model_with_structure_dir, local_files_only=True)
        if not model_with_structure_dir:
            model.load_state_dict(torch.load(os.path.join(model_dir, 'pytorch_model.bin')))
        return model, tokenizer

    model = EncoderDecoderModel.from_pretrained(model_dir, local_files_only=True)
    model = model.encoder
    tokenizer = RobertaTokenizerFast.from_pretrained("/data/junwan/repoexec/DenpendAnalysisTool", local_files_only=True)
    special_tokens = ['<from>', '<to>']
    tokenizer.add_tokens(special_tokens, special_tokens=True)
    
    model = DependencyAnalyzer(model, tokenizer)
    return model, tokenizer


class DependencyClassifier:
    def __init__(self, load_dir, load_with_model_structure=False):
        """
        Initializes the DependencyClassifier with model and tokenizer loading.
        
        Parameters
        ----------
        load_dir : str
            Directory where the model and tokenizer are stored.
        load_with_model_structure : bool, optional
            Whether to load the model structure, by default False.
        """
        self.model, self.tokenizer = load_model_and_tokenizer(load_dir, model_with_structure_dir=load_dir) \
            if load_with_model_structure else load_model_and_tokenizer(load_dir)
        if torch.cuda.is_available():
            self.model.to(torch.device('cuda:1'))

    def construct_pair(self, code_1: str, code_2: str):
        """
        Constructs a token pair for model input.
        
        Parameters
        ----------
        code_1 : str
            The first code snippet.
        code_2 : str
            The second code snippet.

        Returns
        -------
        str
            The constructed pair.
        """
        return f"<from>{code_1}<to>{code_2}"

    def gen(self, text: str) -> float:
        """
        Generates the dependency score for a code pair.

        Parameters
        ----------
        text : str
            The input code pair.

        Returns
        -------
        float
            The dependency score.
        """
        sigmoid = nn.Sigmoid()
        token_input = self.tokenizer(text, return_tensors='pt')
        device = torch.device('cuda:1') if torch.cuda.is_available() else torch.device('cpu')
        token_input = token_input.to(device)

        with torch.no_grad():
            outputs = self.model(input_ids=token_input['input_ids'], attention_mask=token_input['attention_mask'])[0]
        outputs = sigmoid(outputs).detach().cpu()
        return outputs[1].item()

    def batch_gen(self, corpus_pair: list[str]) -> np.ndarray:
        """
        Processes multiple code pairs in a batch and returns dependency scores.
        
        Parameters
        ----------
        corpus_pair : list[str]
            A list of code pairs to analyze.

        Returns
        -------
        np.ndarray
            The dependency scores for each code pair.
        """
        sigmoid = nn.Sigmoid()
        device = torch.device('cuda:1') if torch.cuda.is_available() else torch.device('cpu')
        token_input = self.tokenizer(corpus_pair, return_tensors='pt', padding=True, truncation=True, max_length=512)
        dataset = TensorDataset(token_input["input_ids"], token_input["attention_mask"])
        dataloader = DataLoader(dataset, batch_size=32, shuffle=False)

        preds = []
        with torch.no_grad():
            for batch in dataloader:
                batch_input, attention_mask = [item.to(device) for item in batch]
                outputs = self.model(input_ids=batch_input, attention_mask=attention_mask)
                outputs = sigmoid(outputs)[:,1]
                preds.append(outputs.detach().cpu())

        preds = torch.cat(preds, dim=0)
        return preds.numpy()


# ========== Example Usage ==========
if __name__ == "__main__":
    model_dir = "/path/to/your/model"
    classifier = DependencyClassifier(model_dir)

    # Example code snippets for comparison
    code_1 = "def foo(): pass"
    code_2 = "def bar(): pass"

    score = classifier.gen(classifier.construct_pair(code_1, code_2))
    logging.info(f"Dependency score between the two code snippets: {score}")
    
    # Example of batch processing
    corpus = [("def foo(): pass", "def bar(): pass"), ("def add(a, b): return a + b", "def multiply(a, b): return a * b")]
    scores = classifier.batch_gen([classifier.construct_pair(code_1, code_2) for code_1, code_2 in corpus])
    logging.info(f"Dependency scores for the batch: {scores}")