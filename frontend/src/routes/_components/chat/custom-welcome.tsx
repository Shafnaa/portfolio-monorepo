export function CustomWelcome() {
  return (
    <div className="aui-thread-welcome-root mb-6 flex flex-col items-center gap-2 px-4 text-center">
      <h1 className="aui-thread-welcome-message-inner fade-in slide-in-from-bottom-1 animate-in fill-mode-both text-2xl font-medium tracking-tight duration-200">
        Hi! This is Saujana's digital twin.
      </h1>
      <p className="text-gray-600">You can ask me anything about my skills, experiences, projects, or even my thoughts on something relevant to personal growth!</p>
      {/* I want to add PS: Sorry, currently the file attachment is not working. I'm still working on it. Thanks for the understanding! */}
      <p className="text-xs text-muted-foreground">
        PS: Sorry, currently the file attachment is not working. Thanks for the understanding!
      </p>
    </div>
  )
}