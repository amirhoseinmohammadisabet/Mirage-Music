import sqlite3

print("Connecting to database...")
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

print("Clearing fake acoustic data...")
# This does the exact same thing that the terminal command was trying to do
cursor.execute("UPDATE tracks SET energy = NULL, brightness = NULL, bpm = NULL;")

conn.commit()
conn.close()
print("✅ Data cleared successfully! Your database is ready for real DSP analysis.")