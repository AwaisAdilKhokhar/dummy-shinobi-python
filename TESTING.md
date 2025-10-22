# Testing the Shinobi Clone Without Physical Cameras

This guide shows you how to test the video surveillance system without actual IP cameras.

## Quick Start: Use Public Test Streams

### Method 1: Public RTSP Stream (Easiest)

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Access the web interface:**
   - Go to http://localhost:3000
   - Register a new account
   - Login

3. **Add a test camera:**
   - Click "+ Add Camera"
   - Fill in the details:
     - **Name:** `Big Buck Bunny Test`
     - **Stream URL:** `rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4`
     - **Protocol:** `rtsp`
     - **Resolution:** `640x480`
     - **FPS:** `15`
     - Leave username/password empty
   - Click "Add Camera"

4. **View the stream:**
   - Click on the camera card
   - Click "Start Stream" on the live view
   - You should see the Big Buck Bunny video playing!

### Method 2: Local Test RTSP Server

For more control, use the included test setup:

1. **Start the test RTSP server:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
   ```

2. **This will start:**
   - MediaMTX RTSP server on port 8554
   - A test pattern stream generator

3. **Add the test stream in Shinobi:**
   - **Stream URL:** `rtsp://rtsp-server:8554/test`
   - Or from host: `rtsp://localhost:8554/test`

4. **Access MediaMTX Web UI:**
   - Go to http://localhost:8888
   - View available streams

## Alternative Public Test Streams

### RTSP Streams

Try these free RTSP test streams:

1. **Big Buck Bunny (Wowza)**
   ```
   rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
   ```

2. **Sample Video (Low Quality)**
   ```
   rtsp://rtsp.stream/pattern
   ```

### HTTP Streams (MJPEG)

For HTTP protocol cameras:

1. **Test MJPEG Stream**
   ```
   http://webcam.test/mjpeg
   ```

## Testing Features

### 1. Live Streaming
- Add a camera with one of the test streams above
- Go to camera detail page
- Click "Start Stream"
- Video should play in the browser

### 2. Recording
- On the camera detail page
- Click "Start Recording"
- Let it record for 30 seconds
- Click stop (or wait for automatic stop)
- Go to "Recordings" tab
- You should see the recording with a thumbnail
- Click "Download" to get the video file

### 3. Motion Detection
When adding a camera, enable:
- **Motion Detection:** ON
- **Motion Sensitivity:** 50
- **Recording Mode:** Motion

The system will record when motion is detected in the stream.

### 4. PTZ Controls (ONVIF Only)

PTZ controls require an ONVIF-compatible camera. To test without hardware:

**Option 1: ONVIF Camera Emulator**
- Use onvif-camera-emulator: https://github.com/roleoroleo/onvif-camera-emulator

**Option 2: Skip PTZ Testing**
- PTZ controls only appear for cameras with protocol set to "onvif"
- Test other features first with regular RTSP streams

## Using Your Own Video Files

### Step 1: Create a test stream from a video file

```bash
# Using FFmpeg directly
ffmpeg -re -stream_loop -1 -i /path/to/your/video.mp4 \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -c:a aac -f rtsp rtsp://localhost:8554/mystream
```

### Step 2: Or use VLC

1. Open VLC Media Player
2. Media → Stream
3. Add your video file
4. Stream using RTSP protocol
5. Set destination: rtsp://localhost:8554/stream

### Step 3: Add to Shinobi

- Stream URL: `rtsp://localhost:8554/mystream`

## Troubleshooting Test Streams

### Stream Won't Connect

1. **Check stream is accessible:**
   ```bash
   ffplay rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

3. **Verify FFmpeg is installed in backend:**
   ```bash
   docker-compose exec backend ffmpeg -version
   ```

### Stream Plays But Doesn't Record

1. **Check recordings directory permissions:**
   ```bash
   docker-compose exec backend ls -la /var/shinobi/recordings
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

### Stream is Laggy

1. **Lower the resolution** when adding the camera
2. **Reduce FPS** to 10-15
3. **Use a test stream closer to you geographically**

## Production Testing Checklist

Before deploying with real cameras:

- [ ] User registration and login works
- [ ] Can add/edit/delete cameras
- [ ] Live streaming works
- [ ] Recording starts and stops correctly
- [ ] Recordings can be downloaded
- [ ] Motion detection triggers recording
- [ ] Thumbnails are generated
- [ ] Events are logged
- [ ] Multiple cameras work simultaneously
- [ ] Storage cleanup works (old recordings deleted)

## Recommended Test Sequence

1. **Basic Setup (5 minutes)**
   - Register account
   - Add public RTSP test stream
   - View live stream

2. **Recording Test (10 minutes)**
   - Start manual recording
   - Wait 2 minutes
   - Stop recording
   - Verify recording appears
   - Download and play recording

3. **Multi-Camera Test (10 minutes)**
   - Add 3 different test streams
   - View dashboard with all cameras
   - Start streaming on all cameras
   - Verify all streams work

4. **Long-Running Test (Optional)**
   - Let camera record for several hours
   - Check disk usage
   - Verify cleanup of old recordings
   - Check for memory leaks

## Notes

- Public test streams may have variable availability
- Use local test streams for reliable testing
- Test streams don't support PTZ control
- For PTZ testing, you need an ONVIF emulator or real camera

## Need Help?

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify all containers are running: `docker-compose ps`
3. Ensure ports are not blocked by firewall
4. Check the main README.md for troubleshooting section
