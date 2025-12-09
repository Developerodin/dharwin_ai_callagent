import './globals.css'

export const metadata = {
  title: 'Dharwin Interview Scheduler - Ava',
  description: 'Voice calling agent for interview scheduling',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

