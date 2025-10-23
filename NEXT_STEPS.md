# Next Steps - Remaining Features

## ✅ COMPLETED

### 1. Multi-Camera Grid View with Drag-and-Drop
- **Status:** ✅ DONE
- **Location:** `/grid` route
- **Features:**
  - Draggable and resizable camera tiles
  - Auto-starts all camera streams
  - Saves layout to localStorage
  - Quick access to camera settings
  - List/Grid toggle in navigation

**To Use:**
1. Pull latest changes: `git pull`
2. Rebuild frontend: `docker-compose down && docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d --build`
3. Go to http://localhost:3000
4. Click "Grid" in the navigation
5. Drag cameras to rearrange, resize by dragging corners

---

## 🚧 TODO: Fix Recording Functionality

### Current Issue
Recording endpoints exist but may not be working correctly. Need to verify:

1. **Check if FFmpeg recording process starts**
2. **Verify files are being created**
3. **Ensure proper file permissions**

### Implementation Steps

#### Step 1: Test Recording Manually
```bash
# Check if backend can access camera stream
docker-compose exec backend ffmpeg -i rtsp://rtsp-server:8554/myvideo -t 10 /tmp/test.mp4

# If that works, the stream is accessible
```

#### Step 2: Check Recording Service
The recording service is in `backend/app/services/recording_service.py`. It should:
- Start FFmpeg process to record stream
- Save to `/var/shinobi/recordings/{camera_id}/`
- Generate thumbnails after recording

#### Step 3: Verify Directory Permissions
```bash
docker-compose exec backend ls -la /var/shinobi/recordings/
docker-compose exec backend mkdir -p /var/shinobi/recordings/test
docker-compose exec backend touch /var/shinobi/recordings/test/test.txt
```

#### Step 4: Add Debug Logging
In `backend/app/services/recording_service.py`, add logging:
```python
import logging
logger = logging.getLogger(__name__)

# In start_recording method:
logger.info(f"Starting recording for camera {camera.id}")
logger.info(f"FFmpeg command: {' '.join(cmd)}")
logger.info(f"Output path: {file_path}")
```

#### Step 5: Test from Frontend
1. Go to camera detail page
2. Click "Start Recording"
3. Check backend logs: `docker-compose logs backend -f`
4. Look for FFmpeg output and any errors

### Common Issues & Fixes

**Issue 1: Permission Denied**
```bash
# Fix permissions
docker-compose exec backend chmod -R 755 /var/shinobi/recordings
```

**Issue 2: FFmpeg Not Finding Stream**
- Ensure camera stream URL is correct
- Test with: `docker-compose exec backend ffplay rtsp://rtsp-server:8554/myvideo`

**Issue 3: Files Not Appearing**
- Check if FFmpeg process is actually running
- Look for FFmpeg errors in backend logs

---

## 🚧 TODO: Motion Detection with Auto-Recording

### Current State
- Motion detection service EXISTS in `backend/app/services/motion_detection.py`
- UI controls for motion detection exist in camera form
- **BUT:** Motion detection is NOT integrated with recording system

### What Needs to Be Done

#### 1. Create Motion Detection Background Task

Add to `backend/app/services/motion_detection.py`:

```python
from app.services.recording_service import RecordingService
from app.models.event import Event, EventType
from app.database import SessionLocal

def motion_detected_callback(camera_id: int, detected_regions: list):
    """Callback when motion is detected - starts recording"""
    db = SessionLocal()
    try:
        # Get camera
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera or not camera.motion_detection_enabled:
            return

        # Check if already recording
        active_recordings = [r for r in RecordingService.active_recordings.keys()]
        camera_recordings = [r for r in active_recordings
                           if db.query(Recording).filter(Recording.id == r).first().camera_id == camera_id]

        if not camera_recordings:
            # Start recording
            recording = RecordingService.start_recording(
                db, camera, RecordingType.MOTION, duration=60  # 60 second clips
            )

            # Log event
            event = Event(
                camera_id=camera_id,
                recording_id=recording.id,
                user_id=camera.owner_id,
                event_type=EventType.MOTION_DETECTED,
                title="Motion Detected",
                description=f"Motion detected in {len(detected_regions)} regions",
                event_data={"regions": detected_regions}
            )
            db.add(event)
            db.commit()

            print(f"Motion detected on camera {camera_id}, started recording {recording.id}")
    finally:
        db.close()
```

#### 2. Start Motion Detection When Camera Is Added

Add to `backend/app/api/cameras.py`:

```python
from app.services.motion_detection import MotionDetectionService, motion_detected_callback

@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_camera = CameraService.create_camera(db, camera, current_user)

    # Start motion detection if enabled
    if db_camera.motion_detection_enabled:
        MotionDetectionService.start_detection(
            db_camera.id,
            db_camera.stream_url,
            db_camera.motion_sensitivity,
            callback=lambda cam_id, regions: motion_detected_callback(cam_id, regions),
            regions=db_camera.motion_regions
        )

    return db_camera
```

