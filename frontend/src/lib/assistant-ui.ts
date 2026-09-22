import {
  AuiConfig,
  Suggestions,
  type ChatModelAdapter,
} from "@assistant-ui/react";

import { getChatCompletions } from "./api/chat";

const modelAdapter: ChatModelAdapter = {
  async *run({ messages }) {
    const stream = await getChatCompletions([...messages]);

    let text = "";
    for await (const chunk of stream) {
      text += chunk.choices[0]?.delta?.content ?? "";
      yield { content: [{ type: "text", text }] };
    }
  },
};

const config = AuiConfig({
  suggestions: Suggestions([
    "Tell me your experience with RAG!",
    "Have you ever worked with Swift?",
  ]),
});

export { modelAdapter, config };
