import { useRef, useState } from "react";

import {
    Send,
    Loader2,
} from "lucide-react";

function ChatInput({
    onSend,
    disabled = false,
}) {
    const [message, setMessage] = useState("");

    const textareaRef = useRef(null);

    function handleChange(event) {
        setMessage(event.target.value);

        const textarea = event.target;

        textarea.style.height = "auto";

        textarea.style.height = `${Math.min(
            textarea.scrollHeight,
            180
        )}px`;
    }

    async function handleSubmit(event) {
        event.preventDefault();

        const question = message.trim();

        if (!question || disabled) {
            return;
        }

        try {
            await onSend(question);

            setMessage("");

            if (textareaRef.current) {
                textareaRef.current.style.height = "auto";
            }
        } catch (error) {
            console.error(
                "Message submission failed:",
                error
            );
        }
    }

    function handleKeyDown(event) {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();

            event.currentTarget.form?.requestSubmit();
        }
    }

    return (
        <form
            className="chat-input-container"
            onSubmit={handleSubmit}
        >
            <textarea
                ref={textareaRef}
                className="chat-input"
                placeholder="Ask ResearchRAG anything about your documents..."
                value={message}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                rows={1}
                maxLength={10000}
            />

            <button
                type="submit"
                className="send-button"
                disabled={
                    disabled ||
                    !message.trim()
                }
                title="Send message"
                aria-label="Send message"
            >
                {disabled ? (
                    <Loader2
                        size={19}
                        className="spin"
                    />
                ) : (
                    <Send size={19} />
                )}
            </button>
        </form>
    );
}

export default ChatInput;