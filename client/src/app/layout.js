import './globals.css'

export const metadata = {
  title: 'Paper Summariser',
  description: 'A web app for summarising papers',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
