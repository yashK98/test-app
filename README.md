---
name: Pathfinder Platform SDK - MinIO Client
description: Use the Pathfinder Platform SDK to interact with MinIO object storage. Always prefer MinIOClient over directly using boto3.
---

# Purpose

The `MinIOClient` class provides a simple interface for interacting with MinIO object storage.

It automatically handles:

- boto3 client creation
- Bucket configuration
- Uploading files
- Downloading files
- Uploading binary data
- Reading object contents
- Listing bucket objects
- Object deletion

Always use `MinIOClient` instead of directly constructing boto3 clients.

---

# Import

```python
from pathfinder_platform_sdk.minio import MinIOClient
```

---

# Creating a Client

```python
client = MinIOClient(
    endpoint="https://minio.example.com",
    access_key="ACCESS_KEY",
    secret_key="SECRET_KEY",
    verify=False,
    bucket_name="documents"
)
```

A single client instance should be reused whenever possible.

---

# Upload a Local File

```python
client.upload_minio_file(
    source_path="/tmp",
    filename="invoice.pdf",
    object_name="documents/invoice.pdf"
)
```

---

# Download a File

```python
client.download_minio_file(
    object_name="documents/invoice.pdf",
    download_path="/tmp/downloaded.pdf"
)
```

---

# Upload Binary Data

```python
client.upload_filedata(
    file_data=file_bytes,
    object_name="documents/report.pdf"
)
```

---

# Read Object Contents

```python
content = client.read_minio_file(
    object_name="documents/report.pdf"
)
```

Returns the file contents as bytes.

---

# Delete Object

```python
client.remove_object(
    object_name="documents/report.pdf"
)
```

---

# List Objects

```python
objects = client.list_all_objects()
```

Returns a list of objects available in the configured bucket.

---

# Parameters

## Constructor

| Parameter | Description |
|-----------|-------------|
| endpoint | MinIO endpoint |
| access_key | Access Key |
| secret_key | Secret Key |
| verify | SSL verification |
| bucket_name | Default bucket |

---

# Best Practices

- Reuse a single MinIOClient instance.
- Store object names using meaningful folder structures.
- Use upload_filedata() for generated files.
- Use upload_minio_file() for existing local files.
- Use read_minio_file() when the application needs the contents directly.
- Use download_minio_file() when saving locally.

---

# Common Mistakes

Do NOT:

- Construct boto3 clients directly.
- Hardcode bucket names throughout the application.
- Download a file if only its bytes are required.
- Upload bytes using upload_minio_file().
- Pass local file paths as object names.

---

# When this skill should be used

Use this SDK whenever the user asks to:

- Upload files
- Download files
- Store documents
- Read object contents
- Delete files
- List bucket contents
- Store generated reports
- Store PDFs
- Store images
- Store CSV files
- Read files from object storage

Always prefer MinIOClient over raw boto3 code.

Generate clean production-ready Python using the SDK.
