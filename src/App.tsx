import AppRoutes from "./routes/AppRoutes";
import AmbientBackground from "./components/layout/AmbientBackground";
import WhatsAppChatButton from "./components/layout/WhatsAppChatButton";
import AIChatbotButton from "./components/layout/AIChatbotButton";

function App() {
  return (
    <div className="relative min-h-screen isolate">
      <AmbientBackground fixed />
      <div className="relative z-10">
        <AppRoutes />
      </div>
      <AIChatbotButton />
      <WhatsAppChatButton />
    </div>
  );
}

export default App;
