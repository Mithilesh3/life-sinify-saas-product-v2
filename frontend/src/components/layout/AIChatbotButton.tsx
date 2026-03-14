export default function AIChatbotButton() {
  return (
    <button
      type="button"
      className="ai-chatbot-button"
      aria-label="Open AI Chatbot"
      title="AI Chatbot"
    >
      <svg className="ai-chatbot-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 2a4 4 0 0 0-4 4v1.1A6 6 0 0 0 4 13v2a6 6 0 0 0 6 6h4a6 6 0 0 0 6-6v-2a6 6 0 0 0-4-5.9V6a4 4 0 0 0-4-4Zm-2 4a2 2 0 1 1 4 0v1h-4V6Zm-2 7a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Zm8 0a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Zm-5.5 4.5h3a.75.75 0 0 1 0 1.5h-3a.75.75 0 0 1 0-1.5Z"
        />
      </svg>
    </button>
  );
}
