import { AssistantRuntimeProvider, useLocalRuntime } from "@assistant-ui/react";

import { config, modelAdapter } from "@/lib/assistant-ui";

export function ChatProvider({ children }: { children: React.ReactNode }) {
    const runtime = useLocalRuntime(modelAdapter)

    return (
        <AssistantRuntimeProvider runtime={runtime} config={config}>
            {children}
        </AssistantRuntimeProvider>
    )
}