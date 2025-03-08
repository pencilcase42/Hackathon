// src/app/page.js
"use client"; // Important: This makes it a Client Component

import { useState } from 'react';

export default function Home() {
  // State to track whether papers have been retrieved
  const [showPapers, setShowPapers] = useState(false);
  
  // Project data
  const tiles = [
    { id: 1, title: "Paper One", author: "John Doe", date: "2024-01-01", tags: ["tag1", "tag2"], summary: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in dui mauris." },
    { id: 2, title: "Paper Two", author: "Jane Smith", date: "2024-01-02", tags: ["tag3", "tag4"], summary: "Fusce convallis metus id felis luctus adipiscing. Pellentesque egestas, neque sit amet convallis pulvinar." },
    { id: 3, title: "Paper Three", author: "John Doe", date: "2024-01-03", tags: ["tag5", "tag6"], summary: "Sed lectus. Donec mollis hendrerit risus. Phasellus nec sem in justo pellentesque facilisis." },
    { id: 4, title: "Paper Four", author: "Jane Smith", date: "2024-01-04", tags: ["tag7", "tag8"], summary: "Proin sapien ipsum, porta a, auctor quis, euismod ut, mi. Aenean viverra rhoncus pede." },
    { id: 5, title: "Paper Five", author: "John Doe", date: "2024-01-05", tags: ["tag9", "tag10"], summary: "Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo." },
    { id: 6, title: "Paper Six", author: "Jane Smith", date: "2024-01-06", tags: ["tag11", "tag12"], summary: "Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna." },
  ];

  // Function to formate date using fixed locale to avoid hydration errors
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-UK', options);
  };
  

  // Function to handle button click
  const handleRetrievePapers = () => {
    // In a real app, you might fetch data from an API here
    setShowPapers(true);
  };

  return (
    <main className="container">
      <h1 className="title">Research Papers</h1>
      
      {!showPapers ? (
        <div className="empty-state">
          <p>No papers are currently displayed.</p>
          <button 
            className="retrieve-button"
            onClick={handleRetrievePapers}
          >
            Retrieve Latest Papers
          </button>
        </div>
      ) : (
        <div className="stack">
          {tiles.map((tile) => (
            <div key={tile.id} className="card">
              <div className="card-header">
                <h2 className="card-title">{tile.title}</h2>
                <div className="card-meta">
                  <span className="author">By {tile.author}</span>
                  <span className="date">{formatDate(tile.date)}</span>
                </div>
              </div>
              <p className="summary">{tile.summary}</p>
              <div className="tags">
                {tile.tags.map((tag, index) => (
                  <span key={index} className="tag">{tag}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
