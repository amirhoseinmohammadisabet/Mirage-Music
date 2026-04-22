let tracks = [];
let currentIndex = -1;
let currentVibe = "Manual Selection";
let currentStressScore = 0;
let trackStartTime = 0;

const player = document.getElementById('audio-player');
const playPauseBtn = document.getElementById('play-pause-btn');
const seekBar = document.getElementById('seek-bar');
const volumeBar = document.getElementById('volume-bar');
const coverImg = document.getElementById('cover-art');

// 1. Initial Load
fetch('/api/tracks')
    .then(response => response.json())
    .then(data => renderTrackList(data));

// 2. Render List Function
function renderTrackList(trackArray) {
    tracks = trackArray;
    const list = document.getElementById('track-list');
    list.innerHTML = ''; 
    trackArray.forEach((track, index) => {
        let li = document.createElement('li');
        li.className = 'track-item';
        li.id = `track-${index}`;
        li.innerHTML = `<div class="track-title">${track.title}</div><div class="track-artist">${track.artist} &bull; ${track.album}</div>`;
        li.onclick = () => loadAndPlay(index);
        list.appendChild(li);
    });
}

// 3. Playback Logic
function loadAndPlay(index) {
    if (index < 0 || index >= tracks.length) return;
    
    if (currentIndex !== -1 && document.getElementById(`track-${currentIndex}`)) {
        document.getElementById(`track-${currentIndex}`).classList.remove('active');
    }
    
    currentIndex = index;
    const track = tracks[currentIndex];
    trackStartTime = Date.now(); 
    
    if (document.getElementById(`track-${currentIndex}`)) {
        document.getElementById(`track-${currentIndex}`).classList.add('active');
        // Auto-scroll the library list to the active track
        document.getElementById(`track-${currentIndex}`).scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    document.getElementById('now-playing-title').innerText = track.title;
    document.getElementById('now-playing-artist').innerText = track.artist;
    
    coverImg.style.display = 'block'; 
    coverImg.src = `/cover/${track.id}`;
    seekBar.disabled = false;
    
    player.src = `/play/${track.id}`;
    player.play();
    playPauseBtn.innerText = "⏸";
}

function togglePlay() {
    if (currentIndex === -1) return;
    if (player.paused) { player.play(); playPauseBtn.innerText = "⏸"; } 
    else { player.pause(); playPauseBtn.innerText = "▶"; }
}

// 4. Telemetry Logging
function logTrackData() {
    if (currentIndex === -1) return;
    const timeListened = player.currentTime;
    
    fetch('/api/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            track_id: tracks[currentIndex].id,
            vibe_name: currentVibe,
            stress_score: currentStressScore,
            duration_listened: timeListened
        })
    });
}

function playNext() { logTrackData(); loadAndPlay(currentIndex + 1); }
function playPrevious() { logTrackData(); loadAndPlay(currentIndex - 1); }
player.onended = () => playNext();

// 5. Dashboard UI Toggles
function switchTab(tabName) {
    document.getElementById('tab-mood').classList.remove('active');
    document.getElementById('tab-time').classList.remove('active');
    document.getElementById('grid-mood').style.display = 'none';
    document.getElementById('grid-time').style.display = 'none';
    
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.getElementById(`grid-${tabName}`).style.display = 'grid';
}

// 6. Clinical Queue & EMA Modal Logic
let pendingQueueType = '';
let pendingQueueName = '';

function triggerQueue(type, name) {
    pendingQueueType = type;
    pendingQueueName = name;
    document.getElementById('ema-modal').style.display = 'flex';
}

document.getElementById('submit-mood-btn').onclick = () => {
    currentStressScore = document.getElementById('stress-slider').value;
    document.getElementById('ema-modal').style.display = 'none';
    
    fetch(`/api/queue/${pendingQueueType}/${pendingQueueName}`)
        .then(response => response.json())
        .then(data => {
            currentVibe = data.vibe;
            document.getElementById('vibe-text').innerText = `TARGET PROFILE: ${currentVibe.toUpperCase()}`;
            renderTrackList(data.tracks);
            loadAndPlay(0);
        });
};

// 7. Player Controls & Search Update
player.ontimeupdate = () => {
    seekBar.max = player.duration || 0;
    seekBar.value = player.currentTime || 0;
    document.getElementById('current-time').innerText = formatTime(player.currentTime);
    document.getElementById('duration').innerText = formatTime(player.duration);
};

seekBar.oninput = () => { player.currentTime = seekBar.value; };
volumeBar.oninput = () => { player.volume = volumeBar.value; };

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return "0:00";
    let min = Math.floor(seconds / 60);
    let sec = Math.floor(seconds % 60);
    return `${min}:${sec < 10 ? '0' : ''}${sec}`;
}

document.getElementById('search-input').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const trackItems = document.querySelectorAll('.track-item');
    trackItems.forEach(item => {
        if (item.innerText.toLowerCase().includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});