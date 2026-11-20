import { useRef, useState } from "react";
import {
    Upload,
    FileText,
    X,
    CheckCircle2,
    AlertCircle,
} from "lucide-react";

import { uploadDocument } from "../api/upload";

const MAX_FILE_SIZE = 25 * 1024 * 1024;

function DocumentUploader({
    onUploaded,
    onUploadComplete,
}) {
    const inputRef = useRef(null);

    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [dragging, setDragging] = useState(false);

    function validateFile(selectedFile) {
        if (!selectedFile) return false;

        setError("");
        setSuccess("");

        const isPDF =
            selectedFile.type === "application/pdf" ||
            selectedFile.name.toLowerCase().endsWith(".pdf");

        if (!isPDF) {
            setError("Only PDF files are supported.");
            return false;
        }

        if (selectedFile.size > MAX_FILE_SIZE) {
            setError("File size must be less than 25 MB.");
            return false;
        }

        setFile(selectedFile);
        setProgress(0);

        return true;
    }

    function handleFileChange(event) {
        const selectedFile = event.target.files?.[0];

        if (selectedFile) {
            validateFile(selectedFile);
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        setDragging(true);
    }

    function handleDragLeave(event) {
        event.preventDefault();
        setDragging(false);
    }

    function handleDrop(event) {
        event.preventDefault();
        setDragging(false);

        if (uploading) return;

        const droppedFile = event.dataTransfer.files?.[0];

        if (droppedFile) {
            validateFile(droppedFile);
        }
    }

    function clearFile() {
        setFile(null);
        setProgress(0);

        if (inputRef.current) {
            inputRef.current.value = "";
        }
    }

    async function handleUpload() {
        if (!file || uploading) return;

        try {
            setUploading(true);
            setError("");
            setSuccess("");
            setProgress(0);

            const uploadedFileName = file.name;

            await uploadDocument(file, (percentage) => {
                setProgress(percentage);
            });

            setSuccess(`${uploadedFileName} uploaded successfully.`);
            clearFile();

            // Support both callback names.
            const refreshCallback =
                onUploadComplete || onUploaded;

            if (refreshCallback) {
                await refreshCallback();
            }
        } catch (err) {
            console.error("Document upload failed:", err);

            setError(
                err.response?.data?.detail ||
                "Upload failed. Please try again."
            );
        } finally {
            setUploading(false);
        }
    }

    return (
        <div className="upload-card">
            <div
                className={`upload-dropzone ${
                    dragging ? "upload-dragging" : ""
                } ${uploading ? "upload-disabled" : ""}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => {
                    if (!uploading) {
                        inputRef.current?.click();
                    }
                }}
                role="button"
                tabIndex={0}
                onKeyDown={(event) => {
                    if (
                        !uploading &&
                        (event.key === "Enter" || event.key === " ")
                    ) {
                        event.preventDefault();
                        inputRef.current?.click();
                    }
                }}
            >
                <div className="upload-icon">
                    <Upload size={27} />
                </div>

                <div className="upload-content">
                    <h3>Upload Research Document</h3>

                    <p>
                        Drag and drop your PDF here, or{" "}
                        <span className="upload-browse">
                            browse files
                        </span>
                    </p>

                    <span className="upload-hint">
                        PDF format · Maximum file size 25 MB
                    </span>
                </div>

                <input
                    ref={inputRef}
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    disabled={uploading}
                    hidden
                />
            </div>

            {file && (
                <div className="upload-selected-file">
                    <div className="upload-selected-info">
                        <FileText size={20} />

                        <div>
                            <strong>{file.name}</strong>

                            <span>
                                {(file.size / (1024 * 1024)).toFixed(2)} MB
                            </span>
                        </div>
                    </div>

                    {!uploading && (
                        <button
                            type="button"
                            className="upload-remove-button"
                            onClick={clearFile}
                            aria-label="Remove selected file"
                        >
                            <X size={17} />
                        </button>
                    )}
                </div>
            )}

            {uploading && (
                <div className="upload-progress-container">
                    <div className="upload-progress-label">
                        <span>Uploading PDF...</span>
                        <strong>{progress}%</strong>
                    </div>

                    <div
                        className="upload-progress-track"
                        role="progressbar"
                        aria-valuenow={progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                    >
                        <div
                            className="upload-progress-fill"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {file && (
                <button
                    type="button"
                    className="upload-button"
                    onClick={handleUpload}
                    disabled={uploading}
                >
                    {uploading ? "Uploading..." : "Upload PDF"}
                </button>
            )}

            {error && (
                <div className="upload-feedback upload-feedback-error">
                    <AlertCircle size={17} />
                    <span>{error}</span>
                </div>
            )}

            {success && (
                <div className="upload-feedback upload-feedback-success">
                    <CheckCircle2 size={17} />
                    <span>{success}</span>
                </div>
            )}
        </div>
    );
}

export default DocumentUploader;