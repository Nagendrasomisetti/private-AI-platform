# PrivAI Desktop Application

A cross-platform desktop application for PrivAI, built with Electron. This application provides a native desktop experience for the privacy-first AI application for education.

## Features

### 🖥️ **Desktop Integration**
- **Native Look & Feel**: Platform-specific UI components
- **System Integration**: File associations, notifications, and shortcuts
- **Auto-Updater**: Automatic updates with user notification
- **Cross-Platform**: Windows, macOS, and Linux support

### 🔒 **Privacy-First Design**
- **Local Processing**: All data stays on your machine
- **No Cloud Calls**: Complete privacy protection
- **Secure Communication**: Encrypted IPC between processes
- **Data Control**: Full control over your data

### ⚡ **Performance**
- **Fast Startup**: Optimized application launch
- **Memory Efficient**: Minimal resource usage
- **Background Processing**: Efficient backend management
- **Responsive UI**: Smooth user interface

## Quick Start

### Prerequisites
- **Node.js** 16+ 
- **Python** 3.8+
- **npm** 8+

### Development Setup

1. **Install Dependencies**
   ```bash
   cd electron-app
   npm install
   ```

2. **Start Development Environment**
   ```bash
   npm run dev
   ```

3. **Build Application**
   ```bash
   npm run build
   ```

4. **Create Distribution Packages**
   ```bash
   npm run dist
   ```

## Project Structure

```
electron-app/
├── src/
│   ├── main.js              # Main Electron process
│   └── preload.js           # Preload script for security
├── scripts/
│   ├── build.js             # Build script
│   ├── dev.js               # Development script
│   └── package.js           # Packaging script
├── assets/
│   ├── icon.ico             # Windows icon
│   ├── icon.icns            # macOS icon
│   ├── icon.png             # Linux icon
│   ├── entitlements.mac.plist # macOS entitlements
│   └── dmg-background.png   # DMG background
├── build/                   # Build output
├── dist/                    # Distribution packages
├── package.json             # Dependencies and scripts
└── README.md               # This file
```

## Scripts

### Development
- `npm start` - Start Electron app
- `npm run dev` - Start development environment (backend + frontend + electron)
- `npm run start-backend` - Start FastAPI backend
- `npm run start-frontend` - Start React frontend

### Building
- `npm run build` - Build application
- `npm run build-frontend` - Build React frontend
- `npm run build-backend` - Prepare Python backend
- `npm run pack` - Package application

### Distribution
- `npm run dist` - Create distribution packages
- `npm run dist-win` - Create Windows packages
- `npm run dist-mac` - Create macOS packages
- `npm run dist-linux` - Create Linux packages

### Utilities
- `npm run clean` - Clean build directories
- `npm run rebuild` - Rebuild native modules
- `npm test` - Run tests
- `npm run lint` - Run linter

## Platform Support

### Windows
- **Targets**: NSIS Installer, Portable Executable
- **Architectures**: x64, ia32
- **Requirements**: Windows 10+

### macOS
- **Targets**: DMG, ZIP
- **Architectures**: x64, arm64 (Apple Silicon)
- **Requirements**: macOS 10.15+

### Linux
- **Targets**: AppImage, DEB, RPM
- **Architectures**: x64, arm64
- **Requirements**: Ubuntu 18.04+, CentOS 7+

## Architecture

### Main Process (`main.js`)
- **Application Lifecycle**: Startup, shutdown, window management
- **Backend Management**: Start/stop FastAPI backend
- **Auto-Updater**: Handle application updates
- **System Integration**: Menu, notifications, file handling

### Preload Script (`preload.js`)
- **Security Bridge**: Secure communication between processes
- **API Exposure**: Safe API access for renderer
- **Event Handling**: IPC event management

### Renderer Process
- **React Frontend**: User interface
- **Backend Communication**: API calls to FastAPI
- **State Management**: Application state

## Backend Integration

The Electron app automatically manages the FastAPI backend:

1. **Auto-Start**: Backend starts when app launches
2. **Health Monitoring**: Continuous health checks
3. **Error Handling**: Graceful error recovery
4. **Resource Management**: Process lifecycle management

## Auto-Updater

The application includes automatic update functionality:

- **Check for Updates**: Automatic update checking
- **Download Updates**: Background download
- **User Notification**: Update available notifications
- **Install Updates**: User-controlled installation

## Security

### Process Isolation
- **Context Isolation**: Renderer process isolation
- **Node Integration**: Disabled in renderer
- **Preload Script**: Secure API exposure

### Code Signing
- **Windows**: Authenticode signing
- **macOS**: Apple Developer ID signing
- **Linux**: GPG signing

### Permissions
- **File Access**: Limited file system access
- **Network Access**: Controlled network permissions
- **System Access**: Minimal system privileges

## Building from Source

### Windows
```bash
# Install dependencies
npm install

# Build for Windows
npm run dist-win

# Output: dist/PrivAI Desktop Setup 1.0.0.exe
```

### macOS
```bash
# Install dependencies
npm install

# Build for macOS
npm run dist-mac

# Output: dist/PrivAI Desktop-1.0.0.dmg
```

### Linux
```bash
# Install dependencies
npm install

# Build for Linux
npm run dist-linux

# Output: dist/PrivAI Desktop-1.0.0.AppImage
```

## Configuration

### Environment Variables
- `NODE_ENV` - Development/production mode
- `ELECTRON_IS_DEV` - Development flag
- `BACKEND_PORT` - Backend port (default: 8000)
- `FRONTEND_PORT` - Frontend port (default: 3000)

### Build Configuration
- **Electron Builder**: Platform-specific build configs
- **Code Signing**: Platform-specific signing configs
- **Auto-Updater**: Update server configuration

## Troubleshooting

### Common Issues

1. **Backend Won't Start**
   ```bash
   # Check Python installation
   python --version
   
   # Install backend dependencies
   cd ../backend
   pip install -r requirements.txt
   ```

2. **Frontend Build Fails**
   ```bash
   # Install frontend dependencies
   cd ../frontend
   npm install
   
   # Build frontend
   npm run build
   ```

3. **Electron Won't Start**
   ```bash
   # Rebuild native modules
   npm run rebuild
   
   # Clear node_modules
   rm -rf node_modules
   npm install
   ```

### Debug Mode
```bash
# Enable debug logging
NODE_ENV=development npm start
```

## Development

### Adding Features
1. **Main Process**: Add to `src/main.js`
2. **Renderer Process**: Add to React frontend
3. **IPC Communication**: Use preload script

### Testing
```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### Linting
```bash
# Run linter
npm run lint

# Fix linting issues
npm run lint:fix
```

## Distribution

### Creating Releases
1. **Update Version**: Update version in `package.json`
2. **Build Packages**: Run platform-specific build commands
3. **Test Packages**: Test on target platforms
4. **Upload**: Upload to distribution platform

### Code Signing
- **Windows**: Use Windows SDK signtool
- **macOS**: Use Apple Developer certificates
- **Linux**: Use GPG for package signing

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
- Check the troubleshooting guide
- Review the documentation

## Changelog

### Version 1.0.0
- Initial release
- Cross-platform support
- Auto-updater integration
- Backend management
- Security features
