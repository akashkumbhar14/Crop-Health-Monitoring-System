# Crop-Health-Monitoring-System
**Smart Crop Health Monitoring System** is an AI-powered platform that uses satellite imagery and NDVI analysis to detect early crop stress such as nutrient deficiency, water stress, and pests. It provides personalized, local-language advisories via SMS, enabling timely decisions, improved yield, and sustainable farming.

npx expo start // start the application

Crop-Health-Monitoring-System/
│
├── 📁 Backend/
│   ├── 📁 config/
│   │   ├── db.js                 # MongoDB connection
│   │   ├── env.js                # Environment config
│   │
│   ├── 📁 controllers/
│   │   ├── authController.js
│   │   ├── farmerController.js
│   │   ├── cropController.js
│   │   └── advisoryController.js
│   │
│   ├── 📁 models/
│   │   ├── User.js
│   │   ├── Farm.js
│   │   ├── NDVI.js
│   │   └── Advisory.js
│   │
│   ├── 📁 routes/
│   │   ├── authRoutes.js
│   │   ├── farmerRoutes.js
│   │   ├── cropRoutes.js
│   │   └── advisoryRoutes.js
│   │
│   ├── 📁 services/
│   │   ├── ndviService.js        # NDVI + AI logic
│   │   ├── smsService.js         # SMS gateway logic
│   │   └── satelliteService.js   # GEE / Sentinel APIs
│   │
│   ├── 📁 middlewares/
│   │   ├── authMiddleware.js
│   │   └── errorMiddleware.js
│   │
│   ├── 📁 utils/
│   │   ├── logger.js
│   │   └── helpers.js
│   │
│   ├── server.js                 # App entry point
│   ├── package.json
│   ├── .env
│   └── README.md
│
├── 📁 Frontend/
│   └── 📁 CropHealthApp/
│       ├── 📁 app/               # Expo Router pages
│       │   ├── index.js           # Blank / splash screen
│       │   ├── home.js
│       │   ├── login.js
│       │   ├── register.js
│       │   └── profile.js
│       │
│       ├── 📁 src/
│       │   ├── 📁 components/
│       │   │   ├── CustomButton.js
│       │   │   ├── Header.js
│       │   │   └── Loader.js
│       │   │
│       │   ├── 📁 screens/        # Optional (non-router)
│       │   │   └── NotificationScreen.js
│       │   │
│       │   ├── 📁 services/
│       │   │   ├── api.js         # Axios config
│       │   │   ├── authService.js
│       │   │   └── farmerService.js
│       │   │
│       ├── 📁 config/
│       │   ├── api.js             # Backend base URL
│       │   └── theme.js
│       │
│       ├── 📁 assets/
│       │   ├── images/
│       │   └── icons/
│       │
│       ├── 📁 constants/
│       │   └── colors.js
│       │
│       ├── App.tsx
│       ├── package.json
│       └── README.md
│
├── 📁 Docs/
│   ├── SRS.pdf
│   ├── Architecture.png
│   └── Diagrams/
│
├── 📁 .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
└── README.md
