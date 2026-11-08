import numpy as np
import pandas as pd

from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding, Trainer, TrainingArguments

# Load dataset
dataset = pd.read_csv('client_servicing_sentiment_50000.csv')

label_encoder = LabelEncoder()
dataset['sentiment_encoded'] = label_encoder.fit_transform(
    dataset['sentiment']
)

X = dataset['client_message']
y = dataset['sentiment_encoded']

print(label_encoder.classes_)

# Reproduce the original train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    random_state=42,
    test_size=0.6,
    stratify=y
)

test_df = pd.DataFrame({
    "text": X_test,
    "label": y_test
})

test_dataset = Dataset.from_pandas(test_df.reset_index(drop=True))

# Load fine-tuned model and tokenizer
model_path = "./sentiment_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

model.eval()

# Tokenize test data
def tokenize(data):
    return tokenizer(
        data["text"],
        truncation=True,
        max_length=128
    )

test_dataset = test_dataset.map(
    tokenize,
    batched=True,
    remove_columns=["text"]
)

if "token_type_ids" in test_dataset.column_names:
    test_dataset = test_dataset.remove_columns(["token_type_ids"])

# Dynamic padding
data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    return_tensors="pt"
)

# Evaluation arguments
training_args = TrainingArguments(
    output_dir="./sentiment_evaluation",
    per_device_eval_batch_size=2,
    use_cpu=True,
    report_to="none"
)

# Create Trainer for prediction only
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    processing_class=tokenizer
)

# Generate predictions
prediction_output = trainer.predict(test_dataset)

predictions = np.argmax(
    prediction_output.predictions,
    axis=1
)

actual_labels = prediction_output.label_ids

# Evaluate
print("Accuracy:", accuracy_score(actual_labels, predictions))

print(
    classification_report(
        actual_labels,
        predictions,
        target_names=label_encoder.classes_
    )
)

print("Confusion Matrix:")
print(confusion_matrix(actual_labels, predictions))