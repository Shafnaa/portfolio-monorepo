import { Thread } from "#/components/assistant-ui/thread";

import { CustomWelcome } from "./chat/custom-welcome";

export function Chat() {
  return (
    <div className="w-full h-screen">
      <Thread components={{ Welcome: CustomWelcome }} />
    </div>
  )
}
