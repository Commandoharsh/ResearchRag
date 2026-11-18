import { useEffect, useMemo, useState } from "react";

import {
    FileText,
    RefreshCw,
    Search,
    CheckCircle,
    Clock,
    XCircle,
    Files,
    Database,
} from "lucide-react";

import DocumentUploader from "../components/DocumentUploader";
import { getDocuments } from "../api/documents";

function formatBytes(bytes) {
    if (!bytes || bytes <= 0) return "0 B";

    const units = ["B", "KB", "MB", "GB"];

    const index = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
    );

    return `${(bytes / Math.pow(1024, index)).toFixed(1)} ${units[index]}`;
}

function formatDate(date) {
    if (!date) return "-";

    const parsed = new Date(date);

    if (Number.isNaN(parsed.getTime())) return "-";

    return parsed.toLocaleString();
}

function StatusBadge({ status }) {
    const normalized = String(status || "unknown").toLowerCase();

    const configurations = {
        indexed: {
            icon: CheckCircle,
            label: "Indexed",
        },
        indexing: {
            icon: Clock,
            label: "Indexing",
        },
        failed: {
            icon: XCircle,
            label: "Failed",
        },
    };

    const configuration = configurations[normalized];
    const Icon = configuration?.icon;

    return (
        <span className={`document-status ${normalized}`}>
            {Icon && <Icon size={14} />}
            {configuration?.label || normalized}
        </span>
    );
}

function StatCard({ title, value, icon: Icon, description }) {
    return (
        <div className="document-stat-card">
            <div className="document-stat-icon">
                <Icon size={21} />
            </div>

            <div className="document-stat-value">
                {value}
            </div>

            <div className="document-stat-title">
                {title}
            </div>

            <div className="document-stat-description">
                {description}
            </div>
        </div>
    );
}

function Documents() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [search, setSearch] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");

    async function loadDocuments() {
        try {
            setLoading(true);
            setError("");

            const data = await getDocuments();

            const items = Array.isArray(data)
                ? data
                : data.documents || [];

            setDocuments(items);
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.detail ||
                "Failed to load documents."
            );
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadDocuments();
    }, []);

    const statistics = useMemo(() => {
        const indexed = documents.filter(
            (document) => document.status === "indexed"
        ).length;

        const indexing = documents.filter(
            (document) => document.status === "indexing"
        ).length;

        const failed = documents.filter(
            (document) => document.status === "failed"
        ).length;

        const totalChunks = documents.reduce(
            (total, document) =>
                total + (Number(document.chunk_count) || 0),
            0
        );

        return {
            total: documents.length,
            indexed,
            indexing,
            failed,
            totalChunks,
        };
    }, [documents]);

    const filteredDocuments = useMemo(() => {
        return documents
            .filter((document) => {
                const matchesSearch = String(
                    document.filename || ""
                )
                    .toLowerCase()
                    .includes(search.toLowerCase());

                const matchesStatus =
                    statusFilter === "all" ||
                    document.status === statusFilter;

                return matchesSearch && matchesStatus;
            })
            .sort((a, b) => {
                return (
                    new Date(b.updated_at || 0) -
                    new Date(a.updated_at || 0)
                );
            });
    }, [documents, search, statusFilter]);

    return (
        <div className="documents-page">

            <div className="documents-header">
                <div>
                    <h1>Research Documents</h1>

                    <p>
                        Manage and explore your research knowledge base.
                    </p>
                </div>

                <button
                    className="refresh-button"
                    onClick={loadDocuments}
                    disabled={loading}
                >
                    <RefreshCw
                        size={17}
                        className={loading ? "spin" : ""}
                    />

                    Refresh
                </button>
            </div>

            <div className="document-stats-grid">

                <StatCard
                    title="Total Documents"
                    value={statistics.total}
                    icon={Files}
                    description="Uploaded documents"
                />

                <StatCard
                    title="Indexed"
                    value={statistics.indexed}
                    icon={CheckCircle}
                    description="Ready for retrieval"
                />

                <StatCard
                    title="Processing"
                    value={statistics.indexing}
                    icon={Clock}
                    description="Currently indexing"
                />

                <StatCard
                    title="Total Chunks"
                    value={statistics.totalChunks}
                    icon={Database}
                    description="Knowledge base segments"
                />

            </div>

            <DocumentUploader onUploaded={loadDocuments} />

            {error && (
                <div className="document-error">
                    {error}
                </div>
            )}

            <div className="documents-toolbar">

                <div>
                    <h2>All Documents</h2>

                    <p>
                        {filteredDocuments.length} of{" "}
                        {documents.length} documents
                    </p>
                </div>

                <div className="document-filters">

                    <div className="document-search">
                        <Search size={17} />

                        <input
                            type="search"
                            placeholder="Search documents..."
                            value={search}
                            onChange={(event) =>
                                setSearch(event.target.value)
                            }
                        />
                    </div>

                    <select
                        value={statusFilter}
                        onChange={(event) =>
                            setStatusFilter(event.target.value)
                        }
                        aria-label="Filter documents by status"
                    >
                        <option value="all">All statuses</option>
                        <option value="indexed">Indexed</option>
                        <option value="indexing">Indexing</option>
                        <option value="failed">Failed</option>
                    </select>

                </div>

            </div>

            <div className="documents-card">

                {loading ? (
                    <div className="documents-empty">
                        Loading documents...
                    </div>
                ) : filteredDocuments.length === 0 ? (
                    <div className="documents-empty">
                        <FileText size={40} />

                        <h3>
                            {documents.length === 0
                                ? "No documents yet"
                                : "No matching documents"}
                        </h3>

                        <p>
                            {documents.length === 0
                                ? "Upload a PDF to start building your research knowledge base."
                                : "Try changing your search or status filter."}
                        </p>
                    </div>
                ) : (
                    <div className="documents-table-wrapper">

                        <table className="documents-table">

                            <thead>
                                <tr>
                                    <th>Document</th>
                                    <th>Type</th>
                                    <th>Size</th>
                                    <th>Chunks</th>
                                    <th>Status</th>
                                    <th>Last Updated</th>
                                </tr>
                            </thead>

                            <tbody>
                                {filteredDocuments.map((document) => (
                                    <tr key={document.id}>

                                        <td>
                                            <div className="document-name">
                                                <FileText size={19} />

                                                <span>
                                                    {document.filename}
                                                </span>
                                            </div>
                                        </td>

                                        <td>
                                            {document.file_type || "PDF"}
                                        </td>

                                        <td>
                                            {formatBytes(document.file_size)}
                                        </td>

                                        <td>
                                            {document.chunk_count ?? 0}
                                        </td>

                                        <td>
                                            <StatusBadge
                                                status={document.status}
                                            />
                                        </td>

                                        <td>
                                            {formatDate(document.updated_at)}
                                        </td>

                                    </tr>
                                ))}
                            </tbody>

                        </table>

                    </div>
                )}

            </div>

        </div>
    );
}

export default Documents;