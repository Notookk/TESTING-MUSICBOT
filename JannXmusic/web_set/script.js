document.addEventListener('DOMContentLoaded', () => {
    const audioPlayer = document.getElementById('audio-player');
    const currentTimeElem = document.getElementById('current-time');
    const durationElem = document.getElementById('duration');
    const skipButton = document.getElementById('skip');
    const stopButton = document.getElementById('stop');

    audioPlayer.addEventListener('loadedmetadata', () => {
        durationElem.textContent = formatTime(audioPlayer.duration);
    });

    audioPlayer.addEventListener('timeupdate', () => {
        currentTimeElem.textContent = formatTime(audioPlayer.currentTime);
    });

    skipButton.addEventListener('click', () => {
        // Logic to skip to next track (could be implemented here)
        alert('Skip functionality not implemented');
    });

    stopButton.addEventListener('click', () => {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
    });

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    }
});
