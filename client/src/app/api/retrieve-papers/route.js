// src/app/api/retrieve-papers/route.js
import { exec } from 'child_process';
import { NextResponse } from 'next/server';

const LOG_PREFIX = "[API]";

export async function GET(request) {
  // Get query parameters
  const { searchParams } = new URL(request.url);
  const topic = searchParams.get('topic') || 'ai';
  const timeFrame = searchParams.get('timeFrame') || '10';
  const checkNew = searchParams.get('checkNew') === 'true';
  
  // If it's a polling request, retrieve papers from database directly
  if (checkNew) {
    return getLatestPapersFromDB();
  }
  
  // Otherwise, start the paper retrieval and summary generation process
  console.log(`${LOG_PREFIX} Starting paper retrieval for topic: "${topic}", timeFrame: ${timeFrame}`);
  
  return new Promise((resolve) => {
    // Start the main process to fetch and process papers
    console.log(`${LOG_PREFIX} Running main.py to fetch and process papers...`);
    const mainProcess = exec(`python scripts/main.py`);
    
    let dataReceived = false;
    
    // Listen for the "initial papers ready" signal from main.py
    mainProcess.stdout.on('data', (data) => {
      const message = data.toString().trim();
      console.log(`${LOG_PREFIX} main.py → ${message}`);
      
      // Check if we've received the signal that initial papers are ready
      if (message.includes('INITIAL_PAPERS_READY') && !dataReceived) {
        dataReceived = true;
        console.log(`${LOG_PREFIX} Initial papers inserted, retrieving from database...`);
        
        // Now get the papers from the database
        getLatestPapersFromDB().then(response => {
          resolve(response);
        });
      }
    });
    
    // Handle errors from main.py
    mainProcess.stderr.on('data', (data) => {
      // Only log non-trivial messages to reduce noise
      const message = data.toString().trim();
      if (message.includes('Error') || message.includes('Processing paper')) {
        console.error(`${LOG_PREFIX} main.py stderr: ${message}`);
      }
    });
    
    // Handle if process ends without sending the signal
    mainProcess.on('close', (code) => {
      if (!dataReceived) {
        console.error(`${LOG_PREFIX} main.py exited with code ${code} without signaling paper insertion`);
        
        // Try to get papers anyway
        getLatestPapersFromDB().then(response => {
          resolve(response);
        });
      }
    });
    
    // Set a timeout in case the process hangs
    setTimeout(() => {
      if (!dataReceived) {
        console.error(`${LOG_PREFIX} Timeout waiting for main.py to signal paper insertion`);
        
        // Try to get papers anyway
        getLatestPapersFromDB().then(response => {
          resolve(response);
        });
      }
    }, 30000); // 30 second timeout
  });
}

// New endpoint to poll for papers
export async function POST(request) {
  return getLatestPapersFromDB(false); // Pass false to indicate it's a poll request (less verbose)
}

// Helper function to get papers from the database
async function getLatestPapersFromDB(verbose = true) {
  return new Promise((resolve) => {
    if (verbose) {
      console.log(`${LOG_PREFIX} Retrieving papers from database...`);
    }
    
    // Run retrieve_all_papers.py to get papers from the database
    const retrieveProcess = exec('python scripts/retrieve_all_papers.py');
    
    let scriptOutput = '';
    
    // Collect data from the retrieve script
    retrieveProcess.stdout.on('data', (data) => {
      scriptOutput += data.toString();
    });
    
    // Handle errors from the retrieve script
    retrieveProcess.stderr.on('data', (data) => {
      // Only log if it contains something that seems important
      const message = data.toString().trim();
      if (message.includes('[') || verbose) {
        console.error(`${LOG_PREFIX} retrieve_all_papers.py: ${message}`);
      }
    });
    
    // When the retrieve script finishes
    retrieveProcess.on('close', (retrieveCode) => {
      if (retrieveCode !== 0) {
        console.error(`${LOG_PREFIX} retrieve_all_papers.py exited with code ${retrieveCode}`);
        return resolve(NextResponse.json({ 
          error: `Failed to retrieve papers from database: exited with code ${retrieveCode}` 
        }, { status: 500 }));
      }
      
      try {
        // Parse the output as JSON
        const trimmedOutput = scriptOutput.trim();
        
        if (!trimmedOutput) {
          if (verbose) {
            console.log(`${LOG_PREFIX} No output from retrieve_all_papers.py`);
          }
          return resolve(NextResponse.json({ papers: [] }));
        }
        
        const data = JSON.parse(trimmedOutput);
        if (verbose) {
          console.log(`${LOG_PREFIX} Retrieved ${Array.isArray(data) ? data.length : 0} papers from database`);
        }
        
        if (data.error) {
          console.error(`${LOG_PREFIX} Error in retrieved data: ${data.error}`);
          return resolve(NextResponse.json({ 
            error: data.error 
          }, { status: 500 }));
        }
        
        // Return the papers to the frontend
        resolve(NextResponse.json({ papers: data }));
        
      } catch (error) {
        console.error(`${LOG_PREFIX} Failed to parse script output: ${error.message}`);
        resolve(NextResponse.json({ 
          error: 'Failed to parse script output' 
        }, { status: 500 }));
      }
    });
  });
}
