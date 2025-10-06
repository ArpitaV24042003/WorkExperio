import { useState, useCallback } from "react";
import { Send, CornerUpLeft, PlusCircle, Paperclip, CheckCircle, XCircle, ChevronLeft, GitBranch, Zap, Trophy, TrendingUp, Cpu } from 'lucide-react';

// Firebase and API Constants (Mandatory for a full application)
const apiKey = "";
const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${apiKey}`;

// === Helper Components ===

// Replaces the non-compliant alert()
const CompletionModal = ({ message, onClose }) => {
  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4 font-inter">
      <div className="bg-white p-8 rounded-xl shadow-2xl max-w-sm w-full text-center">
        <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
        <p className="text-lg font-semibold mb-6">{message}</p>
        <button
          onClick={onClose}
          className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition duration-150"
        >
          Close
        </button>
      </div>
    </div>
  );
};

// --- Main Component ---

export default function ProjectDashboardPage() {
  const [activeSection, setActiveSection] = useState("home");
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  
  // --- TASK FLOW STATE ---
  const tasks = [
    { id: 1, title: "Task 1: Draft the Final Report Outline", questions: ["What main sections did you define?", "What are the next two required steps to complete this task?"], completed: false },
    { id: 2, title: "Task 2: Design the Project UI Mockup", questions: ["Why this layout?", "What design tools did you use (Figma, Sketch, etc.)?"], completed: false }
  ];
  const [selectedTask, setSelectedTask] = useState(null);
  const [qIndex, setQIndex] = useState(0); // 0 = task instruction/finish button, 1+ = questions
  const [answer, setAnswer] = useState("");
  const [tempAnswers, setTempAnswers] = useState([]); 
  const [taskData, setTaskData] = useState(tasks); // Use state for tasks to update completion
  const [taskError, setTaskError] = useState(null); // New state for task validation errors

  const handleFinishTask = () => {
    setQIndex(1); // Move to Q&A phase
    setAnswer("");
    setTempAnswers([]); 
    setTaskError(null); 
    // NOTE: In a real app, this would also trigger the AI to generate questions dynamically
  };

  const handleQuestionSubmit = () => {
    setTaskError(null);
    if (answer.trim().length < 5) {
        setTaskError("ERROR: Answer must contain at least 5 characters. Input required for Submission.");
        return;
    }

    // 1. Save the current answer
    const newAnswers = [...tempAnswers, { 
        question: selectedTask.questions[qIndex - 1], 
        answer: answer.trim(),
        taskId: selectedTask.id
    }];
    setTempAnswers(newAnswers);
    
    // Clear the input field immediately
    setAnswer(""); 

    // 2. Check if there are more questions
    if (qIndex < selectedTask.questions.length) {
      setQIndex(qIndex + 1);
    } else {
      // All questions completed, show modal and reset
      setShowCompletionModal(true);
      
      // Update the task as completed
      setTaskData(prevTasks => 
        prevTasks.map(task => 
          task.id === selectedTask.id ? { ...task, completed: true } : task
        )
      );
      
      // *** This is the crucial point for AI Review generation:
      // Trigger API call here to start AI review based on submitted answers and files.
      console.log(`Submitting final answers for Task ${selectedTask.id}:`, newAnswers);

      // Reset task state
      setSelectedTask(null);
      setQIndex(0);
      setTempAnswers([]);
    }
  };

  const handleBackToTasks = () => {
    setSelectedTask(null);
    setQIndex(0);
    setAnswer("");
    setTempAnswers([]); 
    setTaskError(null);
  };

  // --- CHAT STATE (Team Chat) ---
  const [chatMessages, setChatMessages] = useState([
    { id: 1, user: "Supervisor", text: "Welcome to the group chat! Let's coordinate our efforts here.", timestamp: "10:00 AM" },
    { id: 2, user: "You", text: "Great, I'm working on the data models now.", timestamp: "10:05 AM" },
  ]);
  const [chatInput, setChatInput] = useState("");

  const handleSendChat = () => {
    if (chatInput.trim() !== "") {
      const newMessage = {
        id: Date.now(),
        user: "You",
        text: chatInput.trim(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages([...chatMessages, newMessage]);
      setChatInput("");
    }
  };

  // --- CHATBOT STATE (AI Model) ---
  const [botMessages, setBotMessages] = useState([]);
  const [botInput, setBotInput] = useState("");
  const [isBotLoading, setIsBotLoading] = useState(false);

  const handleBotSubmit = async () => {
    const prompt = botInput.trim();
    if (prompt === "") return;

    const userMessage = { sender: "user", text: prompt };
    setBotMessages(prev => [...prev, userMessage]);
    setBotInput("");
    setIsBotLoading(true);

    try {
        const systemPrompt = "You are the 'Project Assistant AI'. Your role is to provide constructive feedback, answer questions, and offer guidance on academic final year projects. Keep your answers concise, helpful, and professional.";
        
        const payload = {
            contents: [{ parts: [{ text: prompt }] }],
            systemInstruction: {
                parts: [{ text: systemPrompt }]
            },
        };

        let response = await fetchWithExponentialBackoff(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const result = await response.json();
        const botResponse = result.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I encountered an error. Please try again.";

        setBotMessages(prev => [...prev, { sender: "bot", text: botResponse }]);

    } catch (error) {
        console.error("Gemini API Error:", error);
        setBotMessages(prev => [...prev, { sender: "bot", text: "Error: Could not connect to the AI Assistant." }]);
    } finally {
        setIsBotLoading(false);
    }
  };

  // Exponential Backoff Fetcher
  const fetchWithExponentialBackoff = async (url, options, retries = 3) => {
    for (let i = 0; i < retries; i++) {
        try {
            return await fetch(url, options);
        } catch (error) {
            if (i === retries - 1) throw error;
            const delay = Math.pow(2, i) * 1000 + Math.random() * 1000;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
  };

  // --- FILE UPLOAD STATE ---
  const [uploadedFiles, setUploadedFiles] = useState([
    { id: 1, name: "Proposal_V1.pdf", size: "1.2 MB", date: "2024-03-01", repoLink: "https://github.com/user/project/proposal.pdf" },
    { id: 2, name: "Database_Schema.sql", size: "45 KB", date: "2024-03-05", repoLink: "https://github.com/user/project/schema.sql" },
    { id: 3, name: "Wireframes.zip", size: "2.5 MB", date: "2024-03-10", repoLink: "https://github.com/user/project/wireframes.zip" }, // Added a third file
  ]);
  
  const handleFileUpload = useCallback((e) => {
    const files = e.target.files;
    if (files.length > 0) {
      const newFiles = Array.from(files).map(file => ({
        id: Date.now() + Math.random(),
        name: file.name,
        size: (file.size / 1024 / 1024).toFixed(2) + " MB",
        date: new Date().toISOString().slice(0, 10),
        // Mocking GitHub link for uploaded files
        repoLink: "https://github.com/user/project/file_" + Date.now().toString().slice(-4)
      }));
      setUploadedFiles(prev => [...prev, ...newFiles]);
    }
  }, []);
  
  // New function to handle file deletion
  const handleDeleteFile = useCallback((fileId) => {
    setUploadedFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  }, []);

  // New function to handle file download (mocked)
  const handleDownloadFile = useCallback((fileName) => {
    // Determine the appropriate MIME type based on the file extension
    const extension = fileName.split('.').pop().toLowerCase();
    let mimeType;
    let mockContent;

    switch (extension) {
        case 'pdf':
            // Using a generic PDF MIME type. The content is still text/mock data.
            mimeType = 'application/pdf'; 
            mockContent = `Mock PDF Content for file: ${fileName}. In a real app, this would be binary PDF data.`;
            break;
        case 'sql':
            // SQL files are typically plain text
            mimeType = 'text/plain'; 
            mockContent = `--- SQL Schema Dump ---\nCREATE TABLE users (id INT, username VARCHAR(50));\nINSERT INTO users VALUES (1, 'mock_user');\n\nFile: ${fileName}`;
            break;
        case 'zip':
            // Using a generic ZIP MIME type. The content is still text/mock data.
            mimeType = 'application/zip'; 
            mockContent = `Mock ZIP Content for file: ${fileName}. This file is corrupted because it's only text, but the browser will recognize the .zip extension.`;
            break;
        default:
            mimeType = 'text/plain';
            mockContent = `Mock file content for: ${fileName}`;
            break;
    }

    const blob = new Blob([mockContent], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName; // Set the name of the file to be downloaded
    
    // Append to body, click, and remove
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // Clean up the object URL
    URL.revokeObjectURL(url);
    
    console.log(`Downloading mock file: ${fileName} with MIME type: ${mimeType}`);
  }, []);


  // --- MENU ITEMS ---
  const menuItems = [
    { name: "Project Home", section: "home", icon: "🏠", color: "bg-indigo-600 text-white" },
    { name: "Tasks & Progress", section: "tasks", icon: "✅", color: "bg-red-500 text-white" },
    { name: "Team Chat", section: "chat", icon: "💬", color: "bg-gray-300 text-gray-800" },
    { name: "Project Chatbot", section: "chatbot", icon: "🤖", color: "bg-gray-300 text-gray-800" },
    { name: "File Upload/Docs", section: "upload", icon: "📁", color: "bg-orange-500 text-white" },
    { name: "Reviews/Feedback", section: "review", icon: "⭐", color: "bg-yellow-500 text-gray-900" },
    { name: "Performance Metrics", section: "performance", icon: "📈", color: "bg-blue-600 text-white" }
  ];

  // === RENDER LOGIC ===

  const renderSection = () => {
    switch (activeSection) {
      case "home":
        return (
          <div className="p-8 bg-white rounded-xl shadow-lg">
            <h1 className="text-3xl font-extrabold text-gray-800 mb-4">Project Dashboard</h1>
            <p className="text-gray-600 text-lg mb-6">
              Welcome! Use the navigation menu to manage your tasks, communicate with your team, and track your progress.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <InfoCard title="Tasks Pending" value={taskData.filter(t => !t.completed).length} color="text-red-500" icon={Zap} />
              <InfoCard title="Files Uploaded" value={uploadedFiles.length} color="text-orange-500" icon={Paperclip} />
              <InfoCard title="Level" value="Rookie" color="text-green-500" icon={Trophy} />
            </div>
            
            <div className="mt-8 p-6 bg-indigo-50 rounded-xl">
              <h2 className="text-2xl font-semibold text-indigo-800 mb-3 flex items-center">
                <Cpu className="w-5 h-5 mr-2" /> 
                Problem Statement
              </h2>
              <p className="text-gray-700">
                [Problem Statement Placeholder: A concise statement of the problem your project aims to solve.]
              </p>
              <p className="text-sm text-gray-500 mt-2">
                [Detailed Description Placeholder: A detailed description of the problem, background, and proposed solution approach.]
              </p>
            </div>
          </div>
        );

      case "tasks":
        if (!selectedTask) {
          return (
            <div className="p-8 bg-white rounded-xl shadow-lg">
              <h1 className="text-3xl font-bold text-gray-800 mb-6">Project Tasks</h1>
              <div className="space-y-4">
                {taskData.map((task) => (
                  <div key={task.id} className="flex justify-between items-center bg-gray-50 border border-gray-200 rounded-lg p-5 transition hover:shadow-md">
                    <div className="flex items-center space-x-3">
                        {task.completed 
                            ? <CheckCircle className="w-6 h-6 text-green-500" />
                            : <Zap className="w-6 h-6 text-red-500" />}
                        <h3 className="font-semibold text-lg text-gray-700">{task.title}</h3>
                        {task.completed && <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full ml-2">COMPLETED</span>}
                    </div>
                    <button
                      onClick={() => setSelectedTask(task)}
                      className="flex items-center bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-600 transition disabled:opacity-50"
                    >
                      <PlusCircle className="w-4 h-4 mr-2" /> Start/View Q&A
                    </button>
                  </div>
                ))}
                
                <div className="pt-4 mt-6 border-t border-gray-200">
                    <h3 className="text-xl font-semibold text-indigo-700">Final Review</h3>
                    <p className="text-gray-600 mt-2">Once all tasks are completed, the final review will be initiated through a chatting interface to assess overall understanding and task done by the user.</p>
                </div>
              </div>
            </div>
          );
        } else {
          return (
            <div className="p-8 bg-white rounded-xl shadow-lg">
              <button onClick={handleBackToTasks} className="flex items-center text-indigo-600 hover:text-indigo-800 mb-4 transition">
                <ChevronLeft className="w-5 h-5 mr-1" /> Back to Task List
              </button>
              <h2 className="text-2xl font-bold mb-6 text-gray-800 border-b pb-2">{selectedTask.title}</h2>
              
              {qIndex === 0 ? (
                // Task Instruction/Finish View
                <div className="text-center p-8 border-2 border-dashed border-gray-300 rounded-xl">
                    <p className="text-lg text-gray-600 mb-6">
                        Complete the required work for **{selectedTask.title}** (e.g., code, report draft). When finished, click the button below to answer the post-task questions generated by the AI Model.
                    </p>
                    <button
                        onClick={handleFinishTask}
                        className="bg-green-600 text-white font-semibold px-8 py-3 rounded-xl shadow-lg hover:bg-green-700 transition transform hover:scale-105"
                    >
                        Task Finished - Start Q&A
                    </button>
                </div>
              ) : (
                // Question and Answer View
                <div className="space-y-4">
                    <div className="p-4 bg-indigo-50 rounded-lg">
                        <p className="text-sm text-indigo-600 font-medium">Question {qIndex} of {selectedTask.questions.length}</p>
                        <p className="text-xl font-semibold mt-1 text-gray-900">
                            {selectedTask.questions[qIndex - 1]}
                        </p>
                    </div>
                    
                    <textarea
                        className={`border p-3 w-full h-32 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition ${taskError ? 'border-red-500' : 'border-gray-300'}`}
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Type your answer here..."
                    ></textarea>
                    
                    {taskError && <p className="text-red-500 text-sm font-medium bg-red-100 p-2 rounded">SYSTEM ERROR: {taskError}</p>}
                    
                    <div className="flex justify-end space-x-3">
                        <button
                          onClick={handleBackToTasks}
                          className="bg-gray-500 text-white px-5 py-2 rounded-lg hover:bg-gray-600 transition"
                        >
                          Cancel
                        </button>
                        <button
                          className="bg-indigo-600 text-white px-5 py-2 rounded-lg hover:bg-indigo-700 transition"
                          onClick={handleQuestionSubmit}
                        >
                          {qIndex < selectedTask.questions.length ? "Next Question" : "Submit & Complete"}
                        </button>
                    </div>
                </div>
              )}
            </div>
          );
        }

      case "chat":
        return (
          <ChatSection 
            messages={chatMessages} 
            input={chatInput} 
            setInput={setChatInput} 
            sendMessage={handleSendChat} 
          />
        );
        
      case "chatbot":
        return (
            <ChatbotSection 
                messages={botMessages} 
                input={botInput} 
                setInput={setBotInput} 
                handleSubmit={handleBotSubmit} 
                isLoading={isBotLoading}
            />
        );

      case "upload":
        return (
          <FileUploadSection 
            files={uploadedFiles} 
            handleFileUpload={handleFileUpload} 
            handleDeleteFile={handleDeleteFile}
            handleDownloadFile={handleDownloadFile} // Pass the new download handler
          />
        );

      case "review":
        return (
          <ReviewSection 
            tasks={taskData} 
          />
        );

      case "performance":
        return (
          <PerformanceSection />
        );

      default:
        return <h2 className="text-xl font-bold text-red-500">404 - Section Not Found</h2>;
    }
  };


  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-xl p-5 space-y-4 border-r border-gray-200">
        <h2 className="text-2xl font-extrabold text-indigo-700 mb-6 border-b pb-2">Project Navigator</h2>
        <nav className="space-y-2">
          {menuItems.map((item) => (
            <button
              key={item.name}
              onClick={() => {
                setActiveSection(item.section);
                setSelectedTask(null); 
              }}
              className={`flex items-center space-x-3 w-full p-3 rounded-xl text-left transition duration-200 ${
                activeSection === item.section
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 p-8 overflow-y-auto">
        {renderSection()}
      </div>

      {showCompletionModal && (
        <CompletionModal
          message="Task questions successfully submitted! The AI Review is now being generated."
          onClose={() => setShowCompletionModal(false)}
        />
      )}
    </div>
  );
}


// --- Component Helpers for Clean Rendering ---

const InfoCard = ({ title, value, color, icon: Icon }) => (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
        <div className="flex items-center space-x-2 mb-1">
            <Icon className={`w-5 h-5 ${color}`} />
            <p className="text-sm font-medium text-gray-500">{title}</p>
        </div>
        <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
);


const ChatSection = ({ messages, input, setInput, sendMessage }) => (
    <div className="flex flex-col h-[85vh] bg-white rounded-xl shadow-lg overflow-hidden">
        <header className="p-4 bg-indigo-600 text-white text-xl font-bold border-b">Team Chat</header>
        
        {/* Messages Container */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto">
            {messages.map((msg) => (
                <div 
                    key={msg.id} 
                    className={`flex ${msg.user === "You" ? 'justify-end' : 'justify-start'}`}
                >
                    <div className={`max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-xl shadow-md ${
                        msg.user === "You" 
                            ? 'bg-indigo-500 text-white rounded-br-none' 
                            : 'bg-gray-200 text-gray-800 rounded-tl-none'
                    }`}>
                        <p className="font-semibold text-sm mb-1">{msg.user}</p>
                        <p className="text-base">{msg.text}</p>
                        <span className="block text-xs text-opacity-80 mt-1 text-right">{msg.timestamp}</span>
                    </div>
                </div>
            ))}
        </div>
        
        {/* Input Area */}
        <div className="p-4 border-t bg-gray-50">
            <div className="flex space-x-3">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="flex-1 border border-gray-300 p-3 rounded-full focus:ring-indigo-500 focus:border-indigo-500 transition"
                />
                <button
                    onClick={sendMessage}
                    className="bg-indigo-600 text-white p-3 rounded-full hover:bg-indigo-700 transition"
                >
                    <Send className="w-6 h-6" />
                </button>
            </div>
        </div>
    </div>
);


const ChatbotSection = ({ messages, input, setInput, handleSubmit, isLoading }) => (
    <div className="flex flex-col h-[85vh] bg-white rounded-xl shadow-lg overflow-hidden">
        <header className="p-4 bg-purple-600 text-white text-xl font-bold border-b">Project Assistant Chatbot (Powered by Gemini)</header>
        
        {/* Messages Container */}
        <div className="flex-1 p-6 space-y-4 overflow-y-auto">
            {messages.length === 0 && (
                <div className="text-center p-8 text-gray-500">
                    <p className="mb-2">Ask the AI Model for advice, definitions, or project guidance!</p>
                    <p className="font-semibold">Example: "What are best practices for React state management?"</p>
                </div>
            )}
            {messages.map((msg, index) => (
                <div 
                    key={index} 
                    className={`flex ${msg.sender === "user" ? 'justify-end' : 'justify-start'}`}
                >
                    <div className={`max-w-md p-3 rounded-xl shadow-md ${
                        msg.sender === "user" 
                            ? 'bg-purple-100 text-gray-800 rounded-br-none' 
                            : 'bg-purple-600 text-white rounded-tl-none'
                    }`}>
                        <p className="font-semibold text-xs mb-1">
                          {msg.sender === "user" ? "You" : "Assistant"}
                        </p>
                        <p className="text-base">{msg.text}</p>
                    </div>
                </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                  <div className="max-w-md p-3 rounded-xl bg-purple-600 text-white rounded-tl-none">
                      <div className="flex space-x-2 items-center">
                          <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-100"></div>
                          <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-200"></div>
                          <div className="w-3 h-3 bg-white rounded-full animate-bounce delay-300"></div>
                          <span className="ml-2 text-sm">Thinking...</span>
                      </div>
                  </div>
              </div>
            )}
        </div>
        
        {/* Input Area */}
        <div className="p-4 border-t bg-gray-50">
            <div className="flex space-x-3">
                <input
                    type="text"
                    placeholder="Ask a question..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                    className="flex-1 border border-gray-300 p-3 rounded-full focus:ring-purple-500 focus:border-purple-500 transition"
                    disabled={isLoading}
                />
                <button
                    onClick={handleSubmit}
                    className="bg-purple-600 text-white p-3 rounded-full hover:bg-purple-700 transition disabled:opacity-50"
                    disabled={isLoading}
                >
                    <Send className="w-6 h-6" />
                </button>
            </div>
        </div>
    </div>
);


const FileUploadSection = ({ files, handleFileUpload, handleDeleteFile, handleDownloadFile }) => (
    <div className="p-8 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Project Documentation & Files</h1>
        
        {/* Upload Button */}
        <div className="mb-8 border-2 border-dashed border-orange-400 bg-orange-50 rounded-xl p-8 text-center">
            <Paperclip className="w-10 h-10 text-orange-500 mx-auto mb-3" />
            <p className="text-gray-700 mb-4">Drag and drop files here, or click to browse. **Files should be uploaded to GitHub first.**</p>
            <label htmlFor="file-upload" className="cursor-pointer">
                <span className="bg-orange-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-orange-600 transition shadow-md">
                    <PlusCircle className="w-5 h-5 inline mr-2" /> Upload New File
                </span>
                <input
                    id="file-upload"
                    type="file"
                    multiple
                    onChange={handleFileUpload}
                    className="hidden"
                />
            </label>
            <div className="mt-4 text-sm text-gray-600 flex items-center justify-center">
                <GitBranch className="w-4 h-4 mr-2" /> 
                <a href="#" className="underline font-medium hover:text-indigo-600">Clone GitHub Repo (Link Placeholder)</a>
            </div>
        </div>

        {/* File List */}
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">Uploaded Files ({files.length})</h2>
        <div className="border border-gray-200 rounded-xl overflow-hidden">
            <div className="grid grid-cols-5 p-4 bg-gray-100 font-bold text-sm text-gray-600 border-b">
                <div>File Name</div>
                <div>Size</div>
                <div>Date Added</div>
                <div>GitHub Link</div>
                <div>Actions</div>
            </div>
            {files.map((file) => (
                <div key={file.id} className="grid grid-cols-5 p-4 border-b last:border-b-0 hover:bg-gray-50 transition">
                    <div className="font-medium text-indigo-600 truncate">{file.name}</div>
                    <div className="text-sm text-gray-500">{file.size}</div>
                    <div className="text-sm text-gray-500">{file.date}</div>
                    <div className="text-sm">
                        <a href={file.repoLink} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline truncate">{file.repoLink.split('/').pop()}</a>
                    </div>
                    <div>
                        <button 
                            onClick={() => handleDownloadFile(file.name)} // Added onClick handler for download
                            className="text-sm text-green-600 hover:underline"
                        >
                            Download
                        </button>
                        <button 
                            onClick={() => handleDeleteFile(file.id)} // Added onClick handler for deletion
                            className="text-sm text-red-600 hover:underline ml-3"
                        >
                            Delete
                        </button>
                    </div>
                </div>
            ))}
        </div>
    </div>
);

const ReviewCard = ({ title, status, score, children, icon: Icon, color }) => (
    <div className={`p-6 rounded-xl shadow-lg border-l-4 ${color.border} bg-white`}>
        <div className="flex justify-between items-center mb-3">
            <div className="flex items-center space-x-2">
                <Icon className={`w-6 h-6 ${color.icon}`} />
                <h3 className="text-xl font-bold text-gray-800">{title}</h3>
            </div>
            <span className={`px-3 py-1 text-sm font-semibold rounded-full ${color.bg} ${color.text}`}>
                {status}
            </span>
        </div>
        {score && <p className="text-lg font-semibold mb-2">Score: <span className="font-extrabold text-2xl">{score}</span> / 100</p>}
        <p className="text-gray-600">{children}</p>
    </div>
);

const ReviewSection = ({ tasks }) => {
    const aiReviewStatus = tasks.some(t => t.completed) ? 'Pending' : 'No Tasks Completed';
    const teammateReviewStatus = 'Pending Teammates';

    return (
        <div className="p-8 bg-gray-50 rounded-xl shadow-lg">
            <h1 className="text-3xl font-extrabold text-gray-800 mb-6">Reviews & Feedback</h1>

            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-indigo-700 border-b pb-2">Review by AI Model (After Each Task)</h2>
                
                <ReviewCard 
                    title="AI Code Metrics Report"
                    status={aiReviewStatus}
                    score="78"
                    icon={Cpu}
                    color={{ border: 'border-purple-500', icon: 'text-purple-600', bg: 'bg-purple-100', text: 'text-purple-800' }}
                >
                    Analysis of uploaded code structure, performance efficiency, and adherence to project protocols.
                </ReviewCard>

                <ReviewCard 
                    title="AI Knowledge Debrief Analysis"
                    status={aiReviewStatus}
                    score="85"
                    icon={CheckCircle}
                    color={{ border: 'border-green-500', icon: 'text-green-600', bg: 'bg-green-100', text: 'text-green-800' }}
                >
                    Evaluation of submitted Q&A logs for completeness, comprehension, and tactical relevance.
                </ReviewCard>
                
                <h2 className="text-2xl font-bold text-indigo-700 border-b pb-2 pt-6">PEER-TO-PEER EVALUATION</h2>
                
                <ReviewCard 
                    title="Teammate Implementation Report"
                    status={teammateReviewStatus}
                    score="N/A"
                    icon={CornerUpLeft}
                    color={{ border: 'border-yellow-500', icon: 'text-yellow-600', bg: 'bg-yellow-100', text: 'text-yellow-800' }}
                >
                    Colleague assessment of completed task implementation, logic, and collaborative contributions.
                </ReviewCard>

                 <ReviewCard 
                    title="Teammate Contribution Rating"
                    status={teammateReviewStatus}
                    score="N/A"
                    icon={TrendingUp}
                    color={{ border: 'border-blue-500', icon: 'text-blue-600', bg: 'bg-blue-100', text: 'text-blue-800' }}
                >
                    Quantitative scoring by peers on effort, quality, and commitment per objective.
                </ReviewCard>
                
            </div>
            
        </div>
    );
};

const PerformanceSection = () => {
    return (
        <div className="p-8 bg-white rounded-xl shadow-lg">
            <h1 className="text-3xl font-extrabold text-gray-800 mb-6">Project Performance Report</h1>

            <div className="space-y-6">
                <div className="p-6 bg-indigo-50 rounded-xl border border-indigo-200">
                    <h2 className="text-2xl font-bold text-indigo-800 mb-3">XP Points & Level Calculation</h2>
                    <p className="text-gray-700 mb-4">
                        All previous review details (AI scores, Teammate ratings) are considered here to calculate your **Experience Points (XP)** and determine your **User Level**.
                    </p>
                    <div className="flex justify-around text-center mt-6">
                        <div>
                            <p className="text-5xl font-extrabold text-green-600">1250 XP</p>
                            <p className="text-gray-500">Total Experience Points</p>
                        </div>
                        <div>
                            <p className="text-5xl font-extrabold text-blue-600">LEVEL 3</p>
                            <p className="text-gray-500">Current User Level</p>
                        </div>
                    </div>
                </div>

                <div className="p-6 bg-yellow-50 rounded-xl border border-yellow-200 text-center">
                    <h2 className="text-2xl font-bold text-yellow-800 mb-3 flex items-center justify-center space-x-3">
                        <Trophy className="w-6 h-6" /> 
                        <span>Achievement Certificate</span>
                    </h2>
                    <p className="text-lg font-semibold text-gray-700">
                        Based on your performance and current level, you have earned the "Project Architect" Certificate.
                    </p>
                    <button className="mt-4 bg-yellow-500 text-white font-semibold px-6 py-2 rounded-lg hover:bg-yellow-600 transition">
                        Download Certificate
                    </button>
                </div>
            </div>
        </div>
    );
};