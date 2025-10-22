# Shinobi Clone - Video Surveillance NVR System

A modern, open-source video surveillance and Network Video Recorder (NVR) system built with Python (FastAPI) and React. Inspired by Shinobi CCTV, this system provides comprehensive camera management, live streaming, recording, and motion detection capabilities.

## Features

### Core Features
- **Multi-Camera Support**: Manage and monitor multiple IP cameras simultaneously
- **Live Streaming**: Real-time HLS (HTTP Live Streaming) video playback
- **Video Recording**: Continuous, motion-triggered, and scheduled recording modes
- **Motion Detection**: Built-in motion detection with configurable sensitivity and regions
- **PTZ Control**: Full Pan-Tilt-Zoom control for ONVIF cameras with preset management
- **User Management**: Multi-user support with authentication and authorization
- **RESTful API**: Comprehensive API for all operations
- **WebSocket Support**: Real-time event notifications
- **Recording Playback**: Browse and download recorded footage
- **Camera Management**: Full CRUD operations for camera configuration

### Technical Features
- **Protocol Support**: RTSP, HTTP, and ONVIF camera protocols
- **PTZ Support**: ONVIF-based PTZ control with continuous, absolute, and relative movement
- **Video Codecs**: H.264, H.265, and MJPEG support
- **FFmpeg Integration**: Powerful video processing and transcoding
- **PostgreSQL Database**: Robust data storage
- **Redis Caching**: Fast data access and session management
- **Docker Support**: Easy deployment with Docker Compose

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **FFmpeg**: Video processing
- **OpenCV**: Motion detection
- **ONVIF**: PTZ camera control
- **JWT**: Authentication

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **HLS.js**: Video streaming player
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **React Query**: Data fetching and caching

## Prerequisites

- Docker and Docker Compose (recommended)
- OR
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+
  - FFmpeg

## Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd dummy-shinobi-python
```

2. **Configure environment variables**
```bash
# Optional: Create .env file for custom configuration
echo "SECRET_KEY=your-super-secret-key-change-in-production" > .env
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

5. **Create your first user**
- Navigate to http://localhost:3000/register
- Register a new account
- Login and start adding cameras

## Manual Setup

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python init_db.py
```

6. **Run the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run development server**
```bash
npm run dev
```

4. **Access the application**
Open http://localhost:3000 in your browser

## Configuration

### Backend Configuration

Edit `backend/.env` file:

```env
DATABASE_URL=postgresql://shinobi:shinobi@localhost:5432/shinobi
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
RECORDINGS_PATH=/var/shinobi/recordings
STREAM_PATH=/var/shinobi/streams
```

### Camera Configuration

When adding a camera, provide:
- **Name**: Friendly name for the camera
- **Stream URL**: RTSP/HTTP URL (e.g., `rtsp://192.168.1.100:554/stream`)
- **Protocol**: rtsp, http, or onvif
- **Username/Password**: Camera credentials (if required)
- **Resolution**: Video resolution (1080p, 720p, 480p)
- **FPS**: Frames per second
- **Recording Mode**: Continuous, Motion, Scheduled, or Disabled
- **Motion Detection**: Enable/disable with sensitivity settings

## API Documentation

### Authentication

