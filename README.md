# 🏛️ Spartacus Desktop

**Your Personal AI Assistant - Claude Desktop Alternative**

Spartacus Desktop is a modern, desktop AI assistant application that combines the power of your own agentic AI library with a beautiful, user-friendly interface. Built with Python FastAPI backend and Electron + React frontend.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## ✨ Features

### 🤖 Multi-Agent System
- **Default Agent**: General purpose conversational AI
- **Coding Agent**: Programming and development assistance
- **Research Agent**: Information gathering and analysis
- **Analysis Agent**: Data analysis and insights
- **Creative Agent**: Writing and brainstorming

### 🎨 Modern Interface
- **Clean Design**: Inspired by Claude Desktop with modern UI/UX
- **Dark/Light Mode**: Automatic theme switching
- **Real-time Chat**: WebSocket-powered instant messaging
- **Markdown Support**: Rich text formatting with syntax highlighting
- **Responsive Layout**: Adapts to different window sizes

### 🔧 Technical Features
- **FastAPI Backend**: High-performance Python API
- **Electron Frontend**: Cross-platform desktop application
- **agentic_lib Integration**: Your own AI agent library
- **Session Management**: Persistent chat history
- **Tool Execution**: Integrated tools and utilities
- **RESTful API**: Full REST API with OpenAPI documentation

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **npm or yarn**

### 1. Clone & Setup
```bash
git clone <repository>
cd spartacus
source activate.sh  # Sets up Python environment
pip install -r requirements.txt
```

### 2. Start the Application
```bash
# Easy way - starts both backend and frontend
python scripts/start_spartacus.py

# Manual way - separate terminals
# Terminal 1: Backend
python spartacus_backend/start_backend.py

# Terminal 2: Frontend (requires Node.js)
cd spartacus_frontend
npm install
npm run dev
```

### 3. Access the Application
- **Desktop App**: Electron window opens automatically
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://127.0.0.1:8000/docs

---

## 📁 Project Structure

```
spartacus/
├── 🐍 agentic_lib/              # Core AI agent library
│   ├── base_agent.py            # Base agent implementation
│   ├── tools/                   # Agent tools and utilities
│   └── context/                 # Context management
│
├── 🔧 spartacus_services/       # Shared services
│   ├── context.py              # Context handling
│   ├── logger.py               # Structured logging
│   └── tool_base.py            # Tool base classes
│
├── 🌐 spartacus_backend/        # FastAPI Backend
│   ├── main.py                 # FastAPI application
│   ├── api/                    # API endpoints
│   ├── services/               # Business logic
│   ├── models/                 # Pydantic models
│   └── config/                 # Configuration
│
├── 🖥️ spartacus_frontend/       # Electron + React Frontend
│   ├── src/
│   │   ├── main/               # Electron main process
│   │   ├── preload/            # Preload scripts
│   │   ├── App.tsx             # React application
│   │   └── main.tsx            # React entry point
│   ├── package.json            # Node.js dependencies
│   └── tsconfig.json           # TypeScript config
│
├── 🧪 scripts/                  # Utility scripts
│   ├── start_spartacus.py      # Combined launcher
│   └── test_backend.py         # Backend tests
│
├── 📖 llm_clients/              # LLM client implementations
├── 📝 doc_agent/                # Documentation and reports
└── 📋 requirements.txt          # Python dependencies
```

---

## 🔌 API Endpoints

### Chat & Messaging
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/{session_id}` - Get chat history
- `WS /api/chat/stream` - WebSocket streaming

### Agent Management
- `POST /api/agents/run` - Execute agent
- `GET /api/agents/list` - List available agents
- `POST /api/agents/create` - Create custom agent

### Tools & Utilities
- `GET /api/tools/list` - List available tools
- `POST /api/tools/execute` - Execute tool

### System Management
- `GET /api/system/status` - System status
- `GET /api/system/health` - Health check
- `GET /api/system/config` - Configuration

---

## 🛠️ Development

### Backend Development
```bash
# Start backend with auto-reload
python spartacus_backend/start_backend.py --reload

# Run backend tests
python scripts/test_backend.py

# Check API documentation
open http://127.0.0.1:8000/docs
```

### Frontend Development
```bash
cd spartacus_frontend

# Install dependencies
npm install

# Start development server
npm run dev:react

# Start Electron in development
npm run dev:electron

# Build for production
npm run build
```

### Testing
```bash
# Backend tests
python scripts/test_backend.py

# Frontend tests (when added)
cd spartacus_frontend
npm test
```

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Server Configuration
SPARTACUS_HOST=127.0.0.1
SPARTACUS_PORT=8000
SPARTACUS_RELOAD=true

# LLM Configuration
SPARTACUS_DEFAULT_MODEL=gpt-4
SPARTACUS_TEMPERATURE=0.7
SPARTACUS_MAX_TOKENS=4000

# Paths
SPARTACUS_DATA_DIR=./data
SPARTACUS_LOGS_DIR=./logs
```

### Agent Configuration
Agents can be configured in `spartacus_backend/config/settings.py`:

```python
# Maximum number of concurrent agents
max_agents: int = 10

# Agent timeout in seconds
agent_timeout: int = 300

# Maximum chat history length
max_chat_history: int = 100
```

---

## 🎯 Use Cases

### 💻 Development Assistant
- Code review and debugging
- Architecture suggestions
- Documentation generation
- Test creation

### 📊 Data Analysis
- Data exploration and visualization
- Statistical analysis
- Report generation
- Insights extraction

### 🔍 Research Assistant
- Information gathering
- Source verification
- Summary generation
- Fact checking

### ✍️ Creative Writing
- Content creation
- Brainstorming sessions
- Editing and proofreading
- Creative ideation

---

## 🔒 Security

### Data Privacy
- **Local Processing**: All data stays on your machine
- **No External Dependencies**: Uses your own AI models
- **Secure Communication**: HTTPS/WSS in production
- **Context Isolation**: Isolated agent contexts

### Best Practices
- Regular security updates
- Input validation and sanitization
- Secure configuration management
- Audit logging

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Code Style
- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Use ESLint and Prettier
- **Git**: Conventional commit messages

### Testing
- Write tests for new features
- Ensure all tests pass
- Maintain test coverage

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Acknowledgments

- **FastAPI** - For the excellent Python web framework
- **Electron** - For cross-platform desktop app capabilities
- **React** - For the modern UI framework
- **Tailwind CSS** - For beautiful styling
- **Claude AI** - For inspiration on the interface design

---

## 🆘 Support

### Getting Help
- 📖 **Documentation**: Check this README and code comments
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Join GitHub Discussions for questions

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Check logs
python spartacus_backend/start_backend.py --log-level DEBUG
```

**Frontend won't build:**
```bash
# Clear node modules
rm -rf spartacus_frontend/node_modules
cd spartacus_frontend
npm install

# Check Node version
node --version  # Should be 18+
```

**API Connection Issues:**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify CORS configuration

---

## 🚀 What's Next?

### Roadmap
- [ ] **Plugin System**: Custom tool integration
- [ ] **Multiple LLM Support**: Support for different AI models
- [ ] **Advanced UI**: More sophisticated interface features
- [ ] **Mobile App**: React Native mobile version
- [ ] **Cloud Sync**: Optional cloud synchronization
- [ ] **Voice Interface**: Speech-to-text integration

### Vision
Spartacus Desktop aims to be the definitive personal AI assistant platform, providing a seamless bridge between cutting-edge AI capabilities and everyday productivity needs.

---

**Made with ❤️ by the Spartacus Team**
