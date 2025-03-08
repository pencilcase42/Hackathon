// src/app/api/retrieve-papers/route.js
import { exec } from 'child_process';
import { NextResponse } from 'next/server';

export async function GET(request) {
  // Get query parameters
  const { searchParams } = new URL(request.url);
  const topic = searchParams.get('topic') || 'ai';
  const timeFrame = searchParams.get('timeFrame') || '10';
  
  return new Promise((resolve) => {
    // Execute the Python script with parameters
    const pythonProcess = exec(`python scripts/arxiv_api_modified.py "${topic}" ${timeFrame}`);
    
    let scriptOutput = '';
    
    // Collect data from Python script
    pythonProcess.stdout.on('data', (data) => {
      scriptOutput += data.toString();
    });
    
    // Handle errors
    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python script output: ${data}`);
    });
    
    // When the script finishes
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        resolve(NextResponse.json({ 
          error: `Script exited with code ${code}` 
        }, { status: 500 }));
      } else {
        try {
          // Parse the output as JSON
          const data = JSON.parse(scriptOutput);
          
          // Check if the response contains an error
          if (data.error) {
            resolve(NextResponse.json({ 
              error: data.error 
            }, { status: 500 }));
          } else {
            // Return the papers
            resolve(NextResponse.json({ papers: data }));
          }
        } catch (error) {
          resolve(NextResponse.json({ 
            error: 'Failed to parse script output' 
          }, { status: 500 }));
        }
      }
    });
  });
}
