"use client";

import { useState, useRef, useEffect } from 'react';

export default function SearchPage() {
  // State for storing chat messages
  const [messages, setMessages] = useState([
    // Start with a welcome message
    { 
      type: 'assistant', 
      content: 'Hello! I can help you search for research papers on any topic. What would you like to search for?' 
    }
  ]);
  
  // State for the current input value
  const [inputValue, setInputValue] = useState('');
  
  // State for loading indicator
  const [isLoading, setIsLoading] = useState(false);
  
  // State to track conversation history for the backend
  const [conversationHistory, setConversationHistory] = useState([]);
  
  // State to store found papers
  const [papers, setPapers] = useState([]);
  
  // State to control if we're showing papers
  const [showingPapers, setShowingPapers] = useState(false);
  
  // Ref for auto-scrolling to the bottom of messages
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  // Format date for display
  const formatDate = (dateString) => {
    try {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString('en-US', options);
    } catch (e) {
      return dateString || 'Unknown date';
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Add user message to chat
    const userMessage = { type: 'user', content: inputValue.trim() };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Call our API endpoint
      const response = await fetch('/api/search-papers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          conversation: conversationHistory
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Add assistant response to chat
        setMessages([
          ...updatedMessages,
          { type: 'assistant', content: data.message || 'I processed your request.' }
        ]);
        
        // Update conversation history if returned
        if (data.conversation) {
          setConversationHistory(data.conversation);
        }
        
        // If papers were returned, update papers state
        if (data.papers && data.papers.length > 0) {
          console.log('Papers found:', data.papers);
          setPapers(data.papers);
          
          // If this is a final response with papers, show the papers section
          if (data.is_final) {
            setShowingPapers(true);
          }
        } else {
          // Reset papers if none were found
          setPapers([]);
          setShowingPapers(false);
        }
      } else {
        // Handle error
        setMessages([
          ...updatedMessages,
          { type: 'assistant', content: `Error: ${data.error || 'Something went wrong'}` }
        ]);
      }
    } catch (error) {
      console.error('Error calling API:', error);
      setMessages([
        ...updatedMessages,
        { type: 'assistant', content: 'Sorry, there was an error processing your request.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="container">
      <h1 className="title">Search Papers</h1>
      
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`chat-message ${message.type === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">{message.content}</div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about research papers..."
            className="chat-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="chat-send-button"
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
      
      {showingPapers && papers.length > 0 && (
        <div className="search-results">
          <h2>Found Papers</h2>
          <div className="papers-list">
            {papers.map((paper, index) => (
              <div key={paper.id || index} className="card">
                <div className="card-header">
                  <h3 className="card-title">{paper.title}</h3>
                  <div className="card-meta">
                    <span className="author">By {paper.author || 'Unknown'}</span>
                    {paper.date && <span className="date">{formatDate(paper.date)}</span>}
                  </div>
                </div>
                <p className="summary">{paper.summary}</p>
                {paper.tags && paper.tags.length > 0 && (
                  <div className="tags">
                    {paper.tags.map((tag, idx) => (
                      <span key={idx} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
                {paper.pdf_link && (
                  <a 
                    href={paper.pdf_link} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="pdf-link"
                  >
                    Download PDF
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 