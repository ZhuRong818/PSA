import { useEffect, useState } from "react";

type ToastType = "info" | "success" | "error";

type ToastMessage = {
  id: number;
  type: ToastType;
  text: string;
};

const listeners = new Set<(message: ToastMessage) => void>();

let counter = 0;

function emit(type: ToastType, text: string) {
  const message: ToastMessage = { id: ++counter, type, text };
  listeners.forEach((listener) => listener(message));
}

export const toast = {
  info: (text: string) => emit("info", text),
  success: (text: string) => emit("success", text),
  error: (text: string) => emit("error", text),
};

export function ToastViewport() {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const listener = (message: ToastMessage) => {
      setMessages((current) => [...current, message].slice(-4));
      window.setTimeout(() => {
        setMessages((current) => current.filter((item) => item.id !== message.id));
      }, 3600);
    };
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }, []);

  return (
    <div className="toast-viewport" role="status" aria-live="polite">
      {messages.map((message) => (
        <div key={message.id} className={`toast ${message.type}`}>
          {message.text}
        </div>
      ))}
    </div>
  );
}
