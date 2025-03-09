import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

const LOG_PREFIX = "[SEARCH-API]";

export async function POST(request) {
  try {
    // Get data from request body
    const body = await request.json();
    const { query, conversation } = body;
    
    console.log(`${LOG_PREFIX} Processing request: query="${query}"`);
    
    // Prepare input for the Python script
    const inputData = JSON.stringify({
      query,
      conversation
    });
    
    // Use a temporary file to pass JSON data to the Python script
    const tempId = uuidv4();
    const tempFilePath = path.join(process.cwd(), `temp_${tempId}.json`);
    
    // Write the input data to the temp file
    fs.writeFileSync(tempFilePath, inputData);
    
    return new Promise((resolve) => {
      // Execute search_main.py with the path to the input JSON file
      const searchProcess = spawn('python', ['scripts/search_main.py', tempFilePath]);
      
      let scriptOutput = '';
      
      // Collect output from the script
      searchProcess.stdout.on('data', (data) => {
        scriptOutput += data.toString();
        console.log(`${LOG_PREFIX} Python script stdout: ${data}`);
      });
      
      // Handle errors
      searchProcess.stderr.on('data', (data) => {
        console.error(`${LOG_PREFIX} Python script stderr: ${data}`);
      });
      
      // When the script finishes
      searchProcess.on('close', (code) => {
        // Clean up the temp file
        try {
          if (fs.existsSync(tempFilePath)) {
            fs.unlinkSync(tempFilePath);
          }
        } catch (cleanupErr) {
          console.error(`${LOG_PREFIX} Error cleaning up temp file: ${cleanupErr}`);
        }
        
        if (code !== 0) {
          console.error(`${LOG_PREFIX} Script exited with code ${code}`);
          return resolve(NextResponse.json({ 
            error: `Search failed with code ${code}` 
          }, { status: 500 }));
        }
        
        try {
          // Parse the output as JSON
          const data = JSON.parse(scriptOutput.trim());
          
          // Return the response
          resolve(NextResponse.json(data));
          
        } catch (error) {
          console.error(`${LOG_PREFIX} Failed to parse script output:`, error);
          resolve(NextResponse.json({ 
            error: 'Failed to parse search results',
            raw_output: scriptOutput
          }, { status: 500 }));
        }
      });
    });
  } catch (error) {
    console.error(`${LOG_PREFIX} Error processing request:`, error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 