#### 3. Add Motion Detection Toggle API Endpoint

Add to `backend/app/api/cameras.py`:

```python
@router.post("/{camera_id}/motion-detection/toggle")
def toggle_motion_detection(
    camera_id: int,
    enabled: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle motion detection on/off for a camera."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    camera.motion_detection_enabled = enabled
    db.commit()

    if enabled:
        # Start detection
        MotionDetectionService.start_detection(
            camera.id,
            camera.stream_url,
            camera.motion_sensitivity,
            callback=lambda cam_id, regions: motion_detected_callback(cam_id, regions),
            regions=camera.motion_regions
        )
    else:
        # Stop detection
        MotionDetectionService.stop_detection(camera.id)

    return {"message": f"Motion detection {'enabled' if enabled else 'disabled'}"}
```

#### 4. Add Motion Detection Toggle to Frontend

In `frontend/src/pages/CameraDetail.tsx`, add a toggle button:

```tsx
const [motionDetectionEnabled, setMotionDetectionEnabled] = useState(camera?.motion_detection_enabled || false);

const handleToggleMotionDetection = async () => {
  if (!camera) return;

  try {
    await apiClient.toggleMotionDetection(camera.id, !motionDetectionEnabled);
    setMotionDetectionEnabled(!motionDetectionEnabled);
    toast.success(`Motion detection ${!motionDetectionEnabled ? 'enabled' : 'disabled'}`);
  } catch (error) {
    toast.error('Failed to toggle motion detection');
  }
};

// In the UI:
<button
  onClick={handleToggleMotionDetection}
  className={`px-4 py-2 rounded-lg ${
    motionDetectionEnabled
      ? 'bg-green-600 hover:bg-green-700'
      : 'bg-gray-700 hover:bg-gray-600'
  } text-white`}
>
  {motionDetectionEnabled ? '🟢 Motion Detection ON' : '⚫ Motion Detection OFF'}
</button>
```

#### 5. Add API Method to Frontend

In `frontend/src/services/api.ts`:

```typescript
async toggleMotionDetection(cameraId: number, enabled: boolean): Promise<void> {
  await this.client.post(`/api/cameras/${cameraId}/motion-detection/toggle`, null, {
    params: { enabled }
  });
}
```

#### 6. Show Motion Events in UI

Create a motion events panel in camera detail page:

```tsx
const [motionEvents, setMotionEvents] = useState<Event[]>([]);

useEffect(() => {
  const loadMotionEvents = async () => {
    const events = await apiClient.getEvents(camera.id, EventType.MOTION_DETECTED);
    setMotionEvents(events.slice(0, 10)); // Last 10 events
  };
  loadMotionEvents();
}, [camera?.id]);

// Display in UI:
<div className="mt-4">
  <h3 className="text-lg font-semibold text-white mb-2">Recent Motion Events</h3>
  {motionEvents.map(event => (
    <div key={event.id} className="p-2 bg-gray-700 rounded mb-2">
      <div className="text-sm text-white">{event.title}</div>
      <div className="text-xs text-gray-400">{format(new Date(event.created_at), 'PPpp')}</div>
    </div>
  ))}
</div>
```

---

## Testing Checklist

### Recording Test
- [ ] Add camera with stream
- [ ] Click "Start Recording"
- [ ] Wait 30 seconds
- [ ] Stop recording
- [ ] Check if recording appears in "Recordings" tab
- [ ] Verify recording can be downloaded
- [ ] Check thumbnail is generated

### Motion Detection Test
- [ ] Enable motion detection on camera
- [ ] Move something in front of camera
- [ ] Verify recording starts automatically
- [ ] Check motion event is logged
- [ ] Verify recording stops after duration
- [ ] Test toggle on/off works

### Grid View Test
- [ ] Add multiple cameras (3-4)
- [ ] Go to Grid view
- [ ] Verify all streams load
- [ ] Drag cameras to rearrange
- [ ] Resize camera tiles
- [ ] Refresh page - layout should persist

---

## Quick Commands

### Rebuild after changes:
```bash
docker-compose -f docker-compose.yml -f docker-compose.test.yml down
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
```

### Check logs:
```bash
docker-compose logs backend -f
docker-compose logs frontend -f
```

### Test FFmpeg:
```bash
docker-compose exec backend ffmpeg -version
docker-compose exec backend ffprobe -i rtsp://rtsp-server:8554/myvideo
```

### Check recordings directory:
```bash
docker-compose exec backend ls -la /var/shinobi/recordings/
```

---

## Summary

**✅ DONE:**
- Multi-camera grid view with drag-and-drop

**🚧 TODO:**
1. Debug and fix recording functionality
2. Integrate motion detection with auto-recording
3. Add motion detection toggle in UI
4. Add motion events display

The backend code for motion detection ALREADY EXISTS - it just needs to be integrated with the recording system and exposed via API endpoints!
