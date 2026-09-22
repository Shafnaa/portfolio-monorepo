import { createFileRoute } from '@tanstack/react-router'

import { ChatProvider } from '@/components/providers/chat-provider';

import { Chat } from './_components/chat';

export const Route = createFileRoute('/')({ component: Home })

function Home() {
  return (
    <ChatProvider>
      <Chat />
    </ChatProvider>
  )
}
