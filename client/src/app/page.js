// src/app/page.js
"use client";

import { useState, useEffect } from 'react';

export default function NewsPage() {
  const [papers, setPapers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
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
  
  // Poll for papers when processing is active
  useEffect(() => {
    let pollInterval;
    
    if (isProcessing && showPapers) {
      // Set up polling interval (every 3 seconds)
      pollInterval = setInterval(() => {
        fetchLatestPapers();
      }, 3000);
    }
    
    // Clean up interval when component unmounts or dependencies change
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [isProcessing, showPapers]);
  
  // Function to fetch latest papers from database
  const fetchLatestPapers = async () => {
    try {
      const response = await fetch('/api/retrieve-papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Get new papers
        const newPapers = data.papers || [];
        
        // Check if we have real updates (not just waiting messages)
        const hasRealUpdates = newPapers.some(newPaper => {
          // Find matching paper in current state
          const existingPaper = papers.find(p => p.id === newPaper.id || p._id === newPaper._id);
          
          // If no existing paper or summary changed from waiting message
          return !existingPaper || 
            (newPaper.summary && 
             newPaper.summary !== "Waiting for summary, thank you for your patience." &&
             existingPaper.summary !== newPaper.summary);
        });
        
        // Only update if we have real changes
        if (hasRealUpdates || papers.length !== newPapers.length) {
          console.log("Updating papers with new data");
          setPapers(newPapers);
        }
        
        // Check if processing is complete
        const allHaveSummaries = newPapers.length > 0 && 
          newPapers.every(paper => 
            paper.summary && 
            paper.summary.trim() !== "" && 
            paper.summary !== "Waiting for summary, thank you for your patience."
          );
        
        if (allHaveSummaries && newPapers.length >= 5) {
          console.log("All papers have summaries, stopping polling");
          setIsProcessing(false);
        }
      } else {
        console.error('Error fetching latest papers:', data.error);
      }
    } catch (err) {
      console.error('Error polling for papers:', err);
    }
  };
  
  // Function to handle button click
  const handleRetrievePapers = async () => {
    setIsLoading(true);
    setError(null);
    setPapers([]);  // Clear existing papers
    
    try {
      // Initial call to start processing
      const response = await fetch(`/api/retrieve-papers?topic=${encodeURIComponent(topic)}&timeFrame=${timeFrame}`);
      const data = await response.json();
      
      if (response.ok) {
        // Set processing flag to enable polling
        setIsProcessing(true);
        setShowPapers(true);
        
        // Do initial fetch to get any papers that may already be in the database
        await fetchLatestPapers();
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
    setIsProcessing(false);  // Stop polling
  };

  return (
    <div className="container">
      <h1 className="title">Latest Research Papers</h1>
      
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
          
          {isProcessing && (
            <div className="processing-indicator">
              <p>Retrieving and processing papers... Papers will appear as they are processed.</p>
            </div>
          )}
          
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
                <p className="summary">
                  {paper.summary || 'Summary is being generated...'}
                </p>
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
            <p className="no-results">
              {isProcessing ? 'Retrieving papers...' : 'No papers found in the database.'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
