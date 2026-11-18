import { User, Bot, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function formatTimestamp(timestamp) {
    if (!timestamp) {
        return "";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
    });
}

function Message({
    role,
    content,
    citations = [],
    timestamp,
}) {
    const isUser = role === "user";

    return (
        <div
            className={`message-row ${
                isUser
                    ? "message-user"
                    : "message-assistant"
            }`}
        >
            <div className="message-icon">
                {isUser ? (
                    <User size={18} />
                ) : (
                    <Bot size={19} />
                )}
            </div>

            <div className="message-body">
                <div className="message-heading">
                    <div className="message-role">
                        {isUser ? "You" : "ResearchRAG"}
                    </div>

                    {timestamp && (
                        <time className="message-timestamp">
                            {formatTimestamp(timestamp)}
                        </time>
                    )}
                </div>

                <div className="message-content markdown-content">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {String(content || "")}
                    </ReactMarkdown>
                </div>

                {!isUser && citations.length > 0 && (
                    <div className="citation-list">
                        <div className="citation-heading">
                            Referenced Sources
                        </div>

                        {citations.map((citation, index) => (
                            <div
                                className="citation-item"
                                key={
                                    citation.id ||
                                    citation.chunk_id ||
                                    index
                                }
                            >
                                <FileText size={16} />

                                <div className="citation-details">
                                    <span>
                                        {citation.filename ||
                                            citation.source ||
                                            "Research document"}
                                    </span>

                                    {citation.page && (
                                        <small>
                                            Page {citation.page}
                                        </small>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Message;