// Game data
const gameData = [
    {
        questionText: "Hewan berkaki empat dan mengeong",
        questionImage: "images/cukurukuk.jpg",
        correctAnswer: "Kucing",
        options: [
            { image: "images/cukurukuk.jpg", text: "Kucing" },
            { image: "images/kecwa ringan.jpg", text: "Elang" },
            { image: "images/ksabar.jpg", text: "Landak" }
        ]
    },
    {
        questionText: "Hewan yang sering disantap oleh warga negara barat",
        questionImage: "images/icikiwir.jpg",
        correctAnswer: "Babi",
        options: [
            { image: "images/icikiwir.jpg", text: "Babi" },
            { image: "images/sucipto.jpg", text: "Hiu" },
            { image: "images/uhahaha.jpg", text: "Kodok" }
        ]
    },
    {
        questionText: "Hewan apa yang dikenal sebagai sahabat manusia?",
        questionImage: "images/let me know.jpg",
        correctAnswer: "Anjing",
        options: [
            { image: "images/cukurukuk.jpg", text: "Kucing" },
            { image: "images/masbro.jpg", text: "Kapibara" },
            { image: "images/let me know.jpg", text: "Anjing" }
        ]
    },
    {
        questionText: "Hewan yang hidup di iklim dingin",
        questionImage: "images/can we get much higher.jpg",
        correctAnswer: "Rusa kutub",
        options: [
            { image: "images/jikaaa.jpg", text: "Serigala" },
            { image: "images/ksabar.jpg", text: "Landak" },
            { image: "images/can we get much higher.jpg", text: "Rusa kutub" }
        ]
    },
    {
        questionText: "Hewan yang melambangkan kesendirian?",
        questionImage: "images/jikaaa.jpg",
        correctAnswer: "Serigala",
        options: [
            { image: "images/kecwa ringan.jpg", text: "Elang" },
            { image: "images/jikaaa.jpg", text: "Serigala" },
            { image: "images/let me know.jpg", text: "Anjing" }
        ]
    },
    {
        questionText: "Hewan terbang",
        questionImage: "images/kecwa ringan.jpg",
        correctAnswer: "Elang",
        options: [
            { image: "images/sucipto.jpg", text: "Hiu" },
            { image: "images/kecwa ringan.jpg", text: "Elang" },
            { image: "images/uhahaha.jpg", text: "Kodok" }
        ]
    },
    {
        questionText: "Hewan lucu berduri",
        questionImage: "images/ksabar.jpg",
        correctAnswer: "Landak",
        options: [
            { image: "images/masbro.jpg", text: "Kapibara" },
            { image: "images/sucipto.jpg", text: "Hiu" },
            { image: "images/ksabar.jpg", text: "Landak" }
        ]
    },
    {
        questionText: "Hewan imut santuy",
        questionImage: "images/masbro.jpg",
        correctAnswer: "Kapibara",
        options: [
            { image: "images/cukurukuk.jpg", text: "Kucing" },
            { image: "images/masbro.jpg", text: "Kapibara" },
            { image: "images/let me know.jpg", text: "Anjing" }
        ]
    },
    {
        questionText: "Predator laut",
        questionImage: "images/sucipto.jpg",
        correctAnswer: "Hiu",
        options: [
            { image: "images/sucipto.jpg", text: "Hiu" },
            { image: "images/jikaaa.jpg", text: "Serigala" },
            { image: "images/kecwa ringan.jpg", text: "Elang" }
        ]
    },
    {
        questionText: "Hewan yang muncul saat hujan",
        questionImage: "images/uhahaha.jpg",
        correctAnswer: "Kodok",
        options: [
            { image: "images/sucipto.jpg", text: "Hiu" },
            { image: "images/uhahaha.jpg", text: "Kodok" },
            { image: "images/ksabar.jpg", text: "Landak" }
        ]
    }
];

