# ResearchRAG document object storage

The upload API stores PDFs through a storage abstraction. The database
`documents.file_path` field now contains an **opaque object key** (for example,
`documents/<uuid>.pdf`) rather than a container-local absolute path.

## Local development

The default backend is local filesystem storage:

```env
STORAGE_BACKEND=local
LOCAL_STORAGE_DIR=data/objects
```

Docker Compose mounts the `/app/data` volume, so local object files survive
backend container replacement as long as the named volume is retained.

## Cloudflare R2

Create an R2 bucket and an API token with object read/write/delete permissions.
Configure these secrets in the backend hosting provider:

```env
APP_ENV=production
STORAGE_BACKEND=r2
R2_ENDPOINT_URL=https://<ACCOUNT_ID>.r2.cloudflarestorage.com
R2_BUCKET_NAME=<YOUR_BUCKET>
R2_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>
R2_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>
R2_REGION=auto
```

Use the account-specific endpoint and bucket credentials from Cloudflare.
Never commit real credentials or expose them through frontend `VITE_*`
variables. Production startup validation requires R2 and all four required
R2 settings.

Install dependencies and restart the backend after configuring the variables:

```powershell
python -m pip install -r requirements.txt
```

## Upload flow

1. The API streams the upload into a temporary file while enforcing the 25 MB limit.
2. The storage adapter writes it to local storage or R2 under a unique UUID key.
3. The indexing pipeline reads a temporary local copy of that object.
4. The document row stores the stable object key, not the temporary path.
5. The temporary copy is removed after indexing.

The storage adapter exposes upload, download, and delete operations. Document
deletion is not yet wired to an API endpoint, and existing document rows that
contain old local paths are not automatically migrated to object keys. Do not
switch an existing production dataset to R2 until those files have been copied
and their database records updated.
