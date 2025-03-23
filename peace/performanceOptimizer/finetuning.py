from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, DataCollatorForSeq2Seq, TrainingArguments, Trainer
from peft import LoraConfig, TaskType, get_peft_model

# Step 1: Import necessary packages
# These libraries are used for loading datasets, tokenization, model training, and fine-tuning with LoRA.

# Step 2: Load dataset
# Load dataset from a local path, expected to contain code snippets and responses.
ds = Dataset.load_from_disk("./data/dataset.json")
print(ds[:3])  # Display the first 3 entries to verify.

# Step 3: Preprocess dataset
# Tokenize the data into the format required for training. The prompt and response are formatted accordingly.
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B-hf")

def process_func(example):
    MAX_LENGTH = 256  # Set maximum sequence length.
    
    # Format the prompt for the task.
    prompt = f"Below are several versions of a codesnippet. You should analyze each version to determine their performance in terms of execution speed. time efficiency.\nThe task is to create the most efficient version and suboptimal version of the code in terms of execution.\n### code snippet:\n{example['code1']} {example['code2']} ...\n### efficient version: {example['fast_code']}\n#艺# suboptimal version: {example['slow_code']}"
    
    # Tokenize the input prompt and response (output).
    instruction = tokenizer(prompt.strip() + "\n\nAssistant: ")
    response = tokenizer(example['response'] + tokenizer.eos_token)
    
    input_ids = instruction["input_ids"] + response["input_ids"]
    attention_mask = instruction["attention_mask"] + response["attention_mask"]
    labels = [-100] * len(instruction["input_ids"]) + response["input_ids"]
    
    # Ensure the tokenized sequence does not exceed the maximum length.
    if len(input_ids) > MAX_LENGTH:
        input_ids = input_ids[:MAX_LENGTH]
        attention_mask = attention_mask[:MAX_LENGTH]
        labels = labels[:MAX_LENGTH]
        
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }

# Apply preprocessing to dataset
tokenized_ds = ds.map(process_func, remove_columns=ds.column_names)
print(tokenized_ds[:3])  # Verify the tokenized dataset.

# Step 4: Initialize LLaMA 8B model
# Load the pre-trained LLaMA 8B model from Hugging Face (Meta's LLaMA 8B).
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B-hf")

# Step 5: Configure LoRA for fine-tuning
# LoRA is set up to modify specific layers of the model, enabling efficient fine-tuning.
config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    target_modules=".*\.query_key_value",  # Target modules for LoRA modification
    modules_to_save=["word_embeddings"]  # Specify which modules to save
)

# Apply LoRA to the model
model = get_peft_model(model, config)

# Step 6: Set up training arguments
# Define hyperparameters for the training process, such as batch size and number of epochs.
args = TrainingArguments(
    output_dir="./data/model",  # Save model checkpoints here.
    per_device_train_batch_size=4,
    gradient_accumulation_steps=16,
    logging_steps=20,
    num_train_epochs=4
)

# Step 7: Create Trainer for model training
# Use Hugging Face's Trainer API to handle the training loop.
trainer = Trainer(
    model=model,
    args=args,
    tokenizer=tokenizer,
    train_dataset=tokenized_ds,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True)
)

# Step 8: Train the model
# Begin training the model with the prepared dataset.
trainer.train()

# Step 9: Model inference
# After training, use the model for inference by passing a prompt and generating the response.
model = model.cuda()  # Move the model to GPU for faster inference.
ipt = tokenizer("Below are several versions of a codesnippet. You should analyze each version to determine their performance in terms of execution speed. time efficiency.\nThe task is to create the most efficient version of the code in terms of execution.\n### code snippet:\n考试有哪些技巧？\n### efficient version:", return_tensors="pt").to(model.device)
print(tokenizer.decode(model.generate(**ipt, max_length=128, do_sample=True)[0], skip_special_tokens=True))
