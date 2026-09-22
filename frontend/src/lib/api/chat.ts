import OpenAI from "openai";

import type { ThreadMessage } from "@assistant-ui/react";

import { OPENAI_BASE_URL, OPENAI_API_KEY } from "../constant";

const client = new OpenAI({
  apiKey: OPENAI_API_KEY,
  baseURL: `${OPENAI_BASE_URL}`,
  dangerouslyAllowBrowser: true, // This is required to allow the OpenAI client to be used in the browser
});

const getChatCompletions = async (messages: ThreadMessage[]) => {
  return await client.chat.completions.create({
    model: "digital-twin",
    messages: messages.map((m) => ({
      role: m.role,
      content: m.content
        .filter((part) => part.type === "text")
        .map((part) => part.text)
        .join("\n"),
    })),
    stream: true,
  });
};

export { getChatCompletions };
