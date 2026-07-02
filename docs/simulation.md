# Simulation logic

The engine resolves active service IDs using `calendar.txt` and `calendar_dates.txt`, filters trips by selected modes and finds active stop-time segments for the requested simulation time. Vehicle position is interpolated between consecutive stops. It computes heading, speed, next stop, distance travelled in the current segment and progress.