// Game variables
let score = 0;
let totalTime = 90;
let timerInterval;
let currentQuestion = {};
let canAnswer = true;
let isMuted = false;
let isVoiceMode = false;
let isRecording = false;

// DOM elements
const titleScreen = document.getElementById('title-screen');
const gameContainer = document.getElementById('game-container');
const gameOverScreen = document.getElementById('game-over');
const startBtn = document.getElementById('start-btn');
const restartBtn = document.getElementById('restart-btn');
const scoreElement = document.getElementById('score');
const finalScoreElement = document.getElementById('final-score');
const timerElement = document.getElementById('timer');
const questionText = document.getElementById('question-text');
const questionImage = document.getElementById('question-image');
const messageElement = document.getElementById('message');
const optionsContainer = document.getElementById('options-container');
const muteBtn = document.getElementById('mute-btn');
const gameMuteBtn = document.getElementById('game-mute-btn');
const clickModeBtn = document.getElementById('click-mode');
const voiceModeBtn = document.getElementById('voice-mode');
const voiceInstruction = document.getElementById('voice-instruction');

// Audio elements
const bgm = document.getElementById('bgm');
const correctSound = document.getElementById('correct-sfx');
const wrongSound = document.getElementById('wrong-sfx');
const clickSound = document.getElementById('click-sfx');
const timeupSound = document.getElementById('timeup-sfx');

// Format time from seconds to MM:SS
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// Play sound function
function playSound(sound) {
    if (isMuted) return;
    sound.currentTime = 0;
    sound.play().catch(e => console.log("Audio error:", e));
}

// Toggle mute function
function toggleMute() {
    isMuted = !isMuted;
    const icon = isMuted ? "🔇" : "🔊";
    muteBtn.textContent = icon;
    gameMuteBtn.textContent = icon;
    [bgm, correctSound, wrongSound, clickSound, timeupSound].forEach(sound => {
        sound.muted = isMuted;
    });
}

// Toggle game mode
function toggleMode(mode) {
    isVoiceMode = mode === 'voice';
    
    clickModeBtn.classList.toggle('active', !isVoiceMode);
    voiceModeBtn.classList.toggle('active', isVoiceMode);
    
    if (isVoiceMode) {
        initSpeechRecognition();
    } else {
        voiceInstruction.style.display = 'none';
    }
    
    // Refresh current question display
    if (gameContainer.style.display === 'block') {
        loadRandomQuestion();
    }
}

// Initialize speech recognition
async function initSpeechRecognition() {
    try {
        // Add record button if it doesn't exist
        if (!document.getElementById('record-btn')) {
            const recordBtn = document.createElement('button');
            recordBtn.id = 'record-btn';
            recordBtn.className = 'game-btn';
            recordBtn.textContent = '🎤 Record (5s)';
            recordBtn.onclick = handleRecording;
            gameContainer.appendChild(recordBtn);
        }
        
        voiceInstruction.style.display = 'block';
    } catch (error) {
        console.error("Error initializing speech:", error);
        isVoiceMode = false;
        clickModeBtn.classList.add('active');
        voiceModeBtn.classList.remove('active');
        voiceInstruction.style.display = 'none';
        alert("Mode suara tidak tersedia. Kembali ke mode klik.");
    }
}

// Handle recording
async function handleRecording() {
    if (isRecording || !canAnswer) return;
    
    const recordBtn = document.getElementById('record-btn');
    try {
        isRecording = true;
        recordBtn.disabled = true;
        recordBtn.textContent = '🎤 Recording...';

        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                sampleSize: 16,
                volume: 1.0
            } 
        });
        const mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm'
        });
        const audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };        mediaRecorder.onstop = async () => {
            try {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const wavBlob = await AudioConverter.blobToWav(audioBlob);
                await sendAudioToServer(wavBlob);
            } catch (error) {
                console.error('Error processing audio:', error);
                messageElement.textContent = 'Error processing audio. Please try again.';
                messageElement.style.color = '#f44336';
            } finally {
                stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                recordBtn.disabled = false;
                recordBtn.textContent = '🎤 Record (5s)';
            }
        };

        mediaRecorder.start();

        // Stop recording after 5 seconds
        setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }, 5000);

    } catch (error) {
        console.error('Error recording:', error);
        isRecording = false;
        recordBtn.disabled = false;
        recordBtn.textContent = '🎤 Record (5s)';
    }
}

// Send audio to server
async function sendAudioToServer(blob) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    try {
        // Update UI to show processing
        messageElement.textContent = '🎤 Memulai proses suara...';
        messageElement.style.color = '#3498db';
        
        const formData = new FormData();        formData.append('file', blob, `recording_${timestamp}.wav`);
        
        messageElement.textContent = '🔍 Menganalisis suara...';
        const response = await fetch('http://localhost:8000/api/speech', {
            method: 'POST',
            body: formData
        });const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error?.message || 'Terjadi kesalahan jaringan');
        }

        if (result.success && result.data?.text) {
            messageElement.textContent = '✅ Suara terdeteksi!';
            messageElement.style.color = '#2ecc71';
            handleSpeechResult(result.data.text);
            
            // Show confidence if available
            if (result.data.confidence < 0.8) {
                messageElement.textContent += ' (Mohon bicara lebih jelas)';
            }
            return;
        }
        
        throw new Error('Format respons tidak valid');    } catch (error) {
        console.error('Error sending audio:', error);
        messageElement.textContent = '❌ Error: ' + error.message;
        messageElement.style.color = '#f44336';
    } finally {
        // Re-enable answering after processing is complete
        canAnswer = true;
    }
}

// Handle speech result
function handleSpeechResult(text) {
    if (!canAnswer) return;
    
    // Convert text to option (A, B, or C)
    const normalizedText = text.trim().toUpperCase();
    if (['A', 'B', 'C'].includes(normalizedText)) {
        const optionIndex = ['A', 'B', 'C'].indexOf(normalizedText);
        const options = document.querySelectorAll('.option');
        if (options[optionIndex]) {
            checkAnswer(
                options[optionIndex].querySelector('.option-text').textContent === currentQuestion.correctAnswer,
                options[optionIndex]
            );
        }
    }
}

// Start game function
function startGame() {
    playSound(clickSound);
    titleScreen.style.display = 'none';
    gameContainer.style.display = 'block';
    gameOverScreen.style.display = 'none';
    
    score = 0;
    scoreElement.textContent = score;
    totalTime = 60;
    timerElement.textContent = formatTime(totalTime);
    timerElement.classList.remove('pulse');
    
    // Play BGM
    bgm.volume = 0.3;
    playSound(bgm);
    
    startTimer();
    loadRandomQuestion();
}

// Start timer function
function startTimer() {
    clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
        totalTime--;
        timerElement.textContent = formatTime(totalTime);
        
        if (totalTime <= 10) {
            timerElement.classList.add('pulse');
        }
        
        if (totalTime <= 0) {
            clearInterval(timerInterval);
            endGame();
        }
    }, 1000);
}

// Load random question function
function loadRandomQuestion() {
    canAnswer = true;
    
    // Reset message
    messageElement.textContent = '';
    messageElement.style.color = '';
    
    // Get random question
    const randomIndex = Math.floor(Math.random() * gameData.length);
    currentQuestion = gameData[randomIndex];
    
    // Update question
    questionText.textContent = currentQuestion.questionText;
    questionImage.src = currentQuestion.questionImage;
    questionImage.classList.remove('revealed');
    questionImage.style.display = 'none';
    
    // Create options
    createOptions();
}

// Create options function
function createOptions() {
    optionsContainer.innerHTML = '';
    
    // Shuffle options
    const shuffledOptions = [...currentQuestion.options].sort(() => Math.random() - 0.5);
    const optionLabels = ['A', 'B', 'C'];
    
    shuffledOptions.forEach((option, index) => {
        const optionWrapper = document.createElement('div');
        optionWrapper.className = 'option-wrapper';
        
        // Create label (A/B/C)
        const labelElement = document.createElement('div');
        labelElement.className = 'option-label';
        labelElement.textContent = optionLabels[index];
        
        // Create option container
        const optionElement = document.createElement('div');
        optionElement.className = 'option';
        
        // Create option content
        const optionImage = document.createElement('img');
        optionImage.className = 'option-image';
        optionImage.src = option.image;
        optionImage.alt = option.text;
        
        const optionText = document.createElement('div');
        optionText.className = 'option-text';
        optionText.textContent = option.text;
        
        optionElement.appendChild(optionImage);
        optionElement.appendChild(optionText);
        
        // Add click event for click mode
        if (!isVoiceMode) {
            optionElement.addEventListener('click', () => {
                if (canAnswer) {
                    checkAnswer(option.text === currentQuestion.correctAnswer, optionElement);
                }
            });
        }
        
        optionWrapper.appendChild(labelElement);
        optionWrapper.appendChild(optionElement);
        optionsContainer.appendChild(optionWrapper);
    });
    
    // Apply mode-specific styles
    if (isVoiceMode) {
        gameContainer.classList.add('voice-mode');
        voiceInstruction.style.display = 'block';
    } else {
        gameContainer.classList.remove('voice-mode');
        voiceInstruction.style.display = 'none';
    }
}

// Check answer function
function checkAnswer(isCorrect, optionElement) {
    if (!canAnswer) return;
    canAnswer = false;
    
    playSound(clickSound);
    
    // Reveal the selected option's image
    const selectedImage = optionElement.querySelector('.option-image');
    if (selectedImage) {
        selectedImage.classList.add('revealed');
    }
    
    if (isCorrect) {
        playSound(correctSound);
        optionElement.classList.add('correct');
        messageElement.textContent = 'Benar! +10 poin';
        messageElement.style.color = '#4CAF50';
        score += 10;
        scoreElement.textContent = score;
        
        // Reveal question image
        setTimeout(() => {
            questionImage.style.display = 'block';
            questionImage.classList.add('revealed');
        }, 500);
        
        // Next question after delay
        setTimeout(() => {
            if (totalTime > 0) {
                loadRandomQuestion();
            }
        }, 1500);
    } else {
        playSound(wrongSound);
        optionElement.classList.add('wrong');
        messageElement.textContent = 'Salah!';
        messageElement.style.color = '#f44336';
        
        // Reveal correct answer
        const correctAnswer = currentQuestion.correctAnswer;
        const options = document.querySelectorAll('.option');
        options.forEach(opt => {
            if (opt.querySelector('.option-text').textContent === correctAnswer) {
                opt.classList.add('correct');
                const correctImage = opt.querySelector('.option-image');
                if (correctImage) {
                    correctImage.classList.add('revealed');
                }
            }
        });
        
        // Reveal question image
        setTimeout(() => {
            questionImage.style.display = 'block';
            questionImage.classList.add('revealed');
        }, 500);
        
        // Next question after delay
        setTimeout(() => {
            if (totalTime > 0) {
                loadRandomQuestion();
            }
        }, 1500);
    }
}

// End game function
function endGame() {
    playSound(timeupSound);
    bgm.pause();
    
    if (recognizer) {
        recognizer.stopListening();
    }
    
    gameContainer.style.display = 'none';
    gameOverScreen.style.display = 'block';
    finalScoreElement.textContent = score;
}

// Event listeners
startBtn.addEventListener('click', startGame);
restartBtn.addEventListener('click', startGame);
muteBtn.addEventListener('click', toggleMute);
gameMuteBtn.addEventListener('click', toggleMute);
clickModeBtn.addEventListener('click', () => toggleMode('click'));
voiceModeBtn.addEventListener('click', () => toggleMode('voice'));

// Initialize
bgm.volume = 1;
toggleMode('click'); // Default to click mode