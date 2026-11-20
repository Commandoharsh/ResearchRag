import { User, Bot, FileText } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Message({
    role,
    content,
    citations = [],
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
                    <User size={17} />
                ) : (
                    <Bot size={18} />
                )}
            </div>

            <div className="message-body">
                <div className="message-role">
                    {isUser ? "You" : "ResearchRAG"}
                </div>

                <div className="message-content">
                    {isUser ? (
                        <div className="user-message-text">
                            {content}
                        </div>
                    ) : (
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                a({ href, children }) {
                                    return (
                                        <a
                                            href={href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {children}
                                        </a>
                                    );
                                },

                                code({
                                    children,
                                    className,
                                    ...props
                                }) {
                                    return (
                                        <code
                                            className={className}
                                            {...props}
                                        >
                                            {children}
                                        </code>
                                    );
                                },

                                table({ children }) {
                                    return (
                                        <div className="markdown-table-wrapper">
                                            <table>
                                                {children}
                                            </table>
                                        </div>
                                    );
                                },
                            }}
                        >
                            {String(content ?? "")}
                        </ReactMarkdown>
                    )}
                </div>

                {!isUser && citations.length > 0 && (
                    <div className="citation-list">
                        <div className="citation-heading">
                            <FileText size={16} />
                            Sources
                        </div>

                        {citations.map((citation, index) => (
                            <div
                                className="citation-item"
                                key={citation.id || citation.chunk_id || index}
                            >
                                <FileText size={15} />

                                <div className="citation-details">
                                    <span className="citation-filename">
                                        {citation.filename ||
                                            citation.source ||
                                            "Research document"}
                                    </span>

                                    {citation.page && (
                                        <span className="citation-page">
                                            Page {citation.page}
                                        </span>
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