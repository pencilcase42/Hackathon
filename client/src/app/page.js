// src/app/page.js
"use client";

import { useState } from 'react';

export default function Home() {
  const [papers, setPapers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPapers, setShowPapers] = useState(false);
  const [topic, setTopic] = useState('ai');
  const [timeFrame, setTimeFrame] = useState(10);
  
  // Function to format date
  const formatDate = (dateString) => {
    try {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('en-US', options);
    } catch (e) {
      return dateString || 'Unknown date';
    }
  };
  
  // Function to handle button click
  const handleRetrievePapers = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Call the API route with parameters (even though they're not used by main.py currently)
      const response = await fetch(`/api/retrieve-papers?topic=${encodeURIComponent(topic)}&timeFrame=${timeFrame}`);
      const data = await response.json();
      
      if (response.ok) {
        setPapers(data.papers || []);
        setShowPapers(true);
      } else {
        setError(data.error || 'Failed to retrieve papers');
      }
    } catch (err) {
      setError('An error occurred while retrieving papers');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to get back to search
  const handleBackToSearch = () => {
    setShowPapers(false);
  };

  return (
    <main className="container">
      <h1 className="title">Research Papers</h1>
      
      {!showPapers ? (
        <div className="empty-state">
          <p>No papers are currently displayed.</p>
          
          <div className="search-controls">
            <div className="input-group">
              <label htmlFor="topic">Topic:</label>
              <input 
                type="text" 
                id="topic" 
                value={topic} 
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., artificial intelligence"
              />
            </div>
            
            <div className="input-group">
              <label htmlFor="timeFrame">Time Frame (days):</label>
              <input 
                type="number" 
                id="timeFrame" 
                value={timeFrame} 
                onChange={(e) => setTimeFrame(e.target.value)}
                min="1" 
                max="365"
              />
            </div>
          </div>
          
          <button 
            className="retrieve-button"
            onClick={handleRetrievePapers}
            disabled={isLoading}
          >
            {isLoading ? 'Retrieving...' : 'Retrieve Latest Papers'}
          </button>
          
          {error && <p className="error-message">{error}</p>}
        </div>
      ) : (
        <div className="stack">
          <button 
            className="back-button"
            onClick={handleBackToSearch}
          >
            Back to Search
          </button>
          
          {papers.length > 0 ? (
            papers.map((paper, index) => (
              <div key={paper.id || paper._id || index} className="card">
                <div className="card-header">
                  <h2 className="card-title">{paper.title}</h2>
                  <div className="card-meta">
                    <span className="author">By {paper.author || 'Unknown'}</span>
                    {paper.date && <span className="date">{formatDate(paper.date)}</span>}
                  </div>
                </div>
                <p className="summary">{paper.summary || 'No summary available'}</p>
                {paper.tags && paper.tags.length > 0 && (
                  <div className="tags">
                    {paper.tags.map((tag, idx) => (
                      <span key={idx} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-results">No papers found in the database.</p>
          )}
        </div>
      )}
    </main>
  );
}
