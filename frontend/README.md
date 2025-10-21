# PrivAI Frontend

A modern React + TypeScript frontend for PrivAI, a privacy-first AI application for college data processing.

## Features

### 🎨 **Modern UI/UX**
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for responsive, modern styling
- **Lucide React** for beautiful icons
- **Responsive Design** that works on all devices
- **Dark/Light Mode** support (ready for implementation)

### 📱 **Pages & Components**
- **Upload Page**: File upload and database connection
- **Ingestion Page**: Data processing and chunk creation
- **Chat Page**: AI-powered question answering
- **Privacy Indicator**: Always visible privacy protection notice
- **Reusable Components**: Button, Input, Card, Alert, etc.

### 🔧 **Key Features**
- **File Upload**: Drag & drop support for PDF, CSV, DOCX
- **Database Integration**: Connect to various database types
- **Real-time Processing**: Live progress tracking
- **AI Chat Interface**: Interactive Q&A with source references
- **Source Attribution**: Track and display document sources
- **Export Functionality**: Download chat history
- **Sample Data**: Load demo data for testing

### 🛡️ **Privacy-First Design**
- **Local Processing**: All data stays on your machine
- **No Cloud Calls**: Complete privacy protection
- **Source Tracking**: Full transparency in AI responses
- **Data Control**: Clear and delete your data anytime

## Quick Start

### 1. Install Dependencies
```bash
cd E:\Nagendra\projects\PrivAI\privai-app\frontend
npm install
```

### 2. Start Development Server
```bash
npm start
```

### 3. Open in Browser
Navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Alert.tsx
│   │   ├── FileUpload.tsx
│   │   ├── ChatMessage.tsx
│   │   └── PrivacyIndicator.tsx
│   ├── pages/               # Main page components
│   │   ├── UploadPage.tsx
│   │   ├── IngestionPage.tsx
│   │   └── ChatPage.tsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useAppState.ts
│   │   └── useApi.ts
│   ├── utils/               # Utility functions
│   │   ├── api.ts
│   │   └── helpers.ts
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── App.tsx              # Main app component
│   ├── index.tsx            # App entry point
│   └── index.css            # Global styles with Tailwind
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Dependencies

### Core Dependencies
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling framework
- **Lucide React** - Icon library
- **Axios** - HTTP client
- **React Router DOM** - Navigation

### Development Dependencies
- **Create React App** - Build tooling
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixes

## API Integration

The frontend integrates with the PrivAI backend API:

- **Base URL**: `http://localhost:8000` (configurable via environment)
- **Endpoints**: Upload, Database, Ingestion, Chat
- **Error Handling**: Comprehensive error management
- **Loading States**: User feedback during API calls

## Styling

### Tailwind CSS Configuration
- **Custom Colors**: Primary, Secondary, Success, Warning, Error
- **Custom Fonts**: Inter (sans), JetBrains Mono (mono)
- **Custom Animations**: Fade-in, slide-up, pulse
- **Component Classes**: Pre-built component styles

### Design System
- **Consistent Spacing**: 4px base unit
- **Color Palette**: Semantic color system
- **Typography**: Hierarchical text styles
- **Components**: Reusable UI patterns

## State Management

### App State
- **Global State**: File uploads, processed chunks, chat history
- **Local State**: Form inputs, UI interactions
- **API State**: Loading states, error handling

### Custom Hooks
- **useAppState**: Global state management
- **useApi**: API integration and error handling

## Features in Detail

### File Upload
- **Drag & Drop**: Intuitive file selection
- **File Validation**: Type and size checking
- **Progress Tracking**: Upload status feedback
- **File Management**: View and remove uploaded files

### Database Connection
- **URL Validation**: Format checking for database URLs
- **Connection Testing**: Verify database connectivity
- **Status Display**: Visual connection status

### Data Ingestion
- **Progress Tracking**: Real-time processing updates
- **Step Visualization**: Clear processing steps
- **Error Handling**: Graceful failure management
- **Completion Feedback**: Success confirmation

### AI Chat
- **Message History**: Persistent chat history
- **Source References**: Document source tracking
- **Export Options**: Download chat history
- **Sample Questions**: Quick start suggestions

## Privacy Features

### Data Protection
- **Local Processing**: No data leaves your machine
- **Privacy Indicator**: Always visible privacy notice
- **Data Control**: Clear and delete options
- **Transparency**: Full source attribution

### Security
- **Input Validation**: Client-side validation
- **Error Sanitization**: Safe error messages
- **HTTPS Ready**: Production security

## Browser Support

- **Chrome** 90+
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

## Development

### Code Style
- **TypeScript**: Strict type checking
- **ESLint**: Code quality enforcement
- **Prettier**: Code formatting
- **Conventional Commits**: Commit message format

### Testing
- **Jest**: Unit testing framework
- **React Testing Library**: Component testing
- **MSW**: API mocking

## Production Build

### Build Process
```bash
npm run build
```

### Output
- **Optimized Bundle**: Minified and compressed
- **Asset Optimization**: Images and fonts
- **Code Splitting**: Lazy loading
- **Service Worker**: Offline support

### Deployment
- **Static Hosting**: Netlify, Vercel, GitHub Pages
- **CDN**: Global content delivery
- **HTTPS**: Secure connections

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 3000
   netstat -ano | findstr :3000
   taskkill /PID <PID> /F
   ```

2. **Module Not Found**
   ```bash
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **API Connection Issues**
   - Check if backend is running on port 8000
   - Verify CORS settings
   - Check network connectivity

### Debug Mode
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide
