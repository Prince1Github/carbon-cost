# 🌱 Carbon-Cost

A comprehensive full-stack solution that estimates the carbon footprint of CI/CD workflows and promotes sustainable development practices. Built with TypeScript, Flask, and Streamlit.

## 🎯 Features

- **GitHub Action**: Automatically estimates CO₂ emissions from CI/CD runs
- **Dynamic Badges**: Shows Green/Yellow/Red status based on emissions thresholds
- **Flask Backend**: Stores emission data and provides analytics API
- **Streamlit Dashboard**: Visualizes emissions trends and team performance
- **Docker Support**: Containerized deployment for easy setup
- **Real-time Updates**: Dynamic badges that update automatically
- **Data Simulation**: Generate sample data to test and demonstrate trends

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Carbon-Cost    │───▶│   Flask Backend │
│   (CI/CD Run)   │    │   Action        │    │   (SQLite DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Badge URL     │    │ Streamlit       │
                       │   (Shields.io)  │    │ Dashboard       │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+
- Docker & Docker Compose (optional)

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd carbon-cost
   ```

2. **Start the Flask Backend**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   python app.py
   ```

3. **Start the Streamlit Dashboard**
   ```bash
   cd dashboard
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. **Build the GitHub Action**
   ```bash
   cd action
   npm install
   npm run build
   ```

### Option 2: Docker Deployment

```bash
# Start both backend and dashboard
docker-compose up --build

# Access the services
# Backend: http://localhost:5000
# Dashboard: http://localhost:8501
```

## 📊 Usage

### GitHub Action Setup

1. **Add the action to your workflow**
   ```yaml
   name: Carbon-Cost CI
   
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]
   
   jobs:
     carbon-cost:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Run Carbon-Cost Action
           uses: ./action
           with:
             backend_url: 'http://your-backend-url:5000/record'
   ```

2. **The action will:**
   - Estimate CO₂ emissions based on job duration and machine type
   - Determine badge color (Green/Yellow/Red)
   - Send data to your backend
   - Output badge URL for display

### Dynamic Badge Integration

Add this to your README for automatic badge updates:

```markdown
![Carbon Badge](https://img.shields.io/endpoint?url=https://your-api.com/latest_co2_badge)
```

The badge automatically updates after each CI/CD run, showing the latest emission status.

### Dashboard Features

- **Real-time Metrics**: Total CO₂, average per build, build counts
- **Visualizations**: 
  - Pie chart of Green/Yellow/Red builds
  - Line chart of emissions over time
  - Bar chart by machine type
- **Filtering**: Date range selection
- **Recent Builds**: Table of latest CI/CD runs

## 🔧 Configuration

### CO₂ Estimation Factors

The action uses these factors (kg CO₂ per second):
- `ubuntu-latest`: 0.0002
- `windows-latest`: 0.0003  
- `macos-latest`: 0.00025

### Badge Thresholds

- **Green**: < 0.5 kg CO₂
- **Yellow**: 0.5 - 1.5 kg CO₂
- **Red**: > 1.5 kg CO₂

## 📈 API Endpoints

### POST /record
Record a new emission:
```json
{
  "repo": "my-repo",
  "owner": "username",
  "run_id": "123456789",
  "co2": 0.75,
  "duration": 300,
  "machine_type": "ubuntu-latest",
  "badge": "Yellow",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /stats
Get emission statistics:
```json
{
  "total_co2": 15.5,
  "average_co2": 0.775,
  "badge_counts": {
    "Green": 10,
    "Yellow": 8,
    "Red": 2
  },
  "emissions": [...]
}
```

### GET /latest_co2_badge
Get latest badge data for Shields.io:
```json
{
  "schemaVersion": 1,
  "label": "CO2",
  "message": "Green",
  "color": "brightgreen"
}
```

## 🧪 Testing

### Generate Sample Data

Use the simulation script to generate realistic test data:

```bash
# Generate 20 sample runs
python simulate_runs.py

# Or run with custom parameters
python simulate_runs.py
# Enter number of runs: 50
# Enter delay: 0.2
```

This will create sample data across multiple repositories and machine types, allowing you to see trends in the dashboard.

### Test the Backend
```bash
# Test the /record endpoint
curl -X POST http://localhost:5000/record \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "test-repo",
    "owner": "test-user",
    "run_id": "123",
    "co2": 0.5,
    "duration": 300,
    "machine_type": "ubuntu-latest",
    "badge": "Green",
    "timestamp": "2024-01-15T10:30:00Z"
  }'

# Test the /stats endpoint
curl http://localhost:5000/stats

# Test the badge endpoint
curl http://localhost:5000/latest_co2_badge
```

### Test the Action Locally
```bash
cd action
npm run build
$env:INPUT_BACKEND_URL="http://localhost:5000/record"
$env:GITHUB_REPOSITORY="test-user/test-repo"
$env:GITHUB_RUN_ID="123"
$env:GITHUB_REPOSITORY_OWNER="test-user"
node dist/index.js
```

## 🐳 Docker Commands

```bash
# Build and start services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
```

## 📁 Project Structure

```
carbon-cost/
├── action/                 # GitHub Action (TypeScript)
│   ├── src/
│   │   └── index.ts       # Main action logic
│   ├── dist/              # Compiled JavaScript
│   ├── action.yml         # Action metadata
│   ├── package.json       # Dependencies
│   └── tsconfig.json      # TypeScript config
├── backend/               # Flask Backend
│   ├── app.py            # Main Flask app
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container config
├── dashboard/            # Streamlit Dashboard
│   ├── app.py           # Dashboard app
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Container config
├── .github/
│   └── workflows/
│       └── test.yml     # Example workflow
├── docker-compose.yml   # Multi-service orchestration
├── simulate_runs.py     # Data simulation script
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Shields.io](https://shields.io/) for badge generation
- [GitHub Actions](https://github.com/features/actions) for CI/CD integration
- [Streamlit](https://streamlit.io/) for the dashboard framework
- [Flask](https://flask.palletsprojects.com/) for the backend API

---

**Made with ❤️ for a greener future in software development** 