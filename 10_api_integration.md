# API Integration

Connect React to a FastAPI backend using fetch or Axios. Create a central API utility and read the backend URL from an environment variable. Use POST /api/chat with {question: string}. Expect {answer: string, sources: [{title: string, url: string}]}. Handle loading, network errors, empty responses, invalid responses, and retry. Never hardcode the API URL inside components.