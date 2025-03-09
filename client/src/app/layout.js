import './globals.css'

export const metadata = {
  title: 'Paper Summariser',
  description: 'A web app for summarising papers',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <nav className="main-nav">
            <a href="/" className="nav-link">News</a>
            <a href="/search" className="nav-link">Search</a>
          </nav>
          <main>{children}</main>
        </div>
      </body>
    </html>
  )
}
