import { useEffect, useRef } from "react";
import { Bot, Sparkles } from "lucide-react";

import Message from "./Message";

function ChatWindow({
    messages = [],
    loading = false,
}) {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        });
    }, [messages, loading]);

    if (messages.length === 0 && !loading) {
        return (
            <div className="chat-empty">
                <div className="chat-empty-content">
                    <div className="chat-empty-icon">
                        <Sparkles size={32} />
                    </div>

                    <h1>ResearchRAG</h1>

                    <p>
                        Your AI-powered research assistant.
                        Ask questions about your indexed
                        research documents.
                    </p>

                    <div className="chat-suggestions">
                        <div>
                            Summarize my research papers
                        </div>

                        <div>
                            Explain the key findings
                        </div>

                        <div>
                            Compare research methodologies
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="chat-window">
            <div className="messages-container">
                {messages.map((message, index) => (
                    <Message
                        key={
                            message.id ||
                            `${message.role}-${index}`
                        }
                        role={message.role}
                        content={message.content}
                        citations={message.citations || []}
                        timestamp={
                            message.created_at ||
                            message.createdAt ||
                            message.timestamp
                        }
                    />
                ))}

                {loading && (
                    <div className="message-row message-assistant">
                        <div className="message-icon">
                            <Bot size={19} />
                        </div>

                        <div className="message-body">
                            <div className="message-role">
                                ResearchRAG
                            </div>

                            <div className="typing-indicator">
                                <span />
                                <span />
                                <span />
                            </div>

                            <div className="generation-status">
                                Analyzing your research question...
                            </div>
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>
        </div>
    );
}

export default ChatWindow;