import { useRef, useState } from "react";

import {
    Upload,
    FileText,
    X,
    CheckCircle,
    AlertCircle,
} from "lucide-react";

import { uploadDocument } from "../api/upload";

function DocumentUploader({ onUploaded }) {
    const inputRef = useRef(null);

    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [dragging, setDragging] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    function validateFile(selected) {
        if (!selected) return false;

        if (
            selected.type !== "application/pdf" &&
            !selected.name.toLowerCase().endsWith(".pdf")
        ) {
            setError("Only PDF files are supported.");
            return false;
        }

        if (selected.size > 25 * 1024 * 1024) {
            setError("Maximum supported file size is 25 MB.");
            return false;
        }

        setError("");
        setSuccess("");
        setFile(selected);

        return true;
    }

    function handleFileChange(event) {
        validateFile(event.target.files?.[0]);
    }

    function handleDrop(event) {
        event.preventDefault();
        setDragging(false);

        if (uploading) return;

        validateFile(event.dataTransfer.files?.[0]);
    }

    async function handleUpload() {
        if (!file || uploading) return;

        try {
            setUploading(true);
            setProgress(0);
            setError("");
            setSuccess("");

            await uploadDocument(file, setProgress);

            setSuccess(
                `${file.name} uploaded successfully.`
            );

            setFile(null);

            if (inputRef.current) {
                inputRef.current.value = "";
            }

            if (onUploaded) {
                await onUploaded();
            }
        } catch (err) {
            console.error("Upload error:", err);

            setError(
                err.response?.data?.detail ||
                "Upload failed. Please try again."
            );
        } finally {
            setUploading(false);
        }
    }

    function clearFile() {
        if (uploading) return;

        setFile(null);
        setError("");
        setSuccess("");

        if (inputRef.current) {
            inputRef.current.value = "";
        }
    }

    return (
        <div className="upload-card">

            <div className="upload-icon">
                <Upload size={25} />
            </div>

            <div className="upload-content">

                <h3>Upload Research Document</h3>

                <p>
                    Add research papers to your
                    ResearchRAG knowledge base.
                </p>

                <div
                    className={`upload-dropzone ${
                        dragging ? "dragging" : ""
                    }`}
                    onDragOver={(event) => {
                        event.preventDefault();
                        setDragging(true);
                    }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => {
                        if (!uploading) {
                            inputRef.current?.click();
                        }
                    }}
                >
                    <Upload size={30} />

                    <strong>
                        Drag and drop your PDF here
                    </strong>

                    <span>
                        or click to browse files
                    </span>

                    <small>
                        PDF files · Maximum 25 MB
                    </small>

                    <input
                        ref={inputRef}
                        type="file"
                        accept=".pdf,application/pdf"
                        onChange={handleFileChange}
                        hidden
                    />
                </div>

                {file && (
                    <div className="selected-file">
                        <FileText size={20} />

                        <span>{file.name}</span>

                        <button
                            type="button"
                            onClick={clearFile}
                            disabled={uploading}
                            aria-label="Remove selected file"
                        >
                            <X size={17} />
                        </button>
                    </div>
                )}

                {uploading && (
                    <div className="upload-progress">

                        <div className="upload-progress-info">
                            <span>Uploading document...</span>
                            <strong>{progress}%</strong>
                        </div>

                        <div className="progress-track">
                            <div
                                className="progress-fill"
                                style={{
                                    width: `${progress}%`,
                                }}
                            />
                        </div>
                    </div>
                )}

                {error && (
                    <div className="upload-error">
                        <AlertCircle size={17} />
                        {error}
                    </div>
                )}

                {success && (
                    <div className="upload-success">
                        <CheckCircle size={17} />
                        {success}
                    </div>
                )}

                <button
                    type="button"
                    className="upload-button"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                >
                    {uploading
                        ? "Uploading..."
                        : "Upload PDF"}
                </button>

            </div>
        </div>
    );
}

export default DocumentUploader;