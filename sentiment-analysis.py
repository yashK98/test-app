import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import DataCollatorWithPadding
from transformers import Trainer, TrainingArguments

dataset = pd.read_csv('client_servicing_sentiment_50000.csv')

label_encoder = LabelEncoder()
dataset['sentiment_encoded'] = label_encoder.fit_transform(dataset['sentiment'])

X = dataset['client_message']
y = dataset['sentiment_encoded']

print(label_encoder.classes_)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.6, stratify=y)

train_df = pd.DataFrame({
    "text": X_train,
    "label": y_train
})

test_df = pd.DataFrame({
    "text": X_test,
    "label": y_test
})

train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
test_dataset = Dataset.from_pandas(test_df.reset_index(drop=True))

model_name = './distilbert'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=4)

def tokenize(data):
    return tokenizer(
        data["text"],
        truncation=True,
        max_length=128
    )

train_dataset = train_dataset.map(
    tokenize,
    batched=True,
    remove_columns=["text"]
)

test_dataset = test_dataset.map(
    tokenize,
    batched=True,
    remove_columns=["text"]
)

train_dataset = train_dataset.remove_columns(["token_type_ids"])
test_dataset = test_dataset.remove_columns(["token_type_ids"])

data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    return_tensors="pt"
)

training_args = TrainingArguments(
    output_dir="./sentiment_output",
    num_train_epochs=2,
    per_device_train_batch_size=2,
    learning_rate=2e-5,
    use_cpu=True,
    eval_strategy="no",
    save_strategy="epoch",
    logging_steps=100,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=data_collator,
    processing_class=tokenizer
)

trainer.train(resume_from_checkpoint=True)

trainer.save_model("./sentiment_model")
tokenizer.save_pretrained("./sentiment_model")