# GenoScope React Frontend - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (Vite default port)

3. **Build for production:**
```bash
npm run build
```

## 🔌 Backend Connection

The frontend is now configured to connect to your FastAPI backend at:
- **Default URL:** `http://localhost:8000`
- **Configure via:** `.env` file (VITE_API_URL)

### API Endpoints Used:
- `GET /health` - Health check
- `POST /predict/` - File upload and prediction
- `POST /analyze-sequence/` - Direct sequence analysis
- `GET /models/info/` - Get model information
- `POST /train-demo/` - Train demo models

## 📁 File Structure

```
src/
├── components/
│   ├── LoginPage.tsx          # Login page
│   ├── SignupPage.tsx         # Registration page
│   ├── DashboardPage.tsx      # Main dashboard
│   ├── UploadPage.tsx         # File upload (✅ CONNECTED TO BACKEND)
│   ├── ReportPage.tsx         # Analysis results
│   ├── Navigation.tsx         # Navigation bar
│   ├── api/
│   │   ├── api.tsx            # ✅ NEW: Real API client (connects to FastAPI)
│   │   └── mockApi.tsx        # ❌ OLD: Mock API (not used)
│   ├── hooks/
│   │   └── useAuth.tsx        # Authentication hook
│   └── ui/                    # shadcn/ui components (47 files)
├── App.tsx                    # Main app
└── main.tsx                   # Entry point
```

## ✅ What's Changed

### 1. **New API Client** (`src/components/api/api.tsx`)
- Connects to FastAPI backend
- Real file upload to backend
- Real prediction from ML models
- Health check functionality

### 2. **Updated UploadPage**
- Now accepts `.fasta`, `.fa`, and `.csv` files
- Sends files to FastAPI `/predict/` endpoint
- Displays real prediction results
- Stores results in localStorage

### 3. **Environment Configuration**
- `.env` file for API URL configuration
- Easy to switch between local/production

## 🧪 Testing the Connection

### 1. Start Backend:
```bash
cd src/backend
python run_app.py
```
Backend should be running at `http://localhost:8000`

### 2. Start Frontend:
```bash
npm run dev
```
Frontend should be running at `http://localhost:5173`

### 3. Test Upload:
1. Go to Upload page
2. Upload a `.fasta` or `.csv` file
3. Click "Run Prediction"
4. Check Report page for results

## 📋 Supported File Formats

### FASTA Format (.fasta, .fa):
```
>sequence_name
ATCGATCGATCG...
```

### CSV Format (.csv):
Must have a column named: `sequence`, `dna_sequence`, or `genetic_sequence`
```csv
id,sequence,description
1,ATCGATCGATCG,Sample sequence
```

## 🔧 Backend Requirements

Make sure your FastAPI backend is running with:
- ✅ CORS enabled for frontend origin
- ✅ Models loaded (sickle_cell, breast_cancer)
- ✅ All required dependencies installed

### Backend CORS Configuration
The backend should allow requests from `http://localhost:5173`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎨 Features

- ✅ Modern React 18 + TypeScript
- ✅ Vite for fast development
- ✅ shadcn/ui components (47 premium components)
- ✅ Tailwind CSS styling
- ✅ Dark/Light mode support
- ✅ Toast notifications (Sonner)
- ✅ Charts and graphs (Recharts)
- ✅ Real-time backend connection
- ✅ File upload with preview
- ✅ Prediction results display

## 🚨 Troubleshooting

### "Backend not responding" error:
1. Check if backend is running: `http://localhost:8000/health`
2. Check CORS configuration in backend
3. Verify `.env` file has correct API URL

### File upload fails:
1. Check file format (.fasta, .fa, or .csv)
2. Ensure file has valid sequence data
3. Check file size (max 5MB)

### Prediction takes too long:
- Models might be training on first run
- Check backend logs for errors
- Ensure models are loaded successfully

## 📦 Dependencies

Key packages:
- `react` 18.3.1
- `vite` 6.3.5
- `@radix-ui/*` - Accessible components
- `lucide-react` - Icons
- `recharts` - Charts
- `sonner` - Toast notifications
- `tailwindcss` - Styling

## 🔄 Migrating from Old Frontend

The old frontend files (`src/frontend/` with vanilla JS) are still there but not used. The new React frontend is in `src/` and `src/components/`.

**Old Frontend (Not Used):**
- ❌ `src/frontend/index.html`
- ❌ `src/frontend/app.js`
- ❌ `src/frontend/enhanced-app.js`

**New Frontend (Active):**
- ✅ `src/App.tsx`
- ✅ `src/components/*`
- ✅ Modern React + TypeScript

## 📝 Next Steps

1. ✅ Backend connection complete
2. ⏳ Add real authentication
3. ⏳ Implement PDF report generation
4. ⏳ Add prediction history from backend
5. ⏳ Deploy to production

## 🎯 Production Deployment

When deploying:

1. Update `.env` with production API URL:
```bash
VITE_API_URL=https://your-backend-api.com
```

2. Build the frontend:
```bash
npm run build
```

3. Deploy the `dist/` folder to your hosting service (Vercel, Netlify, etc.)

4. Update backend CORS to allow your production frontend URL

---

**Status:** ✅ Frontend successfully connected to FastAPI backend!

**Last Updated:** October 31, 2025