**Register**
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "full_name": "Full Name"
}
```

**Login**
```bash
POST /api/auth/login
Form data: username, password
Returns: { "access_token": "...", "token_type": "bearer" }
```

### Camera Management

**List Cameras**
```bash
GET /api/cameras
Headers: Authorization: Bearer <token>
```

**Create Camera**
```bash
POST /api/cameras
Headers: Authorization: Bearer <token>
{
  "name": "Front Door",
  "stream_url": "rtsp://192.168.1.100:554/stream",
  "protocol": "rtsp",
  "username": "admin",
  "password": "password"
}
```

**Update Camera**
```bash
PUT /api/cameras/{id}
Headers: Authorization: Bearer <token>
```

**Delete Camera**
```bash
DELETE /api/cameras/{id}
Headers: Authorization: Bearer <token>
```

### Streaming

**Start Stream**
```bash
POST /api/stream/{camera_id}/start
Headers: Authorization: Bearer <token>
```

**Stop Stream**
```bash
POST /api/stream/{camera_id}/stop
Headers: Authorization: Bearer <token>
```

### Recording

**Start Recording**
```bash
POST /api/recordings/{camera_id}/start
Headers: Authorization: Bearer <token>
Params: recording_type (manual, continuous, motion), duration (optional)
```

**Stop Recording**
```bash
POST /api/recordings/{recording_id}/stop
Headers: Authorization: Bearer <token>
```

**List Recordings**
```bash
GET /api/recordings/camera/{camera_id}
Headers: Authorization: Bearer <token>
```

**Download Recording**
```bash
GET /api/recordings/{recording_id}/download
Headers: Authorization: Bearer <token>
```

### PTZ Control

**Continuous Move**
```bash
POST /api/ptz/{camera_id}/continuous-move
Headers: Authorization: Bearer <token>
{
  "pan": 0.5,      # -1.0 to 1.0 (left to right)
  "tilt": 0.5,     # -1.0 to 1.0 (down to up)
  "zoom": 0.0,     # -1.0 to 1.0 (out to in)
  "timeout": 1     # seconds
}
```

**Absolute Move**
```bash
POST /api/ptz/{camera_id}/absolute-move
Headers: Authorization: Bearer <token>
{
  "pan": 0.0,      # -1.0 to 1.0 (absolute position)
  "tilt": 0.0,     # -1.0 to 1.0 (absolute position)
  "zoom": 0.5      # 0.0 to 1.0 (absolute zoom level)
}
```

**Relative Move**
```bash
POST /api/ptz/{camera_id}/relative-move
Headers: Authorization: Bearer <token>
{
  "pan": 0.1,      # -1.0 to 1.0 (relative translation)
  "tilt": 0.1,     # -1.0 to 1.0 (relative translation)
  "zoom": 0.1      # -1.0 to 1.0 (relative zoom change)
}
```

**Stop Movement**
```bash
POST /api/ptz/{camera_id}/stop
Headers: Authorization: Bearer <token>
```

**Get Presets**
```bash
GET /api/ptz/{camera_id}/presets
Headers: Authorization: Bearer <token>
```

**Go to Preset**
```bash
POST /api/ptz/{camera_id}/goto-preset
Headers: Authorization: Bearer <token>
{
  "preset_token": "preset_1"
}
```

**Set Preset**
```bash
POST /api/ptz/{camera_id}/set-preset
Headers: Authorization: Bearer <token>
{
  "name": "Main Entrance"
}
```

**Remove Preset**
```bash
DELETE /api/ptz/{camera_id}/presets/{preset_token}
Headers: Authorization: Bearer <token>
```

**Go to Home Position**
```bash
POST /api/ptz/{camera_id}/home
Headers: Authorization: Bearer <token>
```

**Set Home Position**
```bash
POST /api/ptz/{camera_id}/set-home
Headers: Authorization: Bearer <token>
```

## Project Structure

```
dummy-shinobi-python/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── utils/        # Utilities (security, ffmpeg)
│   │   ├── config.py     # Configuration
│   │   ├── database.py   # Database setup
│   │   └── main.py       # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # React contexts
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   ├── App.tsx       # Main app component
│   │   └── main.tsx      # Entry point
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Testing

### Test with Demo Camera

You can test with a public RTSP stream:
```
rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
```

## Troubleshooting

### Camera Won't Connect
- Verify the stream URL is correct
- Check camera is accessible on the network
- Ensure credentials are correct
- Test stream with VLC or ffplay first

### Stream Not Playing
- Check FFmpeg is installed and accessible
- Verify stream URL format
- Check browser console for errors
- Ensure HLS.js is loading correctly

### Recording Issues
- Verify recordings path exists and is writable
- Check disk space
- Ensure FFmpeg has proper permissions
- Check backend logs for errors

## Performance Optimization

- **Recording Storage**: Configure `max_recording_days` to manage disk space
- **Stream Quality**: Adjust `recording_quality` (0-100) to balance quality vs storage
- **Motion Detection**: Tune `motion_sensitivity` to reduce false positives
- **Database**: Regular cleanup of old events and recordings
- **Redis**: Use for session caching to improve performance

## Security Considerations

1. **Change Default Secrets**: Update `SECRET_KEY` in production
2. **Use HTTPS**: Configure reverse proxy (nginx/traefik) with SSL
3. **Secure Cameras**: Use strong passwords for camera credentials
4. **Network Isolation**: Place cameras on isolated VLAN
5. **Regular Updates**: Keep dependencies up to date
6. **Access Control**: Use strong passwords and limit user access

## License

This project is open source and available for personal and educational use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the issue tracker.

## Acknowledgments

Inspired by [Shinobi CCTV](https://shinobi.video/) - An amazing open-source CCTV solution.
