// src/app/api/retrieve-papers/route.js
import { exec } from 'child_process';
import { NextResponse } from 'next/server';

export async function GET(request) {
  // Get query parameters
  const { searchParams } = new URL(request.url);
  const topic = searchParams.get('topic') || 'ai';
  const timeFrame = searchParams.get('timeFrame') || '10';
  
  console.log(`Retrieving papers for topic: ${topic}, timeFrame: ${timeFrame}`);
  
  return new Promise((resolve) => {
    // First run main.py to fetch from arXiv and store in the database
    console.log("Running main.py to fetch and store papers...");
    const mainProcess = exec(`python scripts/main.py`);
    
    // Handle errors from main.py
    mainProcess.stderr.on('data', (data) => {
      console.error(`main.py stderr: ${data}`);
    });
    
    // Collect any output from main.py
    let mainOutput = '';
    mainProcess.stdout.on('data', (data) => {
      mainOutput += data.toString();
      console.log(`main.py stdout: ${data}`);
    });
    
    // When main.py finishes, retrieve all papers from the database
    mainProcess.on('close', (code) => {
      if (code !== 0) {
        console.error(`main.py exited with code ${code}`);
        return resolve(NextResponse.json({ 
          error: `Failed to run main.py: exited with code ${code}` 
        }, { status: 500 }));
      }
      
      console.log("main.py completed, retrieving papers from database...");
      
      // Now run retrieve_all_papers.py to get papers from the database
      const retrieveProcess = exec('python scripts/retrieve_all_papers.py');
      
      let scriptOutput = '';
      
      // Collect data from the retrieve script
      retrieveProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
        console.log(`retrieve_all_papers.py stdout: ${data}`);
      });
      
      // Handle errors from the retrieve script
      retrieveProcess.stderr.on('data', (data) => {
        console.error(`retrieve_all_papers.py stderr: ${data}`);
      });
      
      // When the retrieve script finishes
      retrieveProcess.on('close', (retrieveCode) => {
        if (retrieveCode !== 0) {
          console.error(`retrieve_all_papers.py exited with code ${retrieveCode}`);
          return resolve(NextResponse.json({ 
            error: `Failed to retrieve papers from database: exited with code ${retrieveCode}` 
          }, { status: 500 }));
        }
        
        try {
          // Parse the output as JSON
          const trimmedOutput = scriptOutput.trim();
          console.log(`Raw output from retrieve_all_papers.py: ${trimmedOutput}`);
          
          if (!trimmedOutput) {
            console.log("No output from retrieve_all_papers.py");
            return resolve(NextResponse.json({ papers: [] }));
          }
          
          const data = JSON.parse(trimmedOutput);
          console.log(`Retrieved ${Array.isArray(data) ? data.length : 0} papers from database`);
          
          if (data.error) {
            console.error(`Error in retrieved data: ${data.error}`);
            return resolve(NextResponse.json({ 
              error: data.error 
            }, { status: 500 }));
          }
          
          // Return the papers to the frontend
          resolve(NextResponse.json({ papers: data }));
          
        } catch (error) {
          console.error(`Failed to parse script output: ${error.message}`);
          console.error(`Script output was: ${scriptOutput}`);
          resolve(NextResponse.json({ 
            error: 'Failed to parse script output' 
          }, { status: 500 }));
        }
      });
    });
  });
}
