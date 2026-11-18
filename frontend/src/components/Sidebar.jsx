import { useEffect, useState } from "react";

import {
    Plus,
    MessageSquare,
    FileText,
    Activity,
    Trash2,
    Loader2,
} from "lucide-react";

import {
    createConversation,
    getConversations,
    deleteConversation,
} from "../api/conversations";

function Sidebar({
    activeConversationId,
    onConversationSelect,
    onConversationCreated,
    onDocuments,
    onMonitoring,
}) {
    const [conversations, setConversations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [error, setError] = useState("");

    async function loadConversations() {
        try {
            setLoading(true);
            setError("");

            const data = await getConversations();

            setConversations(
                Array.isArray(data) ? data : []
            );
        } catch (err) {
            console.error(err);
            setError("Unable to load conversations.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadConversations();
    }, []);

    async function handleNewConversation() {
        if (creating) return;

        try {
            setCreating(true);
            setError("");

            const conversation = await createConversation(
                "New Conversation"
            );

            if (!conversation?.id) {
                throw new Error(
                    "Invalid conversation response."
                );
            }

            setConversations((previous) => [
                conversation,
                ...previous,
            ]);

            onConversationCreated(conversation);
        } catch (err) {
            console.error(err);
            setError("Could not create a conversation.");
        } finally {
            setCreating(false);
        }
    }

    async function handleDelete(event, conversationId) {
        event.stopPropagation();

        const confirmed = window.confirm(
            "Are you sure you want to delete this conversation?"
        );

        if (!confirmed) return;

        try {
            setDeletingId(conversationId);
            setError("");

            await deleteConversation(conversationId);

            setConversations((previous) =>
                previous.filter(
                    (conversation) =>
                        conversation.id !== conversationId
                )
            );

            if (activeConversationId === conversationId) {
                onConversationSelect(null);
            }
        } catch (err) {
            console.error(err);
            setError("Could not delete the conversation.");
        } finally {
            setDeletingId(null);
        }
    }

    return (
        <aside className="sidebar">

            <div className="sidebar-header">
                <div className="brand">
                    ResearchRAG
                </div>

                <button
                    className="new-chat-button"
                    onClick={handleNewConversation}
                    disabled={creating}
                    title="New conversation"
                    aria-label="Create new conversation"
                >
                    {creating ? (
                        <Loader2
                            size={20}
                            className="spin"
                        />
                    ) : (
                        <Plus size={21} />
                    )}
                </button>
            </div>

            {error && (
                <div className="sidebar-error">
                    {error}
                </div>
            )}

            <div className="sidebar-section">

                <div className="sidebar-section-title">
                    Conversations
                </div>

                <div className="conversation-list">

                    {loading && (
                        <div className="sidebar-empty">
                            Loading conversations...
                        </div>
                    )}

                    {!loading &&
                        conversations.length === 0 && (
                            <div className="sidebar-empty">
                                No conversations yet.
                            </div>
                        )}

                    {!loading &&
                        conversations.map((conversation) => (
                            <div
                                key={conversation.id}
                                className={`conversation-item ${
                                    activeConversationId ===
                                    conversation.id
                                        ? "active"
                                        : ""
                                }`}
                                onClick={() =>
                                    onConversationSelect(
                                        conversation.id
                                    )
                                }
                                role="button"
                                tabIndex={0}
                                onKeyDown={(event) => {
                                    if (
                                        event.key === "Enter" ||
                                        event.key === " "
                                    ) {
                                        event.preventDefault();

                                        onConversationSelect(
                                            conversation.id
                                        );
                                    }
                                }}
                            >
                                <MessageSquare size={16} />

                                <span className="conversation-title">
                                    {conversation.title ||
                                        "Untitled conversation"}
                                </span>

                                <button
                                    className="delete-conversation"
                                    onClick={(event) =>
                                        handleDelete(
                                            event,
                                            conversation.id
                                        )
                                    }
                                    disabled={
                                        deletingId === conversation.id
                                    }
                                    title="Delete conversation"
                                    aria-label="Delete conversation"
                                >
                                    {deletingId === conversation.id ? (
                                        <Loader2
                                            size={14}
                                            className="spin"
                                        />
                                    ) : (
                                        <Trash2 size={14} />
                                    )}
                                </button>
                            </div>
                        ))}
                </div>
            </div>

            <div className="sidebar-bottom">

                <button
                    className="sidebar-nav-button"
                    onClick={onDocuments}
                >
                    <FileText size={18} />
                    <span>Documents</span>
                </button>

                <button
                    className="sidebar-nav-button"
                    onClick={onMonitoring}
                >
                    <Activity size={18} />
                    <span>Monitoring</span>
                </button>

            </div>

        </aside>
    );
}

export default Sidebar